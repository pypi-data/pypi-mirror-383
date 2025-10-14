# fastkafka2\registry.py
import logging
from inspect import signature, iscoroutinefunction
from typing import Any, Callable, get_origin, get_args
from pydantic import BaseModel
from .message import KafkaMessage
from .di.di_container import resolve

__all__ = ["kafka_handler"]

logger = logging.getLogger(__name__)
handlers_registry: dict[str, list["CompiledHandler"]] = {}


class CompiledHandler:
    __slots__ = (
        "topic",
        "func",
        "sig",
        "data_model",
        "headers_model",
        "_headers_predicate",
        "dependencies",
    )

    def __init__(
        self,
        topic: str,
        func: Callable[..., Any],
        data_model: type[BaseModel] | None,
        headers_model: type[BaseModel] | None,
        headers_filter: dict[str, str] | Callable[[dict[str, str]], bool] | None = None,
    ):
        self.topic = topic
        self.func = func
        self.sig = signature(func)
        self.data_model = data_model
        self.headers_model = headers_model

        if headers_filter is None:
            self._headers_predicate = lambda _h: True
        elif callable(headers_filter):
            self._headers_predicate = headers_filter
        else:
            expected: dict[str, str] = headers_filter
            def _eq_predicate(headers: dict[str, str]) -> bool:
                for k, v in expected.items():
                    if headers.get(k) != v:
                        return False
                return True
            self._headers_predicate = _eq_predicate

        self.dependencies: dict[str, Any] = {}
        for name, param in self.sig.parameters.items():
            ann = param.annotation
            origin = get_origin(ann)
            if origin is KafkaMessage or ann in (KafkaMessage, data_model, headers_model):
                continue
            if ann is param.empty:
                continue
            self.dependencies[name] = resolve(param.annotation)

    def matches_headers(self, headers: dict[str, str]) -> bool:
        try:
            return bool(self._headers_predicate(headers))
        except Exception:
            logger.exception("Headers predicate raised for topic %s", self.topic)
            return False

    async def handle(
        self, raw_data: Any, raw_headers: dict[str, str] | None, key: str | None
    ):
        headers_src: dict[str, str] = raw_headers or {}

        msg_data = self.data_model(**raw_data) if self.data_model else raw_data
        msg_headers = (
            self.headers_model(**headers_src) if self.headers_model else headers_src
        )

        message = KafkaMessage(
            topic=self.topic, data=msg_data, headers=msg_headers, key=key
        )

        kwargs: dict[str, Any] = {}
        for name, param in self.sig.parameters.items():
            ann = param.annotation
            origin = get_origin(ann)
            if ann is KafkaMessage or origin is KafkaMessage:
                kwargs[name] = message
            elif self.data_model is not None and ann is self.data_model:
                kwargs[name] = msg_data
            elif self.headers_model is not None and ann is self.headers_model:
                kwargs[name] = msg_headers
            else:
                kwargs[name] = self.dependencies.get(name)

        return await self.func(**kwargs)


def kafka_handler(
    topic: str,
    data_model: type[BaseModel] | None = None,
    headers_model: type[BaseModel] | None = None,
    headers_filter: dict[str, str] | Callable[[dict[str, str]], bool] | None = None,
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not iscoroutinefunction(func):
            raise TypeError("Handler must be async")
        dm = data_model
        hm = headers_model
        if dm is None or hm is None:
            sig = signature(func)
            for param in sig.parameters.values():
                ann = param.annotation
                origin = get_origin(ann)
                if origin is KafkaMessage:
                    args = get_args(ann)
                    if dm is None and len(args) >= 1:
                        try:
                            if isinstance(args[0], type) and issubclass(args[0], BaseModel):
                                dm = args[0]
                        except Exception:
                            pass
                    if hm is None and len(args) >= 2:
                        try:
                            if isinstance(args[1], type) and issubclass(args[1], BaseModel):
                                hm = args[1]
                        except Exception:
                            pass
            if dm is None or hm is None:
                found: list[type[BaseModel]] = []
                for param in sig.parameters.values():
                    ann = param.annotation
                    try:
                        if isinstance(ann, type) and issubclass(ann, BaseModel):
                            found.append(ann)
                    except Exception:
                        continue
                if dm is None and len(found) >= 1:
                    dm = found[0]
                if hm is None and len(found) >= 2:
                    hm = found[1]

        handlers_registry.setdefault(topic, []).append(
            CompiledHandler(topic, func, dm, hm, headers_filter)
        )
        logger.debug(
            "Registered handler %s for topic %s (data_model=%s, headers_model=%s)",
            func.__name__,
            topic,
            getattr(dm, "__name__", None),
            getattr(hm, "__name__", None),
        )
        return func

    return decorator
