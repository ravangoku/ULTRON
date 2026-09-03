from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    risk: str
    requires_confirmation: bool
    handler: Callable[[dict[str, Any]], dict[str, Any]]


def calculator(arguments: dict[str, Any]) -> dict[str, Any]:
    expression = arguments.get("expression", "")
    if not expression or any(char not in "0123456789+-*/(). %" for char in expression):
        return {"ok": False, "error": "Calculator accepts only arithmetic symbols and numbers."}
    try:
        return {"ok": True, "result": eval(expression, {"__builtins__": {}}, {})}  # constrained grammar above
    except (ArithmeticError, SyntaxError):
        return {"ok": False, "error": "Invalid arithmetic expression."}


def system_info(_: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "message": "System telemetry is intentionally limited in this Phase 1 API."}


REGISTRY = {
    "calculator": ToolDefinition("calculator", "Evaluate a basic arithmetic expression.", "low", False, calculator),
    "system_info": ToolDefinition("system_info", "Read limited ULTRON service status.", "low", False, system_info),
}


def execute_tool(name: str, arguments: dict[str, Any], confirmed: bool, emergency_stop: bool) -> dict[str, Any]:
    if emergency_stop:
        return {"ok": False, "error": "Emergency stop is active; tool execution is disabled."}
    tool = REGISTRY.get(name)
    if not tool:
        return {"ok": False, "error": "Tool is not registered or not allowed."}
    if tool.requires_confirmation and not confirmed:
        return {"ok": False, "requires_confirmation": True, "preview": tool.description}
    return {"tool": tool.name, "risk": tool.risk, **tool.handler(arguments)}
