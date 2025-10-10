"""Resource loader tests that avoid OpenGL dependencies."""
import pytest

from src.fretsonfire.Engine import Engine
from src.fretsonfire.Resource import Resource


def _run_until(engine, condition, limit=1000):
    for _ in range(limit):
        engine.run()
        if condition():
            return
    raise AssertionError("Timed out while waiting for condition")


@pytest.fixture
def engine():
    instance = Engine()
    try:
        yield instance
    finally:
        instance.quit()


@pytest.fixture
def resource(engine):
    res = Resource()
    engine.addTask(res, synchronized=False)
    return res


def loader():
    return 0xDADA


def test_async_load(engine, resource):
    class Holder:
        result = None

    holder = Holder()
    resource.load(holder, "result", loader)
    _run_until(engine, lambda: holder.result is not None)
    assert holder.result == 0xDADA


def test_sync_load(engine, resource):
    class Holder:
        result2 = None

    holder = Holder()
    value = resource.load(holder, "result2", loader, synch=True)
    assert value == 0xDADA
    assert holder.result2 == 0xDADA


def test_async_load_series(engine, resource):
    class Holder:
        pass

    holder = Holder()
    for index in range(10):
        resource.load(holder, f"result{index}", loader)

    _run_until(engine, lambda: getattr(holder, "result9", None) is not None)
    assert getattr(holder, "result9") == 0xDADA


def test_onload_callback(engine, resource):
    class Holder:
        fuuba = None
        quux = None

    holder = Holder()

    def loaded(result):
        holder.quux = result

    loader_thread = resource.load(holder, "fuuba", loader, onLoad=loaded)
    loader_thread.join()

    _run_until(engine, lambda: holder.fuuba is not None)
    assert holder.fuuba == holder.quux == 0xDADA

