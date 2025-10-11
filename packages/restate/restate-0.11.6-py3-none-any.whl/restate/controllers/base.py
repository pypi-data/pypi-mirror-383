from __future__ import annotations
from typing import Generic, TypeVar
from random import Random
from uuid import UUID

from typing_extensions import (
    Any,
    Callable,
    Self,
)

from pathlib import PurePosixPath as Path

from restate.shared.constants import ROOT_PATH


_T = TypeVar("_T")


class BaseController:
    def __init__(self):
        self.callbacks: CallbackStore = CallbackStore()

    def get_temporary_path(self, key: str | None = None) -> Path:
        root = ROOT_PATH
        rng = Random(key)
        return root / "tmp" / UUID(bytes=rng.randbytes(16)).hex

    def resolve_path(self, path: PathLike) -> Path:
        while not isinstance(path, Path):
            if isinstance(path, str):
                if not path:
                    path = "/"

                path = Path(path)
            else:
                path = path.path

        if path.parts[:1] != ("/"):
            path = Path("/") / path

        return path

    def register_callback(
        self,
        callback: StateCallback[Self],
        force_id: CallbackID | None = None,
        replace: bool = False,
    ):
        """
        Registers a callback for further use. A part of register-subscribe process.
        You may also use .subscribe method directly if you have both path and callback on hands.
        Returns the callback_id to be used in subscriptions.

        Pass a string force_id to set a specific callback_id.
        If `replace=False`, passing a different callback with the same force_id will result in an error.
        Pass `replace=True` if you intend to overwrite the callback.
        """

        return self.callbacks.add_callback(callback, force_id, replace)

    def subscribe_by_id(
        self,
        path: PathLike,
        callback_id: CallbackID,
        ignore_missing: bool = False,
    ) -> CallbackID:
        """
        Pass a callback_id instead of a real callback.
        Allows to decouple callback creation and subscription.

        If called before callback creation, will raise errors unless `ignore_missing=True`
        """
        self.callbacks.subscribe(
            path=self.resolve_path(path),
            callback_id=callback_id,
            ignore_missing=ignore_missing,
        )

        return callback_id

    def subscribe(
        self,
        path: PathLike,
        callback: StateCallback[Self],
        force_id: CallbackID | None = None,
        replace: bool = False,
    ) -> CallbackID:
        """
        Subscribes a callback to every path update (including all bubbling updates of child paths).
        To subscribe with a callback_id, use .subscribe_by_id.
        To get a callback_id without any subscriptions, use .register_callback

        Pass a string force_id to set a specific callback_id.
        If `replace=False`, passing a different callback with the same force_id will result in an error.
        Pass `replace=True` if you intend to overwrite the callback.
        """

        callback_id = self.register_callback(callback, force_id, replace)
        self.subscribe_by_id(path, callback_id)
        return callback_id

    def unsubscribe_by_id(
        self,
        path: PathLike,
        callback_id: CallbackID,
    ):
        """
        Remove a subscription for the given path and callback_id
        """
        self.callbacks.unsubscribe(self.resolve_path(path), callback_id)

    def unsubscribe(
        self,
        path: PathLike,
        callback: StateCallback[Self],
    ):
        """
        Remove a subscription for the given path and callback
        """
        callback_id = self.callbacks.get_id(callback)
        self.unsubscribe_by_id(path, callback_id)

    def build_event(
        self,
        path: PathLike,
        prev_value: _T | None,
        new_value: _T | None,
        payload: Any,
    ) -> StateEvent[Self, _T]:
        path = self.resolve_path(path)

        return StateEvent(
            controller=self,
            emitting_path=path,
            current_path=path,
            prev_value=prev_value,
            new_value=new_value,
            payload=payload,
        )

    def get_state(
        self,
        path: PathLike,
        default: Any | None = None,
        write_default: bool = False,
    ) -> Any: ...

    def set_state(
        self,
        path: PathLike,
        value: Any | None,
        eq_func: Callable[[Any | None, Any | None], bool] | None = None,
        default: Any | None = None,
        payload: Any = None,
        skip_notify: bool = False,
    ) -> bool: ...

    def del_state(
        self,
        path: PathLike,
        payload: Any = None,
        skip_notify: bool = False,
    ) -> bool: ...


class DeriveData:
    def __init__(self, controller: BaseController, data: dict[Path, Any]):
        self.controller = controller
        self.data = {self.controller.resolve_path(p): v for p, v in data.items()}

    def get(self, path: PathLike) -> Any | None:
        path = self.controller.resolve_path(path)

        return self.data.get(path)

    def __getattr__(self, attr: str):
        return self.get(attr)


_C = TypeVar("_C", bound=BaseController)


class BaseAtom(Generic[_C, _T]):
    default: _T
    path: PathLike
    controller: _C

    def __init__(
        self,
        controller: _C,
        path: PathLike | None = None,
        key: str | None = None,
        default: _T = None,
    ) -> None:
        self.default = default
        self.controller = controller

        if path is None:
            path = controller.get_temporary_path(key)

        self.path = path


from .internal_types import PathLike, StateCallback, StateEvent  # noqa: E402
from .callback_store import CallbackID, CallbackStore  # noqa: E402
