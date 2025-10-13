import asyncio
import inspect
from collections.abc import Coroutine

# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownVariableType=false, reportUnknownParameterType=false
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Union,
)

import engineio

from . import async_manager, base_server, exceptions, packet
from .dependency import run_with_context

if TYPE_CHECKING:  # pragma: no cover
    from .async_admin import InstrumentedAsyncServer

# this set is used to keep references to background tasks to prevent them from
# being garbage collected mid-execution. Solution taken from
# https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
task_reference_holder: Set[asyncio.Task[Any]] = set()


class AsyncServer(base_server.BaseServer):
    # Attribute type hints to aid static type checkers
    manager: Any
    eio: engineio.AsyncServer
    packet_class: Any
    handlers: Dict[str, Dict[str, Any]]
    namespace_handlers: Dict[str, Any]
    namespaces: Union[List[str], str]
    environ: Dict[str, Any]
    _binary_packet: Dict[str, Any]
    """A Socket.IO server for asyncio.

    This class implements a fully compliant Socket.IO web server with support
    for websocket and long-polling transports, compatible with the asyncio
    framework.

    :param client_manager: The client manager instance that will manage the
                           client list. When this is omitted, the client list
                           is stored in an in-memory structure, so the use of
                           multiple connected servers is not possible.
    :param logger: To enable logging set to ``True`` or pass a logger object to
                   use. To disable logging set to ``False``. Note that fatal
                   errors are logged even when ``logger`` is ``False``.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have ``dumps`` and ``loads``
                 functions that are compatible with the standard library
                 versions.
    :param async_handlers: If set to ``True``, event handlers for a client are
                           executed in separate threads. To run handlers for a
                           client synchronously, set to ``False``. The default
                           is ``True``.
    :param always_connect: When set to ``False``, new connections are
                           provisory until the connect handler returns
                           something other than ``False``, at which point they
                           are accepted. When set to ``True``, connections are
                           immediately accepted, and then if the connect
                           handler returns ``False`` a disconnect is issued.
                           Set to ``True`` if you need to emit events from the
                           connect handler and your client is confused when it
                           receives events before the connection acceptance.
                           In any other case use the default of ``False``.
    :param namespaces: a list of namespaces that are accepted, in addition to
                       any namespaces for which handlers have been defined. The
                       default is `['/']`, which always accepts connections to
                       the default namespace. Set to `'*'` to accept all
                       namespaces.
    :param kwargs: Connection parameters for the underlying Engine.IO server.

    The Engine.IO configuration supports the following settings:

    :param async_mode: The asynchronous model to use. See the Deployment
                       section in the documentation for a description of the
                       available options. Valid async modes are "aiohttp",
                       "sanic", "tornado" and "asgi". If this argument is not
                       given, "aiohttp" is tried first, followed by "sanic",
                       "tornado", and finally "asgi". The first async mode that
                       has all its dependencies installed is the one that is
                       chosen.
    :param ping_interval: The interval in seconds at which the server pings
                          the client. The default is 25 seconds. For advanced
                          control, a two element tuple can be given, where
                          the first number is the ping interval and the second
                          is a grace period added by the server.
    :param ping_timeout: The time in seconds that the client waits for the
                         server to respond before disconnecting. The default
                         is 20 seconds.
    :param max_http_buffer_size: The maximum size that is accepted for incoming
                                 messages.  The default is 1,000,000 bytes. In
                                 spite of its name, the value set in this
                                 argument is enforced for HTTP long-polling and
                                 WebSocket connections.
    :param allow_upgrades: Whether to allow transport upgrades or not. The
                           default is ``True``.
    :param http_compression: Whether to compress packages when using the
                             polling transport. The default is ``True``.
    :param compression_threshold: Only compress messages when their byte size
                                  is greater than this value. The default is
                                  1024 bytes.
    :param cookie: If set to a string, it is the name of the HTTP cookie the
                   server sends back to the client containing the client
                   session id. If set to a dictionary, the ``'name'`` key
                   contains the cookie name and other keys define cookie
                   attributes, where the value of each attribute can be a
                   string, a callable with no arguments, or a boolean. If set
                   to ``None`` (the default), a cookie is not sent to the
                   client.
    :param cors_allowed_origins: Origin or list of origins that are allowed to
                                 connect to this server. Only the same origin
                                 is allowed by default. Set this argument to
                                 ``'*'`` to allow all origins, or to ``[]`` to
                                 disable CORS handling.
    :param cors_credentials: Whether credentials (cookies, authentication) are
                             allowed in requests to this server. The default is
                             ``True``.
    :param monitor_clients: If set to ``True``, a background task will ensure
                            inactive clients are closed. Set to ``False`` to
                            disable the monitoring task (not recommended). The
                            default is ``True``.
    :param transports: The list of allowed transports. Valid transports
                       are ``'polling'`` and ``'websocket'``. Defaults to
                       ``['polling', 'websocket']``.
    :param engineio_logger: To enable Engine.IO logging set to ``True`` or pass
                            a logger object to use. To disable logging set to
                            ``False``. The default is ``False``. Note that
                            fatal errors are logged even when
                            ``engineio_logger`` is ``False``.
    """

    def __init__(
        self,
        client_manager: Optional[async_manager.AsyncManager] = None,
        logger: Union[bool, Any] = False,
        json: Optional[Any] = None,
        async_handlers: bool = True,
        namespaces: Optional[Union[List[str], str]] = None,
        **kwargs: Any,
    ) -> None:
        if client_manager is None:
            client_manager = async_manager.AsyncManager()
        super().__init__(
            client_manager=client_manager,
            logger=logger,
            json=json,
            async_handlers=async_handlers,
            namespaces=namespaces,
            **kwargs,
        )
        # attributes are provided by the base class; runtime types are ensured

    def is_asyncio_based(self):  # type: ignore[override]
        return True

    def attach(self, app: Any, socketio_path: str = "socket.io") -> None:
        """Attach the Socket.IO server to an application."""
        self.eio.attach(app, socketio_path)

    async def emit(
        self,
        event: str,
        data: Optional[Any] = None,
        to: Optional[Union[str, List[str]]] = None,
        room: Optional[Union[str, List[str]]] = None,
        skip_sid: Optional[Union[str, List[str]]] = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable[..., Any]] = None,
        ignore_queue: bool = False,
    ) -> None:
        """Emit a custom event to one or more connected clients.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param to: The recipient of the message. This can be set to the
                   session ID of a client to address only that client, to any
                   any custom room created by the application to address all
                   the clients in that room, or to a list of custom room
                   names. If this argument is omitted the event is broadcasted
                   to all connected clients.
        :param room: Alias for the ``to`` parameter.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             clients directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used. It is recommended
                             to always leave this parameter with its default
                             value of ``False``.

        Note: this method is not designed to be used concurrently. If multiple
        tasks are emitting at the same time to the same client connection, then
        messages composed of multiple packets may end up being sent in an
        incorrect sequence. Use standard concurrency solutions (such as a Lock
        object) to prevent this situation.

        Note 2: this method is a coroutine.
        """
        namespace = namespace or "/"
        room = to or room
        self.logger.info(
            'emitting event "%s" to %s [%s]', event, room or "all", namespace
        )
        await self.manager.emit(
            event,
            data,
            namespace,
            room=room,
            skip_sid=skip_sid,
            callback=callback,
            ignore_queue=ignore_queue,
        )

    async def send(
        self,
        data: Any,
        to: Optional[Union[str, List[str]]] = None,
        room: Optional[Union[str, List[str]]] = None,
        skip_sid: Optional[Union[str, List[str]]] = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable[..., Any]] = None,
        ignore_queue: bool = False,
    ) -> None:
        """Send a message to one or more connected clients.

        This function emits an event with the name ``'message'``. Use
        :func:`emit` to issue custom event names.

        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param to: The recipient of the message. This can be set to the
                   session ID of a client to address only that client, to any
                   any custom room created by the application to address all
                   the clients in that room, or to a list of custom room
                   names. If this argument is omitted the event is broadcasted
                   to all connected clients.
        :param room: Alias for the ``to`` parameter.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             clients directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used. It is recommended
                             to always leave this parameter with its default
                             value of ``False``.

        Note: this method is a coroutine.
        """
        await self.emit(
            "message",
            data=data,
            to=to,
            room=room,
            skip_sid=skip_sid,
            namespace=namespace,
            callback=callback,
            ignore_queue=ignore_queue,
        )

    async def call(
        self,
        event: str,
        data: Optional[Any] = None,
        to: Optional[str] = None,
        sid: Optional[str] = None,
        namespace: Optional[str] = None,
        timeout: float = 60,
        ignore_queue: bool = False,
    ) -> Any:
        """Emit a custom event to a client and wait for the response.

        This method issues an emit with a callback and waits for the callback
        to be invoked before returning. If the callback isn't invoked before
        the timeout, then a ``TimeoutError`` exception is raised. If the
        Socket.IO connection drops during the wait, this method still waits
        until the specified timeout.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param to: The session ID of the recipient client.
        :param sid: Alias for the ``to`` parameter.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param timeout: The waiting timeout. If the timeout is reached before
                        the client acknowledges the event, then a
                        ``TimeoutError`` exception is raised.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             client directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used. It is recommended
                             to always leave this parameter with its default
                             value of ``False``.

        Note: this method is not designed to be used concurrently. If multiple
        tasks are emitting at the same time to the same client connection, then
        messages composed of multiple packets may end up being sent in an
        incorrect sequence. Use standard concurrency solutions (such as a Lock
        object) to prevent this situation.

        Note 2: this method is a coroutine.
        """
        if to is None and sid is None:
            raise ValueError("Cannot use call() to broadcast.")
        if not self.async_handlers:
            raise RuntimeError("Cannot use call() when async_handlers is False.")
        callback_event = self.eio.create_event()
        callback_args = []

        def event_callback(*args: Any) -> None:
            callback_args.append(args)
            callback_event.set()

        await self.emit(
            event,
            data=data,
            room=to or sid,
            namespace=namespace,
            callback=event_callback,
            ignore_queue=ignore_queue,
        )
        try:
            await asyncio.wait_for(callback_event.wait(), timeout)
        except asyncio.TimeoutError:
            raise exceptions.TimeoutError() from None
        return (
            callback_args[0]
            if len(callback_args[0]) > 1
            else callback_args[0][0]
            if len(callback_args[0]) == 1
            else None
        )

    async def enter_room(
        self, sid: str, room: str, namespace: Optional[str] = None
    ) -> None:
        """Enter a room.

        This function adds the client to a room. The :func:`emit` and
        :func:`send` functions can optionally broadcast events to all the
        clients in a room.

        :param sid: Session ID of the client.
        :param room: Room name. If the room does not exist it is created.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.

        Note: this method is a coroutine.
        """
        namespace = namespace or "/"
        self.logger.info("%s is entering room %s [%s]", sid, room, namespace)
        await self.manager.enter_room(sid, namespace, room)

    async def leave_room(
        self, sid: str, room: str, namespace: Optional[str] = None
    ) -> None:
        """Leave a room.

        This function removes the client from a room.

        :param sid: Session ID of the client.
        :param room: Room name.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.

        Note: this method is a coroutine.
        """
        namespace = namespace or "/"
        self.logger.info("%s is leaving room %s [%s]", sid, room, namespace)
        await self.manager.leave_room(sid, namespace, room)

    async def close_room(self, room: str, namespace: Optional[str] = None) -> None:
        """Close a room.

        This function removes all the clients from the given room.

        :param room: Room name.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.

        Note: this method is a coroutine.
        """
        namespace = namespace or "/"
        self.logger.info("room %s is closing [%s]", room, namespace)
        await self.manager.close_room(room, namespace)

    async def get_session(
        self, sid: str, namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return the user session for a client.

        :param sid: The session id of the client.
        :param namespace: The Socket.IO namespace. If this argument is omitted
                          the default namespace is used.

        The return value is a dictionary. Modifications made to this
        dictionary are not guaranteed to be preserved. If you want to modify
        the user session, use the ``session`` context manager instead.
        """
        namespace = namespace or "/"
        eio_sid = self.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await self.eio.get_session(eio_sid)
        return eio_session.setdefault(namespace, {})

    async def save_session(
        self, sid: str, session: Dict[str, Any], namespace: Optional[str] = None
    ) -> None:
        """Store the user session for a client.

        :param sid: The session id of the client.
        :param session: The session dictionary.
        :param namespace: The Socket.IO namespace. If this argument is omitted
                          the default namespace is used.
        """
        namespace = namespace or "/"
        eio_sid = self.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await self.eio.get_session(eio_sid)
        eio_session[namespace] = session

    def session(
        self, sid: str, namespace: Optional[str] = None
    ) -> AsyncContextManager[Dict[str, Any]]:
        """Return the user session for a client with context manager syntax.

        :param sid: The session id of the client.

        This is a context manager that returns the user session dictionary for
        the client. Any changes that are made to this dictionary inside the
        context manager block are saved back to the session. Example usage::

            @eio.on("connect")
            async def on_connect(sid, environ):
                username = authenticate_user(environ)
                if not username:
                    return False
                async with eio.session(sid) as session:
                    session["username"] = username


            @eio.on("message")
            async def on_message(sid, msg):
                async with eio.session(sid) as session:
                    print("received message from ", session["username"])
        """

        class _session_context_manager:
            def __init__(
                self, server: "AsyncServer", sid: str, namespace: Optional[str]
            ):
                self.server = server
                self.sid = sid
                self.namespace = namespace
                self.session: Optional[Dict[str, Any]] = None

            async def __aenter__(self) -> Dict[str, Any]:
                self.session = await self.server.get_session(
                    sid, namespace=self.namespace
                )
                return self.session

            async def __aexit__(self, *args: Any) -> None:
                await self.server.save_session(
                    sid, self.session or {}, namespace=self.namespace
                )

        return _session_context_manager(self, sid, namespace)

    async def disconnect(
        self, sid: str, namespace: Optional[str] = None, ignore_queue: bool = False
    ) -> None:
        """Disconnect a client.

        :param sid: Session ID of the client.
        :param namespace: The Socket.IO namespace to disconnect. If this
                          argument is omitted the default namespace is used.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the disconnect is processed
                             locally, without broadcasting on the queue. It is
                             recommended to always leave this parameter with
                             its default value of ``False``.

        Note: this method is a coroutine.
        """
        namespace = namespace or "/"
        if ignore_queue:
            delete_it = self.manager.is_connected(sid, namespace)
        else:
            delete_it = await self.manager.can_disconnect(sid, namespace)
        if delete_it:
            self.logger.info("Disconnecting %s [%s]", sid, namespace)
            eio_sid = self.manager.pre_disconnect(sid, namespace=namespace)
            await self._send_packet(
                eio_sid, self.packet_class(packet.DISCONNECT, namespace=namespace)
            )
            await self._trigger_event(
                "disconnect", namespace, sid, self.reason.SERVER_DISCONNECT
            )
            await self.manager.disconnect(sid, namespace=namespace, ignore_queue=True)

    async def shutdown(self) -> None:
        """Stop Socket.IO background tasks.

        This method stops all background activity initiated by the Socket.IO
        server. It must be called before shutting down the web server.
        """
        self.logger.info("Socket.IO is shutting down")
        await self.eio.shutdown()

    async def handle_request(self, *args: Any, **kwargs: Any) -> Any:
        """Handle an HTTP request from the client.

        This is the entry point of the Socket.IO application. This function
        returns the HTTP response body to deliver to the client.

        Note: this method is a coroutine.
        """
        return await self.eio.handle_request(*args, **kwargs)

    def start_background_task(
        self, target: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ) -> asyncio.Task[Any]:
        """Start a background task using the appropriate async model.

        This is a utility function that applications can use to start a
        background task using the method that is compatible with the
        selected async mode.

        :param target: the target function to execute. Must be a coroutine.
        :param args: arguments to pass to the function.
        :param kwargs: keyword arguments to pass to the function.

        The return value is a ``asyncio.Task`` object.
        """
        return self.eio.start_background_task(target, *args, **kwargs)

    async def sleep(self, seconds: float = 0) -> None:
        """Sleep for the requested amount of time using the appropriate async
        model.

        This is a utility function that applications can use to put a task to
        sleep without having to worry about using the correct call for the
        selected async mode.

        Note: this method is a coroutine.
        """
        return await self.eio.sleep(seconds)

    def instrument(
        self,
        auth: Optional[
            Union[
                bool,
                Dict[str, Any],
                List[Dict[str, Any]],
                Callable[[Dict[str, Any]], bool],
            ]
        ] = None,
        mode: str = "development",
        read_only: bool = False,
        server_id: Optional[str] = None,
        namespace: str = "/admin",
        server_stats_interval: int = 2,
    ) -> "InstrumentedAsyncServer":
        """Instrument the Socket.IO server for monitoring with the `Socket.IO
        Admin UI <https://socket.io/docs/v4/admin-ui/>`_.

        :param auth: Authentication credentials for Admin UI access. Set to a
                     dictionary with the expected login (usually ``username``
                     and ``password``) or a list of dictionaries if more than
                     one set of credentials need to be available. For more
                     complex authentication methods, set to a callable that
                     receives the authentication dictionary as an argument and
                     returns ``True`` if the user is allowed or ``False``
                     otherwise. To disable authentication, set this argument to
                     ``False`` (not recommended, never do this on a production
                     server).
        :param mode: The reporting mode. The default is ``'development'``,
                     which is best used while debugging, as it may have a
                     significant performance effect. Set to ``'production'`` to
                     reduce the amount of information that is reported to the
                     admin UI.
        :param read_only: If set to ``True``, the admin interface will be
                          read-only, with no option to modify room assignments
                          or disconnect clients. The default is ``False``.
        :param server_id: The server name to use for this server. If this
                          argument is omitted, the server generates its own
                          name.
        :param namespace: The Socket.IO namespace to use for the admin
                          interface. The default is ``/admin``.
        :param server_stats_interval: The interval in seconds at which the
                                      server emits a summary of it stats to all
                                      connected admins.
        """
        from .async_admin import InstrumentedAsyncServer

        return InstrumentedAsyncServer(
            self,
            auth=auth,
            mode=mode,
            read_only=read_only,
            server_id=server_id,
            namespace=namespace,
            server_stats_interval=server_stats_interval,
        )

    async def _send_packet(self, eio_sid: str, pkt: packet.Packet) -> None:
        """Send a Socket.IO packet to a client."""
        encoded_packet = pkt.encode()
        if isinstance(encoded_packet, list):
            for ep in encoded_packet:
                await self.eio.send(eio_sid, ep)
        else:
            await self.eio.send(eio_sid, encoded_packet)

    async def _send_eio_packet(self, eio_sid: str, eio_pkt: Any) -> None:
        """Send a raw Engine.IO packet to a client."""
        await self.eio.send_packet(eio_sid, eio_pkt)

    async def _handle_connect(
        self, eio_sid: str, namespace: Optional[str], data: Optional[Any]
    ) -> None:
        """Handle a client connection request."""
        namespace = namespace or "/"
        sid = None
        if (
            namespace in self.handlers
            or namespace in self.namespace_handlers
            or self.namespaces == "*"
            or namespace in self.namespaces
        ):
            sid = await self.manager.connect(eio_sid, namespace)
        if sid is None:
            await self._send_packet(
                eio_sid,
                self.packet_class(
                    packet.CONNECT_ERROR, data="Unable to connect", namespace=namespace
                ),
            )
            return

        if self.always_connect:
            await self._send_packet(
                eio_sid,
                self.packet_class(packet.CONNECT, {"sid": sid}, namespace=namespace),
            )
        fail_reason = exceptions.ConnectionRefusedError().error_args
        try:
            if data:
                success = await self._trigger_event(
                    "connect", namespace, sid, self.environ[eio_sid], data
                )
            else:
                try:
                    success = await self._trigger_event(
                        "connect", namespace, sid, self.environ[eio_sid]
                    )
                except TypeError:
                    success = await self._trigger_event(
                        "connect", namespace, sid, self.environ[eio_sid], None
                    )
        except exceptions.ConnectionRefusedError as exc:
            fail_reason = exc.error_args
            success = False

        if success is False:
            if self.always_connect:
                self.manager.pre_disconnect(sid, namespace)
                await self._send_packet(
                    eio_sid,
                    self.packet_class(
                        packet.DISCONNECT, data=fail_reason, namespace=namespace
                    ),
                )
            else:
                await self._send_packet(
                    eio_sid,
                    self.packet_class(
                        packet.CONNECT_ERROR, data=fail_reason, namespace=namespace
                    ),
                )
            await self.manager.disconnect(sid, namespace, ignore_queue=True)
        elif not self.always_connect:
            await self._send_packet(
                eio_sid,
                self.packet_class(packet.CONNECT, {"sid": sid}, namespace=namespace),
            )

    async def _handle_disconnect(
        self, eio_sid: str, namespace: Optional[str], reason: Optional[str] = None
    ) -> None:
        """Handle a client disconnect."""
        namespace = namespace or "/"
        sid = self.manager.sid_from_eio_sid(eio_sid, namespace)
        if not self.manager.is_connected(sid, namespace):  # pragma: no cover
            return
        self.manager.pre_disconnect(sid, namespace=namespace)
        try:
            await self._trigger_event(
                "disconnect", namespace, sid, reason or self.reason.CLIENT_DISCONNECT
            )
        except TypeError:
            # Fall back to legacy disconnect handler signature without reason
            await self._trigger_event("disconnect", namespace, sid)
        await self.manager.disconnect(sid, namespace, ignore_queue=True)

    async def _handle_event(
        self, eio_sid: str, namespace: Optional[str], id: Optional[int], data: Any
    ) -> None:
        """Handle an incoming client event."""
        namespace = namespace or "/"
        sid = self.manager.sid_from_eio_sid(eio_sid, namespace)
        if sid is None:
            return
        self.logger.info('received event "%s" from %s [%s]', data[0], sid, namespace)
        if not self.manager.is_connected(sid, namespace):
            self.logger.warning("%s is not connected to namespace %s", sid, namespace)
            return
        if self.async_handlers:
            task = self.start_background_task(
                self._handle_event_internal, self, sid, eio_sid, data, namespace, id
            )
            task_reference_holder.add(task)
            task.add_done_callback(task_reference_holder.discard)
        else:
            await self._handle_event_internal(self, sid, eio_sid, data, namespace, id)

    async def _handle_event_internal(
        self,
        server: "AsyncServer",
        sid: str,
        eio_sid: str,
        data: Any,
        namespace: Optional[str],
        id: Optional[int],
    ) -> None:
        r = await server._trigger_event(data[0], namespace, sid, *data[1:])
        if r != server.not_handled and id is not None:
            # send ACK packet with the response returned by the handler
            # tuples are expanded as multiple arguments
            if r is None:
                data = []
            elif isinstance(r, tuple):
                data = list(r)
            else:
                data = [r]
            await server._send_packet(
                eio_sid,
                server.packet_class(packet.ACK, namespace=namespace, id=id, data=data),
            )

    async def _handle_ack(
        self, eio_sid: str, namespace: Optional[str], id: Optional[int], data: Any
    ) -> None:
        """Handle ACK packets from the client."""
        namespace = namespace or "/"
        sid = self.manager.sid_from_eio_sid(eio_sid, namespace)
        self.logger.info("received ack from %s [%s]", sid, namespace)
        await self.manager.trigger_callback(sid, id, data)

    async def _trigger_event(
        self, event: str, namespace: Optional[str], *args: Any
    ) -> Any:
        """Invoke an application event handler using ContextVar-based dependency injection."""
        # Keep originals to support dependency injection from raw payload
        original_args = args
        original_sid: Optional[str] = None
        if original_args and isinstance(original_args[0], str):
            original_sid = original_args[0]

        # first see if we have an explicit handler for the event
        handler, args = self._get_event_handler(event, namespace, args)
        if handler:
            # Prepare data for dependency injection
            payload_data: Any = None
            if event not in base_server.BaseServer.reserved_events:
                if len(original_args) >= 2:
                    candidate_payload = original_args[1]
                    # Only accept single-argument payload for model injection
                    if len(original_args[1:]) == 1:
                        payload_data = candidate_payload
                    else:
                        payload_data = list(
                            original_args[1:]
                        )  # Provide full args list for DI when multiple

            # Prepare environ for DI
            computed_environ: Any = None
            if original_sid is not None:
                try:
                    computed_environ = self.get_environ(original_sid, namespace)
                except Exception:
                    computed_environ = None

            # Prepare auth payload for connect events
            connect_auth_payload: Any = None
            if event == "connect" and len(original_args) >= 3:
                connect_auth_payload = original_args[2]

            # Prepare disconnect reason
            disconnect_reason: Any = None
            if event == "disconnect" and len(args) > 0:
                disconnect_reason = args[-1]

            # Execute middleware chain if middlewares are registered
            if (
                hasattr(self, "_middleware_chain")
                and self._middleware_chain.middlewares
            ):
                # Use middleware chain for execution
                ret = await self._middleware_chain.execute(
                    event=event,
                    sid=original_sid or "",
                    data=payload_data,
                    handler=handler,
                    namespace=namespace,
                    environ=computed_environ,
                    auth=connect_auth_payload if event == "connect" else None,
                    server=self,
                )
            else:
                # Use ContextVar-based dependency injection
                from .types import (
                    Auth as _AuthType,
                    Data as _DataType,
                    Environ as _EnvironType,
                    Event as _EventType,
                    Reason as _ReasonType,
                    SocketID as _SocketIDType,
                )

                def _uses_di(fn: Any) -> bool:
                    try:
                        sig_local = inspect.signature(fn)
                    except Exception:
                        return False
                    try:
                        from .dependency import Depends as _Depends  # type: ignore
                    except Exception:
                        _Depends = None  # type: ignore
                    try:
                        from pydantic import BaseModel as _PydanticBaseModel  # type: ignore
                    except Exception:
                        _PydanticBaseModel = None  # type: ignore
                    for _p in sig_local.parameters.values():
                        if _p.name in {"socket_id", "environ", "auth", "reason", "data", "event"}:
                            return True
                        if (
                            _p.default is not inspect._empty
                            and _Depends is not None
                            and isinstance(_p.default, _Depends)
                        ):
                            return True
                        ann = _p.annotation
                        if ann in (
                            _SocketIDType,
                            _EnvironType,
                            _AuthType,
                            _ReasonType,
                            _DataType,
                            _EventType,
                        ):
                            return True
                        if (
                            _PydanticBaseModel is not None
                            and isinstance(ann, type)
                            and issubclass(ann, _PydanticBaseModel)
                        ):
                            return True
                    return False

                di_mode = _uses_di(handler)

                ret = await run_with_context(
                    handler,
                    *(args if not di_mode else ()),
                    socket_id=original_sid,
                    environ=computed_environ,
                    auth=connect_auth_payload if event == "connect" else None,
                    reason=disconnect_reason if event == "disconnect" else None,
                    data=payload_data,
                    event=event,
                    server=self,
                )

            # Validate response if response_model is defined
            ret = self._validate_response(handler, ret)
            return ret
        # or else, forward the event to a namespace handler if one exists
        handler, args = self._get_namespace_handler(namespace, args)
        if handler:
            return await handler.trigger_event(event, *args)
        return self.not_handled

    async def _handle_eio_connect(self, eio_sid: str, environ: Dict[str, Any]) -> None:  # type: ignore[override]
        """Handle the Engine.IO connection event."""
        if not self.manager_initialized:
            self.manager_initialized = True
            self.manager.initialize()
        self.environ[eio_sid] = environ

    async def _handle_eio_message(self, eio_sid: str, data: Union[bytes, str]) -> None:  # type: ignore[override]
        """Dispatch Engine.IO messages."""
        if eio_sid in self._binary_packet:
            pkt = self._binary_packet[eio_sid]
            if pkt.add_attachment(data):
                del self._binary_packet[eio_sid]
                if pkt.packet_type == packet.BINARY_EVENT:
                    await self._handle_event(eio_sid, pkt.namespace, pkt.id, pkt.data)
                else:
                    await self._handle_ack(eio_sid, pkt.namespace, pkt.id, pkt.data)
        else:
            pkt = self.packet_class(encoded_packet=data)
            if pkt.packet_type == packet.CONNECT:
                await self._handle_connect(eio_sid, pkt.namespace, pkt.data)
            elif pkt.packet_type == packet.DISCONNECT:
                await self._handle_disconnect(
                    eio_sid, pkt.namespace, self.reason.CLIENT_DISCONNECT
                )
            elif pkt.packet_type == packet.EVENT:
                await self._handle_event(eio_sid, pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.ACK:
                await self._handle_ack(eio_sid, pkt.namespace, pkt.id, pkt.data)
            elif (
                pkt.packet_type == packet.BINARY_EVENT
                or pkt.packet_type == packet.BINARY_ACK
            ):
                self._binary_packet[eio_sid] = pkt
            elif pkt.packet_type == packet.CONNECT_ERROR:
                raise ValueError("Unexpected CONNECT_ERROR packet.")
            else:
                raise ValueError("Unknown packet type.")

    async def _handle_eio_disconnect(self, eio_sid: str, reason: str) -> None:  # type: ignore[override]
        """Handle Engine.IO disconnect event."""
        for n in list(self.manager.get_namespaces()).copy():
            await self._handle_disconnect(eio_sid, n, reason)
        if eio_sid in self.environ:
            del self.environ[eio_sid]

    def _engineio_server_class(self) -> Any:
        return engineio.AsyncServer
