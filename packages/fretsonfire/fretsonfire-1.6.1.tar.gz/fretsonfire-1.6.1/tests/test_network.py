"""Tests exercising the Network handshake framing logic."""

import errno
import itertools
import struct
from collections.abc import Callable

import pytest

from src.fretsonfire import Network


class _FakeSocket:
    """Minimal socket stub so asyncore dispatcher can attach to it."""

    _ids = itertools.count(1000)

    def __init__(self):
        self._fd = next(self._ids)

    def setblocking(self, _flag: bool) -> None:  # pragma: no cover - no behaviour
        pass

    def getpeername(self) -> tuple[str, int]:  # pragma: no cover - unused in tests
        raise OSError(errno.ENOTCONN, "fake socket is never connected")

    def fileno(self) -> int:
        return self._fd

    def close(self) -> None:  # pragma: no cover - no behaviour
        pass


@pytest.fixture
def connection_factory() -> Callable[[], Network.Connection]:
    created: list[Network.Connection] = []

    def factory() -> Network.Connection:
        conn = Network.Connection(sock=_FakeSocket())
        conn.server = None
        conn.handleClose = lambda: None  # type: ignore[assignment]
        conn.handle_close = lambda: None  # type: ignore[assignment]
        created.append(conn)
        return conn

    yield factory

    for conn in created:
        conn.close()


def test_handle_accept_frames_handshake_bytes(monkeypatch: pytest.MonkeyPatch, connection_factory: Callable[[], Network.Connection]) -> None:
    sent: list[bytes] = []
    conn = connection_factory()
    conn.send = lambda data: sent.append(data) or len(data)  # type: ignore[assignment]

    def fake_server_init(self, port: int = Network.PORT, localOnly: bool = True) -> None:  # noqa: ARG001
        self.clients = {}
        self._Server__idCounter = 0

    monkeypatch.setattr(Network.Server, "__init__", fake_server_init)

    server = Network.Server()
    server.createConnection = lambda *, sock: conn  # type: ignore[assignment]
    server.accept = lambda: (_FakeSocket(), ("127.0.0.1", Network.PORT))  # type: ignore[assignment]

    opened: list[Network.Connection] = []
    server.handleConnectionOpen = lambda connection: opened.append(connection)  # type: ignore[assignment]

    server.handle_accept()

    assert server.clients == {1: conn}
    assert conn.server is server
    assert opened == [conn]

    conn.handle_write()

    assert sent == [struct.pack("H", 2), struct.pack("H", 1)]


def test_handle_read_delivers_payload_and_resets_state(connection_factory: Callable[[], Network.Connection]) -> None:
    conn = connection_factory()
    conn.id = 1

    payloads = [b"hello world", b"bye"]
    frames: list[bytes] = []
    for payload in payloads:
        frames.extend((struct.pack("H", len(payload)), payload))

    def fake_recv(n: int) -> bytes:
        if not frames:
            return b""
        chunk = frames[0][:n]
        frames[0] = frames[0][n:]
        if not frames[0]:
            frames.pop(0)
        return chunk

    received: list[bytes] = []
    conn.recv = fake_recv  # type: ignore[assignment]
    conn.handlePacket = lambda packet: received.append(packet)  # type: ignore[assignment]

    for _ in payloads:
        conn.handle_read()
        conn.handle_read()

    assert received == payloads
    assert conn._receivedSizeField == 0
    assert frames == []
    assert conn._packet.tell() == 0
