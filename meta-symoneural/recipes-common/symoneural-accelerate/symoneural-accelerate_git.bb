# Recipe created by recipetool
# This is the basis of a recipe and may need further editing in order to be fully functional.
# (Feel free to remove these comments when editing.)

SUMMARY = "Accelerate"
HOMEPAGE = "https://github.com/huggingface/accelerate"
# NOTE: License in setup.py/PKGINFO is: Apache
# WARNING: the following LICENSE and LIC_FILES_CHKSUM values are best guesses - it is
# your responsibility to verify that the values are complete and correct.
# NOTE: Original package / source metadata indicates license is: Apache
#
# NOTE: multiple licenses have been detected; they have been separated with &
# in the LICENSE value for now since it is a reasonable assumption that all
# of the licenses apply. If instead there is a choice between the multiple
# licenses then you should change the value to separate the licenses with |
# instead of &. If there is any doubt, check the accompanying documentation
# to determine which situation is applicable.
# LICENSE established from the licence text in the acquired tree. recipetool had
# emitted a non-SPDX token ('Unknown'/'Apache'), which newer OE-Core's SPDX parser
# rejects outright: do_populate_lic dies with
# "AttributeError: 'UnknownId' object has no attribute 'name'".
# Built by symoneural-pristine: a DISPOSABLE `git archive` export of the
# acquired tree. ${S} is throwaway; the acquired tree is never written to.
# do_unpack asserts the tree HEAD equals SRCREV and refuses to build otherwise.
inherit symoneural-pristine
SYMON_TREE = "/home/google/SymonSaysLLC/Symoneural-Common/src/ml/source/accelerate"

LICENSE = "Apache-2.0"
LIC_FILES_CHKSUM = "file://LICENSE;md5=86d3f3a95c324c9479bd8986968f4327"

SRC_URI = "git://github.com/huggingface/accelerate;protocol=https;branch=v1.15.0-release"

# Modify these as desired
PV = "1.15.0+git"
SRCREV = "6afc1e5ee217051fde702b23de2813344dc0fd33"

inherit setuptools3

# WARNING: the following rdepends are from setuptools install_requires. These
# upstream names may not correspond exactly to bitbake package names.
RDEPENDS:${PN} += "python3-huggingface_hub python3-numpy python3-packaging python3-psutil python3-pyyaml python3-safetensors python3-torch"

# WARNING: the following rdepends are determined through basic analysis of the
# python sources, and might not be 100% accurate.
RDEPENDS:${PN} += "python3-core"

# WARNING: We were unable to map the following python package/module
# dependencies to the bitbake packages which include them:
#    accelerate
#    accelerate.accelerator
#    accelerate.big_modeling
#    accelerate.commands.config.config_args
#    accelerate.commands.env
#    accelerate.commands.estimate
#    accelerate.commands.launch
#    accelerate.commands.test
#    accelerate.commands.to_fsdp2
#    accelerate.commands.tpu
#    accelerate.data_loader
#    accelerate.hooks
#    accelerate.logging
#    accelerate.parallelism_config
#    accelerate.state
#    accelerate.test_utils
#    accelerate.test_utils.examples
#    accelerate.test_utils.scripts.external_deps
#    accelerate.test_utils.testing
#    accelerate.test_utils.training
#    accelerate.tracking
#    accelerate.utils
#    accelerate.utils.ao
#    accelerate.utils.bnb
#    accelerate.utils.constants
#    accelerate.utils.dataclasses
#    accelerate.utils.imports
#    accelerate.utils.launch
#    accelerate.utils.memory
#    accelerate.utils.modeling
#    accelerate.utils.operations
#    accelerate.utils.other
#    accelerate.utils.random
#    accelerate.utils.versions
#    argparse
#    ast
#    bitsandbytes
#    bitsandbytes.nn
#    clearml
#    clearml.config
#    clearml.utilities.config
#    collections
#    comet_ml
#    contextlib
#    copy
#    csv
#    dataclasses
#    datasets
#    dvclive.plots.metric
#    dvclive.serialize
#    dvclive.utils
#    functools
#    huggingface_hub.utils
#    import_timer
#    import_timer.core
#    importlib
#    inspect
#    json
#    logging
#    matplotlib.pyplot
#    mlflow
#    os
#    pandas
#    parameterized
#    pathlib
#    pickle
#    pytest
#    random
#    re
#    safetensors.torch
#    shutil
#    struct
#    subprocess
#    swanlab
#    swanlab.log.backup
#    swanlab.log.backup.datastore
#    swanlab.log.backup.models
#    tempfile
#    tensorboard.compat.proto
#    textwrap
#    torch.distributed._composable.fsdp
#    torch.distributed._tensor
#    torch.distributed.algorithms._checkpoint.checkpoint_wrapper
#    torch.distributed.device_mesh
#    torch.distributed.fsdp.wrap
#    torch.fx
#    torch.nested
#    torch.nn
#    torch.nn.parallel
#    torch.utils.benchmark
#    torch.utils.data
#    torch_xla
#    torch_xla.distributed.spmd
#    torch_xla.distributed.xla_multiprocessing
#    torch_xla.experimental.spmd_fully_sharded_data_parallel
#    torch_xla.runtime
#    torchao.float8.float8_linear
#    torchdata.stateful_dataloader
#    transformers
#    transformers.integrations.bitsandbytes
#    transformers.models.gpt2.modeling_gpt2
#    types
#    typing
#    unittest
#    unittest.mock
#    uuid
#    warnings
#    weakref
#    zipfile
