from importlib.metadata import PackageNotFoundError, version

from .app import KafkaApp
from .handler import KafkaHandler
from .message import KafkaMessage
from .producer import KafkaProducer

__all__ = ["KafkaApp", "KafkaHandler", "KafkaMessage", "KafkaProducer"]

try:
    __version__ = version("fastkafka2")
except PackageNotFoundError:
    __version__ = "0.0.0"


def __getattr__(name: str):
    if name in __all__:
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name}")


def __dir__():
    return __all__ + [n for n in globals() if n.startswith("_")]
