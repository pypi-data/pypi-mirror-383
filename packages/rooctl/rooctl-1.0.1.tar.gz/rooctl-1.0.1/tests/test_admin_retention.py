import unittest
from unittest import mock
import types


class TestAdminRetention(unittest.TestCase):
    def test_admin_retention_calls_api(self):
        # Fake requests
        class FakeResp:
            ok = True
            def json(self):
                return {"ok": True}
        class FakeReq:
            def post(self, *a, **k):
                return FakeResp()
        import sys
        sys.modules['requests'] = FakeReq()
        from importlib import import_module
        m = import_module('cli.rooctl')
        fake_client = types.SimpleNamespace(base_url='http://localhost:8000/api/v1', _headers=lambda: {})
        with mock.patch.object(m, 'OrchestrationClient', return_value=fake_client):
            argv = sys.argv
            try:
                sys.argv = ['rooctl', 'admin', 'retention', '--category', 'audit']
                rc = m.main()
                self.assertEqual(rc, 0)
            finally:
                sys.argv = argv

if __name__ == '__main__':
    unittest.main()

