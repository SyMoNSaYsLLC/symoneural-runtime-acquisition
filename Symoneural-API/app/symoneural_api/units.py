"""The unit registry — what the rack is, and what each surface reports.

A "unit" is one addressable surface on the rack. The registry is the single
place that knows which exist, what resource each needs, and which estate
packages back it. Nothing else hardcodes a unit name.

Resource class matters because this estate runs on ONE card. Two GPU units
cannot both hold weights in 15.92 GiB, so the lock hands the GPU to exactly one
at a time. CPU and NET units never queue for it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Resource(enum.StrEnum):
    GPU = "GPU"      # queues for the single-card lock
    CPU = "CPU"      # never queues
    NET = "NET"      # I/O bound, never queues


class UnitState(enum.StrEnum):
    READY = "READY"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    QUEUED = "QUEUED"
    UNCONFIGURED = "UNCONFIGURED"


@dataclass(frozen=True, slots=True)
class Unit:
    name: str
    resource: Resource
    port: int
    backed_by: tuple[str, ...]      # estate packages this unit requires
    token_env: str
    height: int = 1                 # rack units, for the rack display
    description: str = ""
    enabled_env: str = ""

    @property
    def enabled_variable(self) -> str:
        return self.enabled_env or f"SYM_{self.name.upper()}_ENABLED"


REGISTRY: dict[str, Unit] = {
    u.name: u
    for u in (
        Unit(
            name="ravencalc",
            resource=Resource.CPU,
            port=8801,
            backed_by=("symoneural-sympy", "symoneural-mpmath", "symoneural-numpy",
                       "symoneural-scipy", "symoneural-scikit-learn", "symoneural-openblas"),
            token_env="SYM_RAVENCALC_TOKEN",
            description="Symbolic algebra and numeric solving. CPU only - it is "
                        "the one unit that never waits for the GPU.",
        ),
        Unit(
            name="chat",
            resource=Resource.GPU,
            port=8802,
            backed_by=("symoneural-llama-cpp",),
            token_env="SYM_CHAT_TOKEN",
            description="Text inference via llama-server. Holds the GPU lock "
                        "while a weight set is resident.",
        ),
        Unit(
            name="coder",
            resource=Resource.CPU,
            port=8803,
            backed_by=("symoneural-mcp-python-sdk", "symoneural-anthropic-sdk-python"),
            token_env="SYM_CODER_TOKEN",
            description="Agent surface speaking MCP. CPU: it orchestrates, it "
                        "does not infer locally.",
        ),
        Unit(
            name="project",
            resource=Resource.CPU,
            port=8804,
            backed_by=("symoneural-fastapi", "symoneural-pydantic"),
            token_env="SYM_PROJECT_TOKEN",
            description="Project and task state.",
        ),
        Unit(
            name="streamer",
            resource=Resource.NET,
            port=8805,
            backed_by=("symoneural-gstreamer", "symoneural-hlsjs"),
            token_env="SYM_STREAMER_TOKEN",
            description="HLS segmenting and delivery. NET: bounded by I/O.",
        ),
        Unit(
            name="remix",
            resource=Resource.NET,
            port=8806,
            backed_by=("symoneural-librespot",),
            token_env="SYM_REMIX_TOKEN",
            description="Spotify Connect endpoint.",
        ),
        Unit(
            name="studio",
            resource=Resource.GPU,
            port=8807,
            backed_by=("symoneural-pytorch", "symoneural-transformers",
                       "symoneural-accelerate", "symoneural-safetensors"),
            token_env="SYM_STUDIO_TOKEN",
            description="Fine-tuning and adapter training. Queues for the GPU.",
        ),
        Unit(
            name="miner",
            resource=Resource.GPU,
            port=8808,
            backed_by=("symoneural-stratum", "symoneural-sv2-apps"),
            token_env="SYM_MINER_TOKEN",
            height=6,
            description="Stratum V2 mining. Yields the lock to any interactive "
                        "unit - revenue never outranks a waiting user.",
        ),
        Unit(
            name="image",
            resource=Resource.GPU,
            port=8809,
            backed_by=("symoneural-stable-diffusion-cpp",),
            token_env="SYM_IMAGE_TOKEN",
            description="Diffusion rendering via sd-cli. Ties with chat at "
                        "priority 100: someone waiting on a picture is as "
                        "interactive as someone waiting on a sentence.",
        ),
        Unit(
            name="sigils",
            resource=Resource.GPU,
            port=8810,
            backed_by=("symoneural-stable-diffusion-cpp",),
            token_env="SYM_SIGILS_TOKEN",
            description="Second surface on the same engine at priority 90. What "
                        "it renders has no recorded definition anywhere in this "
                        "repository; see docs/diffuse/ARCHITECTURE.md section 1. "
                        "It has a port and a rank, and deliberately no route.",
        ),
    )
}


def unit(name: str) -> Unit:
    try:
        return REGISTRY[name]
    except KeyError:
        raise KeyError(f"unknown unit {name!r}; known: {sorted(REGISTRY)}") from None


def gpu_units() -> list[Unit]:
    """Units that contend for the single card, in rack order."""
    return [u for u in REGISTRY.values() if u.resource is Resource.GPU]


def backing_packages() -> dict[str, tuple[str, ...]]:
    """unit -> the estate packages it needs installed to be more than a stub.

    This is what makes 'unit X is offline' checkable rather than asserted: if a
    backing package has no ipk, the unit cannot be READY however it is flagged.
    """
    return {u.name: u.backed_by for u in REGISTRY.values()}
