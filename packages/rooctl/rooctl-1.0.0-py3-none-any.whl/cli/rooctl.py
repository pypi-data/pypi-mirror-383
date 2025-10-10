#!/usr/bin/env python3
"""
Minimal CLI for Orchestration System
Commands: login, status, run, artifacts list/sign/export, webhooks add/list, public status/artifacts/sign/set-key
"""
import argparse
import json
from pathlib import Path
from rc_orchestration_sdk.client import OrchestrationClient

CONFIG = Path.home() / ".rooctl" / "config.json"


def load_client() -> OrchestrationClient:
    base_url = None
    token = None
    public_api_key = None
    if CONFIG.exists():
        try:
            cfg = json.loads(CONFIG.read_text())
            base_url = cfg.get("base_url")
            token = cfg.get("access_token")
            public_api_key = cfg.get("public_api_key")
        except Exception:
            pass
    return OrchestrationClient(base_url=base_url, access_token=token, api_key=public_api_key)


def save_client(client: OrchestrationClient):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    data = {"base_url": client.base_url, "access_token": client.access_token, "public_api_key": client.api_key}
    CONFIG.write_text(json.dumps(data, indent=2))


def main():
    p = argparse.ArgumentParser(prog="rooctl", description="Orchestration CLI")
  sub = p.add_subparsers(dest="cmd")

    lp = sub.add_parser("login")
    lp.add_argument("username")
    lp.add_argument("password")
    lp.add_argument("--base-url", default="http://localhost:8000/api/v1")

    sub.add_parser("status")

    ap = sub.add_parser("artifacts")
    ap.add_argument("action", choices=["list", "sign", "export", "diff", "history"]) 
    ap.add_argument("--artifact-id")
    ap.add_argument("--left")
    ap.add_argument("--right")
    ap.add_argument("--phase")
    ap.add_argument("--execution-id")
    ap.add_argument("--status-filter")
    ap.add_argument("--zip-name", default="artifacts_export.zip")
    ap.add_argument("--output", help="Output path for diff (default stdout)")

    wp = sub.add_parser("webhooks")
    wp.add_argument("action", choices=["list", "add"]) 
    wp.add_argument("--url")
    wp.add_argument("--secret")
    wp.add_argument("--events", nargs="*", default=["*"])

    rp = sub.add_parser("run")
    rp.add_argument("--phases", nargs="*")
    rp.add_argument("--dry-run", action="store_true")

  pub = sub.add_parser("public")
  pub_sub = pub.add_subparsers(dest="pubcmd")
    pub_status = pub_sub.add_parser("status")
    pub_art = pub_sub.add_parser("artifacts")
    pub_art.add_argument("action", choices=["list", "sign", "download", "signed-url"]) 
    pub_art.add_argument("--artifact-id")
    pub_art.add_argument("--phase")
    pub_art.add_argument("--status-filter")
    pub_art.add_argument("--page", type=int, default=1)
    pub_art.add_argument("--page-size", type=int, default=25)
    pub_art.add_argument("--execution-id")
    pub_art.add_argument("--ttl-seconds", type=int, default=600)
    pub_art.add_argument("--output", help="Output path for download (default <artifact-id>.yaml)")
  pub_key = pub_sub.add_parser("set-key")
  pub_key.add_argument("--api-key", required=True)

  adm = sub.add_parser("admin")
  adm_sub = adm.add_subparsers(dest="admcmd")
  adm_ret = adm_sub.add_parser("retention")
  adm_ret.add_argument("--category", required=True, choices=["audit","webhooks","webhooks_dlq","analytics"])  # noqa: E501
  adm_ret.add_argument("--days", type=int, default=30)
  adm_ret.add_argument("--action", choices=["compact","rotate"], default="compact")

    args = p.parse_args()
    client = load_client()

    if args.cmd == "login":
        client.base_url = args.base_url
        data = client.login(args.username, args.password)
        save_client(client)
        print("Logged in as:", data.get("user", {}).get("username"))
        return 0

    if args.cmd == "status":
        data = client.status()
        print(json.dumps(data, indent=2))
        return 0

    if args.cmd == "artifacts":
        if args.action == "list":
            data = client.list_artifacts(phase=args.phase, execution_id=args.execution_id, status_filter=args.status_filter)
            print(json.dumps(data, indent=2))
        elif args.action == "sign":
            if not args.artifact_id:
                raise SystemExit("--artifact-id required for sign")
            data = client.sign_artifact(args.artifact_id)
            print(json.dumps(data, indent=2))
        elif args.action == "export":
            import zipfile, tempfile, shutil, requests as rq
            data = client.list_artifacts(phase=args.phase, execution_id=args.execution_id, status_filter=args.status_filter)
            arts = data.get('artifacts', [])
            if not arts:
                print('No artifacts to export')
                return 0
            tmpdir = tempfile.mkdtemp(prefix='rooctl_')
            try:
                for a in arts:
                    aid = a['id']
                    url = f"{client.base_url}/artifacts/{aid}/download"
                    r = rq.get(url, headers=client._headers())
                    r.raise_for_status()
                    with open(f"{tmpdir}/{aid}.yaml", 'wb') as f:
                        f.write(r.content)
                zpath = Path.cwd() / args.zip_name
                with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for p in Path(tmpdir).glob('*.yaml'):
                        zf.write(p, arcname=p.name)
                print('Exported to', zpath)
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
        elif args.action == "diff":
            left = args.left or args.artifact_id
            right = args.right
            if not left or not right:
                raise SystemExit("--left and --right (or --artifact-id and --right) required for diff")
            import requests as rq
            r = rq.get(f"{client.base_url}/artifacts/diff", headers=client._headers(), params={"left": left, "right": right})
            if not r.ok:
                print(r.status_code, r.text)
                raise SystemExit(1)
            data = r.json()
            diff_text = data.get('unified_diff') or ''
            if args.output:
                Path(args.output).write_text(diff_text)
                print('Wrote diff to', args.output)
            else:
                print(diff_text)
        elif args.action == "history":
            aid = args.artifact_id
            if not aid:
                raise SystemExit("--artifact-id required for history")
            import requests as rq
            r = rq.get(f"{client.base_url}/artifacts/{aid}/history", headers=client._headers())
            r.raise_for_status()
            print(json.dumps(r.json(), indent=2))
        return 0

    if args.cmd == "webhooks":
        if args.action == "list":
            data = client.list_webhooks()
            print(json.dumps(data, indent=2))
        elif args.action == "add":
            if not args.url or not args.secret:
                raise SystemExit("--url and --secret required")
            data = client.register_webhook(args.url, args.secret, args.events)  # type: ignore
            print(json.dumps(data, indent=2))
        return 0

    if args.cmd == "run":
        data = client.run_execution(phases=args.phases or None, parallel=True, dry_run=bool(args.dry_run))
        print(json.dumps(data, indent=2))
        return 0

  if args.cmd == "public":
        if args.pubcmd == "status":
            out = client.public_status()
            print(json.dumps(out, indent=2))
            return 0
        if args.pubcmd == "artifacts":
            if args.action == "list":
                out = client.public_list_artifacts(
                    phase=args.phase,
                    status_filter=args.status_filter,
                    page=args.page,
                    page_size=args.page_size,
                    execution_id=args.execution_id,
                )
                print(json.dumps(out, indent=2))
                return 0
            if args.action == "sign":
                if not args.artifact_id:
                    raise SystemExit("--artifact-id required for public artifacts sign")
                out = client.public_sign_artifact(args.artifact_id, ttl_seconds=args.ttl_seconds)
                print(json.dumps(out, indent=2))
                return 0
            if args.action in ("download", "signed-url"):
                if not args.artifact_id:
                    raise SystemExit("--artifact-id required")
                info = client.public_sign_artifact(args.artifact_id, ttl_seconds=args.ttl_seconds)
                url_path = info.get('url')
                if not url_path:
                    raise SystemExit("Failed to generate URL")
                # Build absolute URL from base
                base = client.base_url.replace('/api/v1', '')
                full_url = base.rstrip('/') + url_path
                if args.action == 'signed-url':
                    print(json.dumps({"url": full_url, "expires_at": info.get('expires_at')}, indent=2))
                    return 0
                # Download
                import requests as rq
                headers = {}
                if client.api_key and 'sig=' not in full_url:
                    headers['X-API-Key'] = client.api_key
                r = rq.get(full_url, headers=headers, stream=True)
                r.raise_for_status()
                out_path = args.output or f"{args.artifact_id}.yaml"
                with open(out_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print("Downloaded to", out_path)
                return 0
        if args.pubcmd == "set-key":
            client.api_key = args.api_key
            save_client(client)
            print("Saved public API key")
            return 0

    if args.cmd == "admin":
        if args.admcmd == "retention":
            import requests as rq
            url = f"{client.base_url.replace('/api/v1','')}/api/v1/admin/retention/maintain"
            headers = client._headers() if hasattr(client, '_headers') else {}
            params = {"category": args.category, "days": args.days, "action": args.action}
            r = rq.post(url, headers=headers, params=params)
            if not r.ok:
                print(r.status_code, r.text)
                raise SystemExit(1)
            print(r.json())
            return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
