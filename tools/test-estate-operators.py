#!/usr/bin/env python3
"""Isolated regressions: no real BitBake, source edits, deletion, or renicing.

Run: python3 -B tools/test-estate-operators.py
All generated fixtures live in a new /tmp directory, preserved for inspection.
"""
import contextlib
import ast
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import estate_processes as processes
import proof_support as proof
import git_tree_identity as trees


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


closure = module("closure", "check-python-runtime-closures.py")
verify = module("verify", "verify-acquisition.py")
evidence = module("evidence", "check-evidence-hashes.py")
FIXTURE = Path(tempfile.mkdtemp(prefix="symoneural-operator-regressions-"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)
    path.chmod(0o700)
    return path


def run(*args, env=None):
    return subprocess.run(args, text=True, capture_output=True, timeout=15,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})


class Processes(unittest.TestCase):
    def test_exact_script_and_recipe_named_grep(self):
        self.assertTrue(processes.is_bitbake(["python3", "/boot/bin/bitbake", "symoneural-grep"], "python3"))
        self.assertTrue(processes.is_bitbake(["python3", "/boot/bin/bitbake-server", "--"], "python3"))
        self.assertFalse(processes.is_bitbake(["bash", "-c", "pgrep bitbake"], "bash"))
        self.assertFalse(processes.is_bitbake(["node", "/srv/server.js", "bitbake"], "node"))

    def test_existing_build_identified_by_cwd(self):
        bd = Path("/estate/Symoneural-Common/build/devtool-master")
        row = dict(pid=42, ppid=1, start="1", cwd=bd, comm="python3", bake=True)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(processes.check({42: row}, bd), 1)
            self.assertEqual(processes.check({42: row}, Path("/estate/other")), 0)

    def test_descendants_excludes_unrelated_node(self):
        root = Path("/estate")
        rows = {
            1: dict(bake=True, cwd=root / "Symoneural-Common/build/devtool-master", ppid=0),
            2: dict(bake=False, cwd=root / "Symoneural-Common/build", ppid=1),
            3: dict(bake=False, cwd=Path("/srv"), ppid=0),
            4: dict(bake=True, cwd=Path("/other/build"), ppid=0),
        }
        self.assertEqual(processes.build_descendants(rows, root), {1, 2})

    def test_private_namespace_refused(self):
        proc = FIXTURE / "private-proc"
        write(proc / "1/comm", "codex\n")
        with self.assertRaises(processes.ProbeError):
            processes.snapshot(proc)

    def test_probe_error_fails_closed(self):
        with patch.object(sys, "argv", ["probe", "guard"]), patch.object(processes, "snapshot", side_effect=processes.ProbeError("unreadable")), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(processes.main(), 2)


class Launcher(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="launcher-", dir=FIXTURE))
        self.bd = self.root / "Symoneural-Common/build/devtool-master"
        (self.bd / "conf").mkdir(parents=True)
        self.boot = self.root / "bootstrap"
        write(self.boot / "openembedded-core/oe-init-build-env", 'return 42\n')
        write(self.root / "tools/estate_processes.py", 'import sys; sys.exit(0)\n')
        text = (TOOLS / "symonbake").read_text().replace("/home/google/symoneural-bootstrap-master", str(self.boot))
        self.launcher = write(self.root / "tools/symonbake", text)
        self.binary = write(self.root / "bin/bitbake", '#!/bin/sh\necho MOCK_BUILD\nexit 7\n')
        self.env = {"PATH": str(self.binary.parent) + os.pathsep + os.environ["PATH"]}

    def test_help_and_no_arguments(self):
        self.assertEqual(run(str(self.launcher), "--help").returncode, 0)
        self.assertEqual(run(str(self.launcher)).returncode, 2)

    def test_list_and_path_do_not_initialize(self):
        self.assertIn("Symoneural-Common", run(str(self.launcher), "--list").stdout)
        result = run(str(self.launcher), "--show-path", "Symoneural-Common")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(self.bd))

    def test_rejects_traversal_and_unknown_runtime(self):
        self.assertEqual(run(str(self.launcher), "../elsewhere", "x").returncode, 2)
        self.assertNotEqual(run(str(self.launcher), "Symoneural-Unknown", "x").returncode, 0)

    def test_setup_failure_never_builds(self):
        result = run(str(self.launcher), "Symoneural-Common", "recipe", env=self.env)
        self.assertEqual(result.returncode, 42, result.stderr)
        self.assertNotIn("MOCK_BUILD", result.stdout)

    def test_child_failure_propagates(self):
        write(self.boot / "openembedded-core/oe-init-build-env", 'return 0\n')
        result = run(str(self.launcher), "Symoneural-Common", "recipe", env=self.env)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertIn("MOCK_BUILD", result.stdout)

    def test_probe_failure_never_initializes(self):
        write(self.root / "tools/estate_processes.py", 'import sys; sys.exit(2)\n')
        self.assertEqual(run(str(self.launcher), "Symoneural-Common", "recipe").returncode, 2)

    def test_cooperating_wrapper_lock(self):
        import fcntl
        with (self.bd / ".symonbake.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = run(str(self.launcher), "Symoneural-Common", "recipe")
            self.assertEqual(result.returncode, 1)
            self.assertIn("another wrapper", result.stderr)


class BuildAll(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="build-all-", dir=FIXTURE))
        self.launcher = write(self.root / "tools/build-all", (TOOLS / "build-all").read_text())
        self.mock = write(self.root / "tools/symonbake", '#!/bin/sh\nexit 7\n')
        for rt in ("Common", "Build", "Live"):
            (self.root / f"Symoneural-{rt}/build/devtool-master/conf").mkdir(parents=True)
            write(self.root / f"meta-symoneural/recipes-{rt.lower()}/symoneural-test/symoneural-test_1.bb", "# fixture\n")
        self.env = {"BUILD_ALL_LOGS": str(self.root), "BUILD_ALL_JOBS": "2"}

    def test_child_failure_and_per_run_logs(self):
        first = run(str(self.launcher), env=self.env)
        self.assertEqual(first.returncode, 1)
        self.assertIn("rc=7", first.stdout)
        write(self.mock, '#!/bin/sh\nexit 0\n')
        second = run(str(self.launcher), env=self.env)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(len(list(self.root.glob("symoneural-build-all.*"))), 2)

    def test_dry_run_and_missing_runtimes(self):
        result = run(str(self.launcher), "--dry-run", env=self.env)
        self.assertEqual(result.returncode, 0)
        for rt in ("Common", "Build", "Live"):
            self.assertIn("Symoneural-" + rt, result.stdout)
        self.assertFalse(list(self.root.glob("symoneural-build-all.*")))

    def test_invalid_job_count(self):
        for count in ("0", "-1", "oops", "999999999999999999999"):
            self.assertEqual(run(str(self.launcher), env={**self.env, "BUILD_ALL_JOBS": count}).returncode, 2)


class ProofSafety(unittest.TestCase):
    def test_existing_roots_never_removed(self):
        sentinel = write(FIXTURE / "existing/KEEP", "keep")
        for target in (Path("/tmp"), FIXTURE, sentinel.parent):
            with self.assertRaises(ValueError):
                proof.new_root("Common", str(target))
        self.assertEqual(sentinel.read_text(), "keep")

    def test_new_root_private_unique(self):
        first = proof.new_root("Common", parent=FIXTURE)
        second = proof.new_root("Common", parent=FIXTURE)
        self.assertNotEqual(first, second)
        self.assertEqual(first.stat().st_mode & 0o777, 0o700)

    def test_relative_and_source_destinations_rejected(self):
        with self.assertRaises(ValueError):
            proof.new_root("Common", "relative")
        with self.assertRaises(ValueError):
            proof.new_root("Common", parent=proof.ROOT / "tools")

    def test_empty_driver_and_false_prefix_rejected(self):
        match = proof.driver_package_matches
        self.assertFalse(match("", "libcuda1", "615.71.09-2", "libcuda.so.1"))
        self.assertFalse(match("615.71.09", "libcuda1", "615.71.090-2", "libcuda.so.1"))
        self.assertFalse(match("615.71.09", "unrelated", "615.71.09-2", "libcuda.so.1"))
        self.assertFalse(match("615.71.09", "libcuda1", "615.71.09-2", "libunexpected.so.1"))
        self.assertTrue(match("615.71.09", "libcuda1:amd64", "1:615.71.09-2", "libcuda.so.1"))
        self.assertTrue(match("615.71.09", "libnvidia-ml1", "615.71.09-2", "libnvidia-ml.so.1"))

    def test_cleanup_command_absent(self):
        for name in ("clean-root-proof", "api-clean-root-proof", "llm-clean-root-proof", "cuda-clean-root-proof"):
            self.assertNotIn('rm -rf', (TOOLS / name).read_text())
            self.assertEqual(run(str(TOOLS / name), "--help").returncode, 0)

    def test_trace_absence_fails(self):
        with self.assertRaises(ValueError):
            proof.trace_libraries(FIXTURE / "no-traces")

    def test_trace_literal_paths_and_launcher_order(self):
        root = FIXTURE / "root.with regex [and spaces]"
        prefix = 'calling init: '
        target = str(root / "lib/ld-linux-x86-64.so.2")
        host = '/lib/x86_64-linux-gnu/libc.so.6'
        trace = write(root / "tmp/ld-debug.100", prefix + host + '\n' + prefix + target + '\n')
        result = proof.trace_libraries(root)
        self.assertEqual(result['outside'], set())
        self.assertEqual(result['launchers'], 1)
        write(trace, prefix + target + '\n' + prefix + host + '\n')
        self.assertEqual(proof.trace_libraries(root)['outside'], {host})

    def test_s2_child_keeps_driver_separate_from_shell(self):
        root = FIXTURE / 's2-child'
        target = str(root / 'lib/ld-linux-x86-64.so.2')
        host_ld = '/lib64/ld-linux-x86-64.so.2'
        host_c = '/lib/x86_64-linux-gnu/libc.so.6'
        cuda = '/usr/lib/x86_64-linux-gnu/libcuda.so.1'
        trace = write(root / 'tmp/ld-debug.200', ''.join('calling init: ' + p + '\n' for p in [host_ld, host_c, target, cuda]))
        result = proof.trace_libraries(root)
        self.assertEqual(result['launchers'], 1)
        self.assertEqual(result['outside'], {cuda})
        write(trace, trace.read_text() + 'calling init: ' + host_c + '\n')
        self.assertEqual(proof.trace_libraries(root)['outside'], {host_c, cuda})


class TreeIdentity(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='tree-identity-', dir=FIXTURE))
        self.assertEqual(run('git', 'init', str(self.root)).returncode, 0)
        self.blob = subprocess.run(['git', '-C', str(self.root), 'hash-object', '-w', '--stdin'], input=b'fixture\n', capture_output=True, check=True).stdout.decode().strip()

    def tree(self, entries):
        return subprocess.run(['git', '-C', str(self.root), 'mktree', '--missing'], input=entries, text=True, capture_output=True, check=True).stdout.strip()

    def test_rebuilt_tree_matches_git_without_writes(self):
        child = self.tree(f'100644 blob {self.blob}\tfile\n')
        source = self.tree(f'040000 tree {child}\ta\n100644 blob {self.blob}\ta.c\n')
        commit = 'a' * 40
        expected = self.tree(f'160000 commit {commit}\ta\n100644 blob {self.blob}\ta.c\n')
        before = sorted(p.relative_to(self.root) for p in (self.root / '.git/objects').rglob('*'))
        self.assertEqual(trees.rebuilt_tree(self.root, source, [('a', commit)]), expected)
        self.assertEqual(before, sorted(p.relative_to(self.root) for p in (self.root / '.git/objects').rglob('*')))

    def test_missing_and_duplicate_paths_fail(self):
        source = self.tree(f'100644 blob {self.blob}\tfile\n')
        with self.assertRaises(trees.TreeIdentityError):
            trees.rebuilt_tree(self.root, source, [('missing', 'a' * 40)])
        with self.assertRaises(trees.TreeIdentityError):
            trees.rebuilt_tree(self.root, source, [('file', 'a' * 40), ('file', 'b' * 40)])


class Evidence(unittest.TestCase):
    def test_evidence_mismatch_is_not_rebaselined(self):
        import hashlib
        root = Path(tempfile.mkdtemp(prefix='evidence-', dir=FIXTURE))
        write(root / 'artifact', 'actual bytes')
        manifest = write(root / 'SHA256SUMS', hashlib.sha256(b'approved bytes').hexdigest() + '  artifact\n')
        before = manifest.read_bytes()
        rows = evidence.audit(root, [manifest])
        self.assertEqual(rows[0]['status'], 'MISMATCH')
        self.assertEqual(manifest.read_bytes(), before)

    def test_missing_and_empty_evidence(self):
        root = Path(tempfile.mkdtemp(prefix='evidence-', dir=FIXTURE))
        manifest = write(root / 'SHA256SUMS', 'a' * 64 + '  missing\n')
        self.assertEqual(evidence.audit(root, [manifest])[0]['status'], 'MISSING')
        write(manifest, '')
        self.assertEqual(evidence.audit(root, [manifest])[0]['status'], 'EMPTY MANIFEST')

    def test_completeness_failure_exit(self):
        with patch.object(verify, "FAIL", []), patch.object(verify, "COMPLETE_FAIL", ["missing"]):
            self.assertEqual(verify.result_code(), 1)

    def test_identity_compares_url_tree_and_recipe(self):
        a = dict(source_path="source", upstream_url="upstream", commit_sha="a", tree_sha="b", worktree="clean", recipe_path="r", recipe_SRCREV="a", lock_state="VERIFIED")
        for key in ("upstream_url", "tree_sha", "recipe_SRCREV", "lock_state"):
            self.assertNotEqual(verify.ident("source", a), verify.ident("source", {**a, key: "changed"}))
        self.assertTrue(verify.source_failures([{**a, "recipe_SRCREV": "wrong"}]))

    def test_target_implementation_version(self):
        with patch.object(closure.glob, "glob", return_value=["/work/python3/3.14.7/"]):
            env = closure.target_environment(["Common"])
        self.assertEqual(env["implementation_version"], "3.14.7")
        self.assertEqual(env["python_full_version"], "3.14.7")

    def test_absent_target_version_fails(self):
        with patch.object(closure.glob, "glob", return_value=[]):
            with self.assertRaises(ValueError):
                closure.target_environment(["Common"])

    def test_unknown_runtime_rejected(self):
        result = run(sys.executable, "-B", str(TOOLS / "check-python-runtime-closures.py"), "--runtime", "not-a-runtime")
        self.assertEqual(result.returncode, 2)

    def test_zero_wheels_not_pass(self):
        with patch.object(sys, "argv", ["closure", "--runtime", "Common"]), patch.object(closure, "built_wheels", return_value={}), patch.object(closure, "target_environment", return_value={}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(closure.main(), 1)

    def test_audit_failed_subcommands_propagate(self):
        body = (TOOLS / "audit-workscope.sh").read_text()
        result = run("bash", "-c", 'python3() { return 23; }\n' + body)
        self.assertEqual(result.returncode, 1)

    def test_pkgdata_never_means_done(self):
        body = (TOOLS / "audit-workscope.sh").read_text()
        self.assertNotIn('status = "DONE"', body)
        self.assertIn('PKGDATA EXISTS; NOT QA', body)


class TorchRpath(unittest.TestCase):
    def test_gloo_hook_flag_scope_and_missing_input(self):
        recipe = (TOOLS.parent / "meta-symoneural/recipes-common/symoneural-pytorch/symoneural-pytorch_git.bb").read_text()
        hook = recipe.split('    gloo_hook = """\\\n', 1)[1].split('\n"""', 1)[0]
        directory = FIXTURE / 'gloo-hook'
        hook_path = write(directory / 'gloo-hook.cmake', hook)
        write(directory / 'CMakeLists.txt', '''cmake_minimum_required(VERSION 3.21)
project(parent NONE)
set(USE_CUDA ON)
set(CMAKE_CUDA_FLAGS "parent-flags")
add_subdirectory(child)
if(NOT CMAKE_CUDA_FLAGS STREQUAL "parent-flags")
  message(FATAL_ERROR "Gloo scope leaked into parent")
endif()
''')
        write(directory / 'child/CMakeLists.txt', '''project(gloo NONE)
if(NOT CMAKE_CUDA_FLAGS MATCHES "ffile-prefix-map")
  message(FATAL_ERROR "Gloo did not receive prefix map")
endif()
''')
        args = ['cmake', '-S', str(directory), '-B', str(directory / 'out'), '-DCMAKE_PROJECT_gloo_INCLUDE=' + str(hook_path)]
        self.assertEqual(run(*args, env={'TORCH_NVCC_FLAGS': '-Xcompiler=-ffile-prefix-map=/build=/src'}).returncode, 0)
        self.assertNotEqual(run(*args, env={'TORCH_NVCC_FLAGS': ''}).returncode, 0)

    def test_real_elf_cleaned_and_verified_by_value(self):
        directory = FIXTURE / "torch-tmp/work"
        directory.mkdir(parents=True)
        source = write(directory / "fixture.c", "int fixture(void) { return 1; }\n")
        library = directory / "libfixture.so"
        result = run("cc", "-shared", "-fPIC", str(source), "-Wl,-rpath,$ORIGIN:" + str(directory), "-o", str(library))
        self.assertEqual(result.returncode, 0, result.stderr)
        recipe = (TOOLS.parent / "meta-symoneural/recipes-common/symoneural-pytorch/symoneural-pytorch_git.bb").read_text()
        body = recipe.split('do_install:append() {', 1)[1].split('\n}', 1)[0]
        body = body.replace('${D}${PYTHON_SITEPACKAGES_DIR}/torch/lib', str(directory))
        body = body.replace('${WORKDIR}', str(directory)).replace('${TMPDIR}', str(directory.parent))
        body = body.replace('${READELF}', 'readelf')
        prefix = 'bbfatal() { echo "$*" >&2; exit 1; }; bbnote() { :; };\n'
        result = run("bash", "-c", prefix + body)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(run("chrpath", "-l", str(library)).stdout, r'R(?:UN)?PATH=\$ORIGIN')
        # Idempotence: the old check rejected this already-clean ELF filename.
        self.assertEqual(run("bash", "-c", prefix + body).returncode, 0)
        self.assertNotEqual(run("bash", "-c", prefix + body.replace('readelf -d', 'false')).returncode, 0)


class CudaBoundaryQa(unittest.TestCase):
    def setUp(self):
        source = (TOOLS.parent / 'meta-symoneural/classes/symoneural-cuda.bbclass').read_text()
        body = source.split('python symon_cuda_qa_s2() {\n', 1)[1].split('\n}', 1)[0]
        namespace = {}
        exec('def qa(d, bb):\n' + body, namespace)
        self.qa = namespace['qa']
        self.root = Path(tempfile.mkdtemp(prefix='cuda-boundary-', dir=FIXTURE))
        library = self.root / 'packages/demo/usr/lib/fixture.so'
        library.parent.mkdir(parents=True)
        library.write_bytes(b'\x7fELF')
        self.values = {'PKGDEST': str(self.root / 'packages'),
                       'PKGDATA_DIR': str(self.root / 'pkgdata'), 'READELF': 'readelf',
                       'SYMON_CUDA_S2_LIBS': 'libcuda.so.1 libnvidia-ml.so.1', 'PACKAGES': 'demo'}
        self.notes = []

    def inspect(self, output='', status=0):
        from types import SimpleNamespace
        def fatal(message):
            raise RuntimeError(message)
        data = SimpleNamespace(getVar=self.values.get)
        logger = SimpleNamespace(fatal=fatal, note=self.notes.append)
        result = subprocess.CompletedProcess(['readelf'], status, output, 'inspection failure' if status else '')
        with patch('subprocess.run', return_value=result):
            self.qa(data, logger)

    def test_failed_inspection_is_fatal(self):
        with self.assertRaisesRegex(RuntimeError, 'ELF inspection failed'):
            self.inspect(status=1)

    def test_provider_and_explicit_driver_boundary(self):
        write(self.root / 'pkgdata/shlibs2/libfixture.list', 'libfixture.so.1:libfixture:1.0\n')
        self.inspect(' (NEEDED) Shared library: [libfixture.so.1]\n (NEEDED) Shared library: [libcuda.so.1]\n')
        self.assertIn('1 NEEDED entries resolved by providers', self.notes[-1])
        self.assertIn('libcuda.so.1', self.notes[-1])

    def test_unprovided_dependency_is_fatal(self):
        with self.assertRaisesRegex(RuntimeError, 'libraries without a provider'):
            self.inspect(' (NEEDED) Shared library: [libunexpected.so.1]\n')

    def test_repeated_driver_entries_not_counted_as_providers(self):
        self.inspect(' (NEEDED) Shared library: [libcuda.so.1]\n' * 2)
        self.assertIn('0 NEEDED entries resolved by providers', self.notes[-1])


class NativeAuditSafety(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='native-audit-', dir=FIXTURE))
        source = ast.parse((TOOLS / 'check-native-linkage.py').read_text())
        functions = ast.Module(body=[node for node in source.body if isinstance(node, ast.FunctionDef) and node.name in {'sh', 'unpack'}], type_ignores=[])
        self.ns = dict(os=os, subprocess=subprocess, UNPACK=str(self.root), UNPACKED={})
        exec(compile(functions, 'native-audit-functions', 'exec'), self.ns)

    def test_failed_inspection_is_fatal(self):
        with self.assertRaises(SystemExit):
            self.ns['sh']('false')

    def test_package_extraction_uses_literal_paths(self):
        import tarfile
        archive = self.root / 'data.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            info = tarfile.TarInfo('usr/lib/fixture')
            payload = b'fixture bytes'; info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
        ipk = self.root / 'package with spaces;not-a-command.ipk'
        self.assertEqual(run('ar', 'qc', str(ipk), str(archive)).returncode, 0)
        extracted = Path(self.ns['unpack'](str(ipk)))
        self.assertEqual((extracted / 'usr/lib/fixture').read_bytes(), b'fixture bytes')
        self.assertEqual(self.ns['unpack'](str(ipk)), str(extracted))


if __name__ == "__main__":
    print("Preserved isolated fixtures:", FIXTURE, flush=True)
    unittest.main(verbosity=2)
