"""Headless tests for the core Engine scheduler."""

from src.fretsonfire.Engine import Engine
from src.fretsonfire.Task import Task


class RecordingTask(Task):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.calls: list[int] = []
        self.started_called = False
        self.stopped_called = False

    def started(self):  # noqa: D401 - simple flag setter
        self.started_called = True

    def stopped(self):  # noqa: D401 - simple flag setter
        self.stopped_called = True

    def run(self, ticks: int = 0):  # noqa: D401 - record invocation
        self.calls.append(ticks)


class FakeTimer:
    def __init__(self, frames: list[list[int]]):
        self._frames = frames
        self._index = 0

    def advanceFrame(self):
        if self._index >= len(self._frames):
            return []
        ticks = self._frames[self._index]
        self._index += 1
        return ticks


def test_engine_runs_frame_and_sync_tasks():
    engine = Engine()
    engine.timer = FakeTimer([[5, 7]])

    frame_task = RecordingTask("frame")
    sync_task_a = RecordingTask("sync-a")
    sync_task_b = RecordingTask("sync-b")

    engine.addTask(frame_task, synchronized=False)
    engine.addTask(sync_task_a)
    engine.addTask(sync_task_b)

    ran = engine.run()
    assert ran is True

    assert frame_task.calls == [0]
    assert sync_task_a.calls == [5, 7]
    assert sync_task_b.calls == [5, 7]


def test_remove_task_invokes_stopped():
    engine = Engine()
    engine.timer = FakeTimer([[]])

    task = RecordingTask("sync")
    engine.addTask(task)

    engine.removeTask(task)

    assert task.started_called is True
    assert task.stopped_called is True
    assert task not in engine.tasks
    assert task not in engine.frameTasks


def test_run_without_tasks_returns_false():
    engine = Engine()
    engine.timer = FakeTimer([[]])

    assert engine.run() is False
