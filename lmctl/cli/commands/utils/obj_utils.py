from typing import Dict, Any

__all__ = ('shallow_merge_objs',)

def shallow_merge_objs(first: Dict[str, Any], second: Dict[str, Any]) -> Dict[str, Any]:
    if first is None:
        first = {}
    if second is None:
        second = {}
    first.update(second)
    return first