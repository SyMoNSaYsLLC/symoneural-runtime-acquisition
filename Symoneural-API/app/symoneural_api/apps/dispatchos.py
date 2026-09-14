"""DispatchOS — the first application, registered like any other.

A customer-facing demonstration of the rack: it reads unit readiness and the GPU
lock state through generic APIs and shows them. It requires the ravencalc unit
(CPU, always available) and treats chat as optional, so the page degrades
honestly when the LLM backend is not installed instead of faking a green light.
Public page: /demo/dispatchos.html — served by the UI runtime, backed by
/api/apps/dispatchos.
"""
from ..applications import ApplicationDefinition, DemoPolicy, Mode, register

DISPATCHOS = register(ApplicationDefinition(
    application_id="dispatchos",
    display_name="DispatchOS",
    mode=Mode.DEMO,
    required_units=("ravencalc",),
    optional_units=("chat",),
    allowed_models=(),                       # filled when the model register has a served row
    capabilities=("unit-status", "gpu-lock-status", "ravencalc-compute"),
    public_demo=True,
    page="/demo/dispatchos.html",
    policy=DemoPolicy(
        allowed_models=frozenset(),
        allowed_units=frozenset({"ravencalc", "chat"}),
        allow_mutations=False,
        max_requests_per_minute=30,
        max_concurrent_sessions=4,
        session_lifetime_s=900,
        tool_capabilities=frozenset({"read_status"}),
    ),
))
