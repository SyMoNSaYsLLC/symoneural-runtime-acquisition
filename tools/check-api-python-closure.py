#!/usr/bin/env python3
"""API view of the estate-wide Python closure gate. Same implementation, scoped to
--runtime API; see tools/check-python-runtime-closures.py."""
import os, sys, runpy
sys.argv = [sys.argv[0], "--runtime", "API"] + sys.argv[1:]
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-python-runtime-closures.py"), run_name="__main__")
