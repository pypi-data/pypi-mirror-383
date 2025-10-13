from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from . import base_namespace


class RouterSIO:
    """A lightweight router for organizing Socket.IO event handlers.

    This provides a FastAPI-like developer experience for grouping and
    including handlers. Handlers registered on the router can later be
    attached to a server via ``sio.add_router(router)``.

    Example:
        router = RouterSIO(namespace="/chat")

        @router.on("message")
        async def handle_message(sid: SocketID, data: Data):
            ...

        sio.add_router(router)
    """

    def __init__(self, namespace: Optional[str] = None) -> None:
        # Default namespace applied when not provided explicitly in .on()/@event
        self.default_namespace: str = namespace or "/"
        # Decorator-based function handlers: {namespace: {event: handler}}
        self.handlers: Dict[str, Dict[str, Callable[..., Any]]] = {}
        # Class-based namespace handlers to be registered on the server
        self._namespace_handlers: List[base_namespace.BaseServerNamespace] = []

    # Public API mirrors Server.on
    def on(
        self,
        event: str,
        handler: Optional[Callable[..., Any]] = None,
        namespace: Optional[str] = None,
        *,
        response_model: Optional[Union[Any, Dict[str, Any]]] = None,
        channel: Optional[str] = None,
        # asyncapi_from_ast: bool = False,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        ns = namespace or self.default_namespace

        def set_handler(h: Callable[..., Any]) -> Callable[..., Any]:
            if ns not in self.handlers:
                self.handlers[ns] = {}
            # Set AsyncAPI-related metadata and response validation on function
            eff_resp_model = response_model
            if eff_resp_model is not None:
                try:
                    # Validate response_model structure
                    if isinstance(eff_resp_model, dict):
                        # Validate that all values are Pydantic models or valid types
                        for event_name, model in eff_resp_model.items():
                            if not isinstance(event_name, str):
                                raise ValueError(
                                    f"response_model keys must be strings, got {type(event_name)}"
                                )
                            # Check if it's a Pydantic model (basic check)
                            if hasattr(model, "__bases__"):
                                try:
                                    # Import Pydantic BaseModel locally to avoid import issues
                                    from pydantic import BaseModel as _PydanticBaseModel

                                    if not (
                                        isinstance(model, type)
                                        and issubclass(model, _PydanticBaseModel)
                                    ):
                                        raise ValueError(
                                            f"response_model['{event_name}'] must be a Pydantic BaseModel, got {type(model)}"
                                        )
                                except ImportError:
                                    # If Pydantic is not available, skip validation
                                    pass

                    h._fastsio_response_model = eff_resp_model
                except Exception:
                    pass
            if channel is not None:
                try:
                    h._fastsio_channel_override = channel
                except Exception:
                    pass
            self.handlers[ns][event] = h
            return h

        if handler is None:
            return set_handler
        set_handler(handler)
        return set_handler

    # Convenience decorator mirrors Server.event
    def event(
        self, *args: Any, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # invoked without arguments: @router.event
            return self.on(args[0].__name__)(args[0])

        # invoked with arguments: @router.event(namespace="...")
        def set_handler(h: Callable[..., Any]) -> Callable[..., Any]:
            return self.on(h.__name__, *args, **kwargs)(h)

        return set_handler

    def register_namespace(
        self, namespace_handler: base_namespace.BaseServerNamespace
    ) -> None:
        """Queue a class-based namespace handler for registration.

        The actual registration occurs when the router is attached to a server
        via ``sio.add_router(router)``.
        """
        if not isinstance(namespace_handler, base_namespace.BaseServerNamespace):  # type: ignore[redundant-expr]
            raise ValueError("Not a namespace instance")
        self._namespace_handlers.append(namespace_handler)

    # Internal helpers used by the server when attaching the router
    def iter_function_handlers(self) -> List[Tuple[str, str, Callable[..., Any]]]:
        out: List[Tuple[str, str, Callable[..., Any]]] = []
        for ns, events in self.handlers.items():
            for event, handler in events.items():
                out.append((ns, event, handler))
        return out

    def iter_namespace_handlers(self) -> List[base_namespace.BaseServerNamespace]:
        return list(self._namespace_handlers)
