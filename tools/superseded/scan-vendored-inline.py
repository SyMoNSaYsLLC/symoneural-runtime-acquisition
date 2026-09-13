#!/usr/bin/env python3
"""Pass 2: detect third-party code vendored into ORDINARY directories
(the bitbake lib/ply pattern) - not just vendor/ or third_party/."""
import os,re,sys,json,hashlib
from collections import defaultdict
ROOT="/home/google/SymonSaysLLC"
SKIP={".git","node_modules","__pycache__",".github",".tox"}
# well-known third-party python/js/c packages that projects commonly vendor
KNOWN={"ply","bs4","beautifulsoup4","simplediff","progressbar","pyinotify","six",
 "pkg_resources","setuptools","pip","wheel","chardet","idna","urllib3","requests",
 "certifi","toml","tomli","packaging","pyparsing","attr","attrs","jinja2","markupsafe",
 "yaml","pyyaml","dateutil","pytz","colorama","distro","appdirs","platformdirs",
 "nlohmann","json","httplib","cpp-httplib","fmt","spdlog","catch2","googletest","gtest",
 "zlib","miniz","stb","tinyxml","pugixml","utf8","xxhash","lz4","zstd","concurrentqueue"}
hits=defaultdict(list)
for rt in sorted(os.listdir(ROOT)):
    if not rt.startswith("Symoneural-"): continue
    srcroot=os.path.join(ROOT,rt,"src")
    if not os.path.isdir(srcroot): continue
    for dp,dn,fn in os.walk(srcroot):
        dn[:]=[d for d in dn if d not in SKIP]
        for d in list(dn):
            if d.lower() in KNOWN:
                p=os.path.join(dp,d)
                rel=os.path.relpath(p,srcroot)
                comp=rel.split(os.sep)[0]
                # only count if it looks like a package/lib, not a random dir
                try: entries=os.listdir(p)
                except OSError: continue
                looks = any(e in ("__init__.py",) for e in entries) or \
                        any(e.endswith((".h",".hpp",".c",".cpp")) for e in entries)
                if not looks: continue
                ver=""
                for f in entries:
                    if f.endswith(".py"):
                        try:
                            t=open(os.path.join(p,f),encoding="utf-8",errors="ignore").read(4000)
                            m=re.search(r'__version__\s*=\s*["\']([^"\']+)',t)
                            if m: ver=m.group(1); break
                        except OSError: pass
                hits[d.lower()].append({"runtime":rt.replace("Symoneural-",""),
                    "component":comp,"path":os.path.relpath(p,ROOT),"version":ver})
json.dump(hits,open(sys.argv[1],"w"),indent=1)
print("=== third-party packages vendored into ORDINARY dirs ===")
for k in sorted(hits):
    for h in hits[k]:
        print("  %-16s %-10s %-12s %s" % (k, h["version"] or "?", h["runtime"], h["path"]))
