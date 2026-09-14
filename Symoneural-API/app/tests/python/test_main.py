"""HTTP surface regression via FastAPI's TestClient (needs fastapi + httpx on the interpreter)."""
import importlib, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    from fastapi.testclient import TestClient
except Exception:                                    # pragma: no cover
    TestClient = None


@unittest.skipIf(TestClient is None, "fastapi/httpx not importable here")
class MainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["SYM_GPU_LOCK"] = os.path.join(self.tmp.name, "gpu.lock")
        for k in list(os.environ):
            if k.startswith("SYM_") and k != "SYM_GPU_LOCK":
                del os.environ[k]
        import symoneural_api.gpulock, symoneural_api.main
        importlib.reload(symoneural_api.gpulock)
        self.main = importlib.reload(symoneural_api.main)
        self.c = TestClient(self.main.app)

    def tearDown(self):
        self.tmp.cleanup()

    def test_health_and_status_public(self):
        self.assertEqual(self.c.get("/api/health").json()["status"], "ready")
        states = {u["unit"]: u["state"] for u in self._units()}
        self.assertEqual(len(states), 8)
        self.assertTrue(all(s == "UNCONFIGURED" for s in states.values()), states)

    def test_status_reflects_token_enabled_and_lock(self):
        os.environ["SYM_CHAT_TOKEN"] = "t"
        st = {u["unit"]: u["state"] for u in self._units()}
        self.assertEqual(st["chat"], "OFFLINE")
        os.environ["SYM_CHAT_ENABLED"] = "1"
        st = {u["unit"]: u["state"] for u in self._units()}
        self.assertEqual(st["chat"], "READY")
        self.main.gpulock.acquire("chat", timeout_s=0)
        st = {u["unit"]: u["state"] for u in self._units()}
        self.assertEqual(st["chat"], "BUSY")
        os.environ["SYM_STUDIO_TOKEN"] = "t"; os.environ["SYM_STUDIO_ENABLED"] = "1"
        st = {u["unit"]: u["state"] for u in self._units()}
        self.assertEqual(st["studio"], "QUEUED")
        self.main.gpulock.release("chat")

    def _units(self):
        body = self.c.get("/api/status").json()
        if isinstance(body, list):
            return body
        for v in body.values():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "unit" in v[0]:
                return v
        raise AssertionError("no unit list in /api/status: %s" % list(body))

    def test_operator_routes(self):
        self.assertEqual(self.c.get("/api/operator/lock").status_code, 401)
        os.environ["SYM_API_TOKEN"] = "u"
        self.assertEqual(self.c.get("/api/operator/lock", headers={"Authorization": "Bearer u"}).status_code, 404)
        os.environ["SYM_OWNER_TOKEN"] = "own"
        r = self.c.get("/api/operator/lock", headers={"Authorization": "Bearer own"})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json()["holder"])
        self.main.gpulock.acquire("chat", timeout_s=0)
        r = self.c.post("/api/operator/lock/release?unit=chat", headers={"Authorization": "Bearer own"})
        self.assertEqual(r.json(), {"released": True, "unit": "chat"})

    def test_unit_detail(self):
        self.assertEqual(self.c.get("/api/unit/nosuch").status_code, 404)
        self.assertEqual(self.c.get("/api/unit/chat").status_code, 401)
        os.environ["SYM_OWNER_TOKEN"] = "own"
        r = self.c.get("/api/unit/chat", headers={"Authorization": "Bearer own"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["backed_by"], ["symoneural-llama-cpp"])

    def test_apps_namespace(self):
        r = self.c.get("/api/apps")
        self.assertEqual(r.status_code, 200)
        ids = [a["application_id"] for a in r.json()["applications"]]
        self.assertIn("dispatchos", ids)
        self.assertEqual(self.c.get("/api/apps?page=/demo/dispatchos.html").json()["applications"][0]["application_id"], "dispatchos")
        self.assertEqual(self.c.get("/api/apps?page=/demo/nope.html").status_code, 404)
        self.assertEqual(self.c.get("/api/apps/nosuch").status_code, 404)
        d = self.c.get("/api/apps/dispatchos").json()           # demo -> public
        self.assertEqual(d["api_namespace"], "/api/apps/dispatchos")
        os.environ["SYM_OPKG_STATUS"] = os.path.join(self.tmp.name, "status")     # no such file -> unknown set
        st = self.c.get("/api/apps/dispatchos/status").json()
        self.assertEqual(st["readiness"], "BLOCKED")
        self.assertTrue(any("unknown" in r for u in st["units"] for r in u["reasons"]))


if __name__ == "__main__":
    unittest.main()
