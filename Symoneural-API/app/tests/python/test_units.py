import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from symoneural_api import units


class UnitsTest(unittest.TestCase):
    def test_registry_shape(self):
        names = list(units.REGISTRY)
        self.assertEqual(names, ["ravencalc", "chat", "coder", "project", "streamer", "remix", "studio", "miner"])
        ports = [u.port for u in units.REGISTRY.values()]
        self.assertEqual(ports, list(range(8801, 8809)))
        self.assertEqual(len(set(ports)), 8)

    def test_resources_and_gpu_units(self):
        gpu = [u.name for u in units.gpu_units()]
        self.assertEqual(gpu, ["chat", "studio", "miner"])
        self.assertIs(units.unit("ravencalc").resource, units.Resource.CPU)
        self.assertIs(units.unit("streamer").resource, units.Resource.NET)

    def test_env_names(self):
        u = units.unit("chat")
        self.assertEqual(u.token_env, "SYM_CHAT_TOKEN")
        self.assertEqual(u.enabled_variable, "SYM_CHAT_ENABLED")

    def test_backing_packages_all_estate(self):
        for name, pkgs in units.backing_packages().items():
            self.assertTrue(pkgs, name)
            for p in pkgs:
                self.assertTrue(p.startswith("symoneural-"), p)

    def test_unknown_unit(self):
        with self.assertRaises(KeyError):
            units.unit("nosuch")


if __name__ == "__main__":
    unittest.main()
