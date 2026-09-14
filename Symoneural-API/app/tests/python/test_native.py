"""ctypes binding tests; run with SYM_API_NATIVE=<path to libsymoneural-api.so> (skipped otherwise).
Includes the cross-language proof: a lock taken through the C ABI is seen by the
Python implementation and vice versa - same file, same contract."""
import importlib, os, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from symoneural_api import native


@unittest.skipUnless(os.environ.get("SYM_API_NATIVE"), "SYM_API_NATIVE not set")
class NativeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["SYM_GPU_LOCK"] = os.path.join(self.tmp.name, "gpu.lock")
        native._instance = None
        self.n = native.load()
        import symoneural_api.gpulock as g
        self.g = importlib.reload(g)

    def tearDown(self):
        self.tmp.cleanup()

    def test_abi_and_capabilities(self):
        self.assertEqual(self.n.abi_version >> 16, native.ABI_MAJOR)
        self.assertEqual(self.n.version(), "1.0.0")
        self.assertIn("gpu-lock", self.n.capabilities())
        self.assertEqual(self.n.lock_path(), os.environ["SYM_GPU_LOCK"])

    def test_one_priority_table(self):
        table = self.n.priority_table()
        self.assertEqual(table, self.g.PRIORITY)                 # Python reads the C table
        self.assertEqual(table, self.g._FALLBACK_PRIORITY)       # and the fallback has not drifted
        self.assertEqual(self.n.priority("nosuch"), 50)

    def test_cross_language_lock(self):
        h = self.n.lock_acquire("chat", 0)                       # C takes it
        self.assertEqual(h.pid, os.getpid())
        self.assertEqual(self.g.current().unit, "chat")           # Python sees it
        with self.assertRaises(self.g.LockBusy):
            self.g.acquire("miner", timeout_s=0)
        self.assertTrue(self.n.lock_release("chat"))
        self.g.acquire("image", timeout_s=0)                     # Python takes it
        self.assertEqual(self.n.lock_current().unit, "image")     # C sees it
        with self.assertRaises(native.NativeError) as cm:
            self.n.lock_acquire("miner", 0)
        self.assertEqual(cm.exception.status, -5)                 # EBUSY, no path in the message
        self.assertNotIn(self.tmp.name, str(cm.exception))
        self.assertFalse(self.n.lock_release("miner"))
        self.assertTrue(self.g.release("image"))
        self.assertIsNone(self.n.lock_current())

    def test_rack_json_and_selftest(self):
        js = self.n.rack_json()
        self.assertTrue(js.startswith("{") and '"host":' in js)
        self.assertIn("PASS", self.n.selftest())

    def test_util_agrees_with_binding(self):
        util = os.environ.get("SYM_API_UTIL")
        if not util:
            self.skipTest("SYM_API_UTIL not set")
        out = subprocess.run([util, "units"], capture_output=True, text=True, env={**os.environ, "LD_LIBRARY_PATH": os.path.dirname(os.environ["SYM_API_NATIVE"])}).stdout
        table = {l.split()[0]: int(l.split()[1]) for l in out.splitlines() if l.strip()}
        self.assertEqual(table, self.n.priority_table())


if __name__ == "__main__":
    unittest.main()
