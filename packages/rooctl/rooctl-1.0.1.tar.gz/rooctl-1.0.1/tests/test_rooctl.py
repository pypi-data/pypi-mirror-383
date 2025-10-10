import unittest
from unittest import mock
import types


class TestRooctl(unittest.TestCase):
    def test_status_calls_sdk(self):
        # Patch OrchestrationClient inside rooctl module
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace(status=lambda: {"ok": True})
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            # Call main with args ['status']
            import sys
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'status']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

    def test_artifacts_list_calls_sdk(self):
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace(
            list_artifacts=lambda **kwargs: {"artifacts": [], "total": 0},
        )
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            import sys
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'artifacts', 'list']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

    def test_public_status_calls_sdk(self):
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace(
            public_status=lambda: {"ok": True},
        )
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            import sys
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'public', 'status']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

    def test_artifacts_sign_calls_sdk(self):
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace(
            sign_artifact=lambda aid: {"url":"/x","expires_at":None},
        )
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            import sys
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'artifacts', 'sign', '--artifact-id', 'a1']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

    def test_run_calls_sdk(self):
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace(
            run_execution=lambda **kwargs: {"execution_id":"exec_1"},
        )
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            import sys
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'run', '--dry-run']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

    def test_artifacts_diff_uses_requests(self):
        # Inject fake requests module
        import sys
        class FakeResp:
            ok = True
            def json(self):
                return {"unified_diff":"diff"}
        class FakeReq:
            def get(self, *a, **k):
                return FakeResp()
        sys.modules['requests'] = FakeReq()
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace()
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'artifacts', 'diff', '--left', 'a', '--right', 'b', '--output', 'tmp_diff.txt']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv
                try:
                    import os
                    if os.path.exists('tmp_diff.txt'):
                        os.remove('tmp_diff.txt')
                except Exception:
                    pass

    def test_artifacts_history_uses_requests(self):
        import sys
        class FakeResp:
            def raise_for_status(self):
                return None
            def json(self):
                return {"artifact_id":"a","ancestors":[]}
        class FakeReq:
            def get(self, *a, **k):
                return FakeResp()
        sys.modules['requests'] = FakeReq()
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake = types.SimpleNamespace()
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake):
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'artifacts', 'history', '--artifact-id', 'a']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv


if __name__ == '__main__':
    unittest.main()
