import os, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from symoneural_api.routeclass import AuthzError, RouteClass, authenticate, enforce


class RouteClassTest(unittest.TestCase):
    def setUp(self):
        for k in ("SYM_OWNER_TOKEN", "SYM_CHAT_TOKEN"):
            os.environ.pop(k, None)

    def test_public_needs_nothing(self):
        self.assertIsNone(enforce(RouteClass.PUBLIC_BOOTSTRAP, unit="chat", token=None))

    def test_shared_auth_requires_configured_unit(self):
        with self.assertRaises(AuthzError) as cm:
            enforce(RouteClass.SHARED_AUTH, unit="chat", token=None)
        self.assertEqual(cm.exception.status, 503)
        os.environ["SYM_CHAT_TOKEN"] = "u"
        self.assertIsNone(enforce(RouteClass.SHARED_AUTH, unit="chat", token=None))

    def test_authenticate_order_and_failures(self):
        with self.assertRaises(AuthzError) as cm:
            authenticate(None, "chat")
        self.assertEqual(cm.exception.status, 401)
        os.environ["SYM_OWNER_TOKEN"] = "own"; os.environ["SYM_CHAT_TOKEN"] = "unit"
        self.assertEqual(authenticate("own", "chat").kind, "operator")
        self.assertEqual(authenticate("unit", "chat").kind, "unit")
        with self.assertRaises(AuthzError):
            authenticate("wrong", "chat")

    def test_operator_only_hides_itself(self):
        os.environ["SYM_OWNER_TOKEN"] = "own"; os.environ["SYM_CHAT_TOKEN"] = "unit"
        with self.assertRaises(AuthzError) as cm:
            enforce(RouteClass.OPERATOR_ONLY, unit="chat", token="unit")
        self.assertEqual(cm.exception.status, 404)
        self.assertEqual(enforce(RouteClass.OPERATOR_ONLY, unit="chat", token="own").kind, "operator")

    def test_entitlement(self):
        os.environ["SYM_OWNER_TOKEN"] = "own"; os.environ["SYM_CHAT_TOKEN"] = "unit"
        with self.assertRaises(AuthzError) as cm:
            enforce(RouteClass.ENTITLEMENT_REQUIRED, unit="chat", token="unit")
        self.assertEqual(cm.exception.status, 500)      # no application named
        with self.assertRaises(AuthzError) as cm:
            enforce(RouteClass.ENTITLEMENT_REQUIRED, unit="chat", token="unit", application="chat")
        self.assertEqual(cm.exception.status, 403)      # unit principal has no entitlements today
        self.assertEqual(enforce(RouteClass.ENTITLEMENT_REQUIRED, unit="chat", token="own", application="chat").kind, "operator")


if __name__ == "__main__":
    unittest.main()
