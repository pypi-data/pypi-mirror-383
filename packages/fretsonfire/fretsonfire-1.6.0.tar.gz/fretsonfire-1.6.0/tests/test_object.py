"""Tests for the distributed object manager."""
import pytest

from src.fretsonfire import Object as fof_object


class DummyMessage(fof_object.Message):
    """Simple marker message for signalling."""


class DummyObject(fof_object.Object):
    def __init__(self, manager, id=None, name="unnamed"):
        super().__init__(id=id, manager=manager, name=name)
        self.x = 1
        self.y = 2
        self.z = 3
        self.name = name
        self.lastMessage = None
        self.share("x", "y", "z", "name")
        self.connect(DummyMessage, self.message)

    def message(self, message):
        self.lastMessage = message


@pytest.fixture
def manager():
    return fof_object.Manager(100)


def test_attributes(manager):
    obj = DummyObject(manager)
    obj.x = 1234
    changes = obj.getChanges()
    assert changes
    assert obj.getChanges() is None
    obj.applyChanges(changes)

    other = DummyObject(manager)
    other.applyChanges(changes)
    assert obj.x == other.x

    other.x = 5678
    obj.applyChanges(other.getChanges())
    assert obj.x == other.x


def test_messaging(manager):
    obj1 = DummyObject(manager)
    obj2 = DummyObject(manager)

    obj1.emit(DummyMessage())
    obj2.applyChanges(obj1.getChanges())

    assert isinstance(obj1.lastMessage, DummyMessage)
    assert isinstance(obj2.lastMessage, DummyMessage)


def test_manager_state_migration():
    mgr = fof_object.Manager(200)
    obj = DummyObject(mgr, name="first")
    obj.x = 31337

    original_id = mgr.id
    obj_id = obj.id
    data = mgr.getChanges(everything=True)
    assert data

    mgr.reset()
    mgr.setId(1)
    mgr.applyChanges(original_id, data)

    migrated = mgr.objects[obj_id]
    assert migrated.x == obj.x
    assert migrated is not obj

    obj3 = DummyObject(mgr, name="third")
    obj3_id = obj3.id
    obj3.x = 0xDADA

    obj4 = DummyObject(mgr, name="fourth")
    obj4_id = obj4.id
    obj4.delete()

    mgr.getChanges()
    data = mgr.getChanges(everything=True)

    mgr.reset()
    mgr.setId(2)
    mgr.applyChanges(original_id, data)

    assert obj_id in mgr.objects
    assert obj3_id in mgr.objects
    assert obj4_id not in mgr.objects
    assert mgr.objects[obj3_id].x == 0xDADA


def test_references():
    mgr = fof_object.Manager(300)
    bag = DummyObject(mgr, name="bag")
    apple = DummyObject(mgr, name="apple")
    bag.x = [apple]

    bag_id, apple_id = bag.id, apple.id
    data = mgr.getChanges()
    mgr.reset()
    mgr.setId(1)
    mgr.applyChanges(300, data)

    bag_clone = mgr.objects[bag_id]
    apple_clone = mgr.objects[apple_id]

    assert bag_clone.name == "bag"
    assert apple_clone.name == "apple"
    assert apple_clone in bag_clone.x


def test_multiple_managers():
    manager_one = fof_object.Manager(1000)
    manager_two = fof_object.Manager(2000)

    obj_one = DummyObject(manager_one)
    obj_two = DummyObject(manager_two)

    manager_one.applyChanges(manager_two.id, manager_two.getChanges())
    manager_two.applyChanges(manager_one.id, manager_one.getChanges())

    assert len(manager_one.objects) == 2
    assert len(manager_two.objects) == 2
