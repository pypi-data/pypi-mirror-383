from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("udp_pinger")
except PackageNotFoundError:
    __version__ = "0.0.0"

from importlib import import_module


def __getattr__(name: str):
    core = import_module(f"{__name__}._udp_pinger_core")
    if hasattr(core, name):
        return getattr(core, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    core = import_module(f"{__name__}._udp_pinger_core")
    return sorted(set(globals().keys()) | set(dir(core)))
