# abagentsdk/__init__.py
from __future__ import annotations

# (optional) silence native/grpc/absl noise early if you have this helper
try:
    from .utils.silence import install_silence  # noqa: F401
    install_silence()
except Exception:
    pass

# ---- Core API (safe imports; avoid circulars) ----
from .core.agent import Agent, AgentResult  # noqa: F401
from .core.memory import Memory  # noqa: F401
from .core.tools import Tool, ToolCall, FunctionTool, function_tool  # noqa: F401

# ---- Optional: Handoffs (guard with try to avoid circulars if missing) ----
try:
    from .core.handoffs import Handoff, handoff, RunContextWrapper  # noqa: F401
except Exception:
    Handoff = handoff = RunContextWrapper = None  # type: ignore

# ---- Optional: Guardrails (export only if present) ----
try:
    from .core.guardrails import (  # noqa: F401
        input_guardrail,
        output_guardrail,
        GuardrailFunctionOutput,
        InputGuardrailTripwireTriggered,
        OutputGuardrailTripwireTriggered,
    )
except Exception:
    input_guardrail = output_guardrail = GuardrailFunctionOutput = None  # type: ignore
    InputGuardrailTripwireTriggered = OutputGuardrailTripwireTriggered = None  # type: ignore

# ---- Version ----
try:
    from importlib.metadata import version as _pkg_version, PackageNotFoundError  # type: ignore
    try:
        __version__ = _pkg_version("abagentsdk")
    except PackageNotFoundError:  # local editable installs
        __version__ = "0.0.0"
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    # Core
    "Agent", "AgentResult", "Memory",
    # Tools
    "Tool", "ToolCall", "FunctionTool", "function_tool",
    # Handoffs (optional)
    "Handoff", "handoff", "RunContextWrapper",
    # Guardrails (optional)
    "input_guardrail", "output_guardrail",
    "GuardrailFunctionOutput",
    "InputGuardrailTripwireTriggered", "OutputGuardrailTripwireTriggered",
]
