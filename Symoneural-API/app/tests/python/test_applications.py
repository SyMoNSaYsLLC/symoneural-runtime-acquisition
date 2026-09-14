"""Generic application-registry tests (not about DispatchOS) and, separately, the DispatchOS ones."""
import importlib, os, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from symoneural_api import applications as A, units
from symoneural_api import apps  # noqa: F401


def defn(app_id="demo-x", **kw):
    base = dict(application_id=app_id, display_name="X", mode=A.Mode.DEMO, required_units=("ravencalc",),
                optional_units=("chat",), public_demo=True, page=f"/demo/{app_id}.html",
                policy=A.DemoPolicy(allowed_units=frozenset({"ravencalc", "chat"})))
    base.update(kw)
    return A.ApplicationDefinition(**base)


class GenericRegistryTest(unittest.TestCase):
    def tearDown(self):
        for k in list(A.REGISTRY):
            if k != "dispatchos":
                A.unregister(k)

    def test_register_and_lookup(self):
        a = A.register(defn())
        self.assertIs(A.application("demo-x"), a)
        self.assertEqual(a.api_namespace, "/api/apps/demo-x")
        self.assertIs(A.for_page("/demo/demo-x.html"), a)

    def test_duplicate_id_rejected(self):
        A.register(defn())
        with self.assertRaises(ValueError):
            A.register(defn())

    def test_missing_unit_rejected(self):
        with self.assertRaises(ValueError):
            A.register(defn(required_units=("nosuch",)))

    def test_public_demo_needs_page_and_policy(self):
        with self.assertRaises(ValueError):
            A.register(defn(page=None))
        with self.assertRaises(ValueError):
            A.register(defn(policy=None))
        with self.assertRaises(ValueError):
            A.register(defn(page="/demo/other.html"))          # page must equal /demo/<id>.html
        with self.assertRaises(ValueError):
            A.register(defn(policy=A.DemoPolicy(allowed_units=frozenset({"miner"}))))   # undeclared unit

    def test_admin_never_exposed_by_demo(self):
        with self.assertRaises(ValueError):
            A.register(defn(policy=A.DemoPolicy(expose_admin=True, allowed_units=frozenset({"ravencalc"}))))

    def test_readiness_states(self):
        a = A.register(defn())
        for k in ("SYM_RAVENCALC_TOKEN", "SYM_RAVENCALC_ENABLED", "SYM_CHAT_TOKEN", "SYM_CHAT_ENABLED"):
            os.environ.pop(k, None)
        r = A.readiness(a, installed_packages=set())
        self.assertEqual(r["readiness"], "BLOCKED")
        self.assertEqual(r["blocking_units"], ["ravencalc"])
        self.assertTrue(any("not installed" in x for x in r["units"][0]["reasons"]))
        # required unit satisfied, optional not -> DEGRADED
        os.environ["SYM_RAVENCALC_TOKEN"] = "t"; os.environ["SYM_RAVENCALC_ENABLED"] = "1"
        have = set(units.unit("ravencalc").backed_by)
        r = A.readiness(a, installed_packages=have)
        self.assertEqual(r["readiness"], "DEGRADED")
        self.assertEqual(r["degraded_units"], ["chat"])
        # everything satisfied -> READY
        os.environ["SYM_CHAT_TOKEN"] = "t"; os.environ["SYM_CHAT_ENABLED"] = "1"
        have |= set(units.unit("chat").backed_by)
        self.assertEqual(A.readiness(a, installed_packages=have)["readiness"], "READY")
        # unknown installed set is never READY
        self.assertEqual(A.readiness(a, installed_packages=None)["readiness"], "BLOCKED")

    def test_policy_restricts_model(self):
        p = A.DemoPolicy(allowed_models=frozenset({"m1"}))
        self.assertFalse(p.restricts_model("m1")); self.assertTrue(p.restricts_model("m2"))

    def test_public_descriptor_has_no_secrets_or_paths(self):
        d = A.register(defn()).to_public()
        flat = str(d)
        for bad in ("/home/", "/run/", "TOKEN", "SYM_", ".so", "/etc/"):
            self.assertNotIn(bad, flat)

    def test_route_class_by_mode(self):
        from symoneural_api.routeclass import RouteClass
        self.assertIs(A.route_class_for(defn()), RouteClass.PUBLIC_BOOTSTRAP)
        self.assertIs(A.route_class_for(defn(mode=A.Mode.CUSTOMER, public_demo=False, page=None, policy=None)), RouteClass.ENTITLEMENT_REQUIRED)
        self.assertIs(A.route_class_for(defn(mode=A.Mode.INTERNAL, public_demo=False, page=None, policy=None)), RouteClass.OPERATOR_ONLY)


class DispatchOSTest(unittest.TestCase):
    def test_definition_loads_and_maps(self):
        a = A.application("dispatchos")
        self.assertEqual(a.page, "/demo/dispatchos.html")
        self.assertEqual(a.api_namespace, "/api/apps/dispatchos")
        self.assertTrue(a.public_demo)
        self.assertIs(A.for_page("/demo/dispatchos.html"), a)

    def test_required_units_resolve(self):
        a = A.application("dispatchos")
        for u in (*a.required_units, *a.optional_units):
            units.unit(u)

    def test_demo_policy(self):
        p = A.application("dispatchos").policy
        self.assertFalse(p.allow_mutations); self.assertFalse(p.expose_admin)
        self.assertEqual(p.tool_capabilities, frozenset({"read_status"}))

    def test_no_customer_name_in_generic_code(self):
        root = Path(__file__).resolve().parents[2]
        import glob
        files = ["symoneural_api/applications.py", "symoneural_api/main.py", "symoneural_api/routeclass.py",
                 "symoneural_api/units.py", "symoneural_api/gpulock.py", "symoneural_api/__init__.py"]
        files += [os.path.relpath(p, root) for p in glob.glob(str(root / "src" / "*.c")) + glob.glob(str(root / "include" / "symoneural" / "*.h"))]
        for f in files:
            self.assertNotIn("dispatchos", (root / f).read_text().lower(), f)


if __name__ == "__main__":
    unittest.main()
