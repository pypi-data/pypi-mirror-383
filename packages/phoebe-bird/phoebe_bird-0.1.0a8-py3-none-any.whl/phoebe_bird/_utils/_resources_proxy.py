from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `phoebe_bird.resources` module.

    This is used so that we can lazily import `phoebe_bird.resources` only when
    needed *and* so that users can just import `phoebe_bird` and reference `phoebe_bird.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("phoebe_bird.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
