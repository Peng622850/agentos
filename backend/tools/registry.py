from typing import Callable

_registry: dict[str, Callable] = {}

def register(name: str):
    def decorator(fn: Callable):
        _registry[name] = fn
        return fn
    return decorator

def get_tool(name: str) -> Callable:
    return _registry.get(name)

def list_tools() -> list[str]:
    return list(_registry.keys())