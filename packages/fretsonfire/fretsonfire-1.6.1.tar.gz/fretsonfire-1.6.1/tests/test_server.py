"""Headless tests for server-side session management."""

import pytest

from src.fretsonfire import Server as fof_server


class DummyEngine:
    def __init__(self):
        self.added = []
        self.removed = []

    def addTask(self, task, *, synchronized=True):
        self.added.append((task, synchronized))

    def removeTask(self, task):
        self.removed.append(task)


class DummySession:
    def __init__(self, session_id):
        self.id = session_id
        self.sent_messages: list[object] = []
        self.handled_messages: list[tuple[int, object]] = []

    def sendMessage(self, message):
        self.sent_messages.append(message)

    def handleMessage(self, sender, message):
        self.handled_messages.append((sender, message))


class DummyWorld:
    def __init__(self, engine, server):
        self.engine = engine
        self.server = server


@pytest.fixture(autouse=True)
def stub_network(monkeypatch):
    def fake_init(self, port=fof_server.Network.PORT, localOnly=True):
        self.clients = {}
        self._Server__idCounter = 0

    monkeypatch.setattr(fof_server.Network.Server, "__init__", fake_init)
    monkeypatch.setattr(fof_server.Network.Server, "handleConnectionClose", lambda self, conn: None)
    monkeypatch.setattr(fof_server, "WorldServer", DummyWorld)


def test_handle_connection_open_and_close(monkeypatch):
    engine = DummyEngine()
    server = fof_server.Server(engine)

    session = DummySession(session_id=1)

    server.handleConnectionOpen(session)
    assert server.sessions[1] is session
    assert engine.added == [(session, False)]

    server.handleConnectionClose(session)
    assert 1 not in server.sessions
    assert engine.removed == [session]


def test_broadcast_message_respects_ignore(monkeypatch):
    engine = DummyEngine()
    server = fof_server.Server(engine)

    session_a = DummySession(1)
    session_b = DummySession(2)
    server.sessions = {1: session_a, 2: session_b}

    server.broadcastMessage("ping", meToo=False, ignore=[1])

    assert session_a.sent_messages == []
    assert session_b.sent_messages == ["ping"]


def test_run_invokes_network_communicate(monkeypatch):
    engine = DummyEngine()
    server = fof_server.Server(engine)

    calls = []
    monkeypatch.setattr(fof_server.Network, "communicate", lambda cycles=1: calls.append(cycles))

    server.run(0)
    assert calls == [1]
