# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

SUMMARY = "Client library to download and publish models, datasets and other repos on the huggingface.co hub"
HOMEPAGE = "https://github.com/huggingface/huggingface_hub"
# NOTE: License in setup.py/PKGINFO is: Apache-2.0
# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/huggingface-hub"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

SRC_URI = "git://github.com/huggingface/huggingface_hub;protocol=https;branch=v1.31-release"

# Modify these as desired
# PV is the real upstream release tag at SRCREV, not recipetool's "1.0+git"
# placeholder. The placeholder is not merely cosmetic: it names every .ipk
# <pkg>_1.0+git-r0, and symoneural-pristine exports it as the wheel version
# via *_PRETEND_VERSION/*_BYPASS, where uv-dynamic-versioning parsed it and
# died with IndexError on int(parts[index]).
PV = "1.31.0"
SRCREV = "495b17c8529614759ae0f1ccf1ebe9a61c148b7c"

inherit setuptools3

# WARNING: the following rdepends are determined through basic analysis of the
# python sources, and might not be 100% accurate.
RDEPENDS:${PN} += "python3-core"

# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    PIL
#    _pytest.fixtures
#    _pytest.monkeypatch
#    _pytest.skipping
#    argparse
#    asyncio
#    base64
#    click
#    click.testing
#    collections.abc
#    concurrent.futures
#    contextlib
#    copy
#    dataclasses
#    datetime
#    enum
#    fastapi
#    fastapi.testclient
#    filelock
#    fsspec
#    gradio
#    hashlib
#    hf_xet
#    http.server
#    httpx
#    huggingface_hub
#    huggingface_hub._buckets
#    huggingface_hub._commit_api
#    huggingface_hub._commit_scheduler
#    huggingface_hub._dataset_viewer
#    huggingface_hub._inference_endpoints
#    huggingface_hub._jobs_api
#    huggingface_hub._local_folder
#    huggingface_hub._login
#    huggingface_hub._oauth
#    huggingface_hub._sandbox
#    huggingface_hub._sandbox_cache
#    huggingface_hub._snapshot_download
#    huggingface_hub._space_api
#    huggingface_hub._tree_cache
#    huggingface_hub._upload_large_folder
#    huggingface_hub._upload_pipeline
#    huggingface_hub._webhooks_server
#    huggingface_hub.cli
#    huggingface_hub.cli._cli_utils
#    huggingface_hub.cli._errors
#    huggingface_hub.cli._framework
#    huggingface_hub.cli._output
#    huggingface_hub.cli.cache
#    huggingface_hub.cli.download
#    huggingface_hub.cli.hf
#    huggingface_hub.cli.inference_endpoints
#    huggingface_hub.cli.jobs
#    huggingface_hub.cli.skills
#    huggingface_hub.cli.upload
#    huggingface_hub.community
#    huggingface_hub.constants
#    huggingface_hub.dataclasses
#    huggingface_hub.errors
#    huggingface_hub.file_download
#    huggingface_hub.hf_api
#    huggingface_hub.hf_file_system
#    huggingface_hub.hub_mixin
#    huggingface_hub.inference._common
#    huggingface_hub.inference._generated.types
#    huggingface_hub.inference._generated.types.base
#    huggingface_hub.inference._providers
#    huggingface_hub.inference._providers._common
#    huggingface_hub.inference._providers.cohere
#    huggingface_hub.inference._providers.deepinfra
#    huggingface_hub.inference._providers.fal_ai
#    huggingface_hub.inference._providers.featherless_ai
#    huggingface_hub.inference._providers.fireworks_ai
#    huggingface_hub.inference._providers.groq
#    huggingface_hub.inference._providers.hf_inference
#    huggingface_hub.inference._providers.novita
#    huggingface_hub.inference._providers.nscale
#    huggingface_hub.inference._providers.openai
#    huggingface_hub.inference._providers.ovhcloud
#    huggingface_hub.inference._providers.publicai
#    huggingface_hub.inference._providers.replicate
#    huggingface_hub.inference._providers.scaleway
#    huggingface_hub.inference._providers.together
#    huggingface_hub.inference._providers.wavespeed
#    huggingface_hub.inference._providers.zai_org
#    huggingface_hub.lfs
#    huggingface_hub.repocard
#    huggingface_hub.repocard_data
#    huggingface_hub.serialization
#    huggingface_hub.serialization._base
#    huggingface_hub.serialization._dduf
#    huggingface_hub.serialization._torch
#    huggingface_hub.utils
#    huggingface_hub.utils._auth
#    huggingface_hub.utils._cache_manager
#    huggingface_hub.utils._chunk_utils
#    huggingface_hub.utils._deprecation
#    huggingface_hub.utils._dotenv
#    huggingface_hub.utils._git_credential
#    huggingface_hub.utils._headers
#    huggingface_hub.utils._http
#    huggingface_hub.utils._lfs
#    huggingface_hub.utils._oauth_device
#    huggingface_hub.utils._pagination
#    huggingface_hub.utils._parsing
#    huggingface_hub.utils._runtime
#    huggingface_hub.utils._telemetry
#    huggingface_hub.utils._terminal
#    huggingface_hub.utils._typing
#    huggingface_hub.utils._verification
#    huggingface_hub.utils._xet
#    huggingface_hub.utils._xet_progress_reporting
#    huggingface_hub.utils.endpoint_helpers
#    huggingface_hub.utils.sha
#    huggingface_hub.utils.tqdm
#    inspect
#    io
#    jedi
#    json
#    logging
#    multiprocessing
#    multiprocessing.pool
#    numpy
#    os
#    pathlib
#    pickle
#    pytest
#    pytest_mock
#    queue
#    re
#    safetensors.torch
#    shlex
#    shutil
#    socket
#    starlette.datastructures
#    stat
#    string
#    struct
#    subprocess
#    tempfile
#    threading
#    torch
#    torch.distributed
#    torch.distributed.device_mesh
#    torch.distributed.tensor
#    torch.nn
#    torch.testing._internal.two_tensor
#    torch.utils._python_dispatch
#    tqdm.auto
#    types
#    typing
#    unittest
#    unittest.mock
#    urllib.parse
#    utils.generate_cli_reference
#    uuid
#    warnings
#    weakref
#    yaml
#    zipfile
