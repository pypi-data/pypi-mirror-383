from abc import ABC
from atexit import register
from types import TracebackType
from typing import Any, Self

from xproject.xcall import call_method
from xproject.xmixins.xobject_mixins.xcreate_instance_object_mixin import CreateInstanceObjectMixin


class ContextManagerObjectMixin(CreateInstanceObjectMixin, ABC):
    @classmethod
    def create_instance(cls, *args: Any, auto_call: bool = True, **kwargs: Any) -> Self:
        instance = super().create_instance(*args, **kwargs)
        if auto_call:
            call_method(method=instance._open)
            register(lambda: call_method(method=instance._close))
        return instance

    def __enter__(self) -> Self:
        call_method(method=self._open)
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> None:
        call_method(method=self._close)
