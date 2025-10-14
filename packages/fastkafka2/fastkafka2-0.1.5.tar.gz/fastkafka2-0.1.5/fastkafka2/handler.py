# fastkafka2\handler.py
import logging
from typing import Callable, Any
from .registry import kafka_handler

logger = logging.getLogger(__name__)


class KafkaHandler:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix

    def __call__(
        self,
        topic: str,
        data_model: Any = None,
        headers_model: Any = None,
        headers_filter: Any | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        full_topic = f"{self.prefix}.{topic}" if self.prefix else topic
        return kafka_handler(full_topic, data_model, headers_model, headers_filter)

    def include_handler(self, other: "KafkaHandler") -> None:
        self.prefix += f".{other.prefix}" if other.prefix else ""
