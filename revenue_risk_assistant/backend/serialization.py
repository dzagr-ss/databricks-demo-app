from typing import Any


def to_dict(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    if hasattr(obj, "as_dict"):
        return to_dict(obj.as_dict())
    if hasattr(obj, "__dict__"):
        return {key: to_dict(value) for key, value in obj.__dict__.items() if not key.startswith("_")}
    return str(obj)
