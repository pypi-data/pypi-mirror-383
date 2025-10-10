"""Headless tests for song loading and saving."""

import importlib
import os
from pathlib import Path

import pytest


SONG_DIR = Path(__file__).resolve().parents[1] / "src" / "fretsonfire" / "data" / "songs" / "defy"


class DummyMusic:
    def __init__(self, filename):
        self.filename = Path(filename)
        self.volume = 1.0

    def play(self, *args, **kwargs):
        return None

    def stop(self):
        return None

    def rewind(self):
        return None

    def pause(self):
        return None

    def unpause(self):
        return None

    def setVolume(self, volume):
        self.volume = volume

    def fadeout(self, time):
        return None

    def getPosition(self):
        return 0

    def isPlaying(self):
        return True


class DummyStreamingSound(DummyMusic):
    def __init__(self, engine, channel, filename):
        super().__init__(filename)
        self.channel = channel


class DummyChannel:
    def __init__(self, index):
        self.index = index


class DummyAudio:
    def __init__(self):
        self.channels = {}
        self.paused = False

    def getChannel(self, index):
        channel = DummyChannel(index)
        self.channels[index] = channel
        return channel

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False


class DummyEngine:
    def __init__(self):
        self.audio = DummyAudio()


@pytest.fixture
def song_module(monkeypatch, tmp_path):
    tmp_home = tmp_path / "home"
    tmp_home.mkdir()
    monkeypatch.setenv("HOME", str(tmp_home))
    monkeypatch.setenv("FRETSONFIRE_HOME", str(tmp_home))

    import src.fretsonfire.Log as log_module
    import src.fretsonfire.Song as song_module

    importlib.reload(log_module)
    importlib.reload(song_module)

    log_module.configure(log_path=tmp_home / "fretsonfire.log", quiet=True, console=False)

    monkeypatch.setattr(song_module.Audio, "Music", DummyMusic)
    monkeypatch.setattr(song_module.Audio, "StreamingSound", DummyStreamingSound)

    return song_module


def build_song(song_module, info_dir: Path):
    engine = DummyEngine()
    info = str(info_dir / "song.ini")
    song_audio = str(info_dir / "song.ogg")
    guitar = str(info_dir / "guitar.ogg")
    notes = str(info_dir / "notes.mid")
    return song_module.Song(engine, info, song_audio, guitar, None, notes)


def test_song_loading_parses_bpm(song_module):
    song = build_song(song_module, SONG_DIR)
    assert int(song.bpm) == 122


def test_song_save_preserves_notes(song_module, tmp_path):
    work_dir = tmp_path / "song"
    work_dir.mkdir()

    for filename in ("song.ini", "song.ogg", "guitar.ogg", "notes.mid"):
        (work_dir / filename).write_bytes((SONG_DIR / filename).read_bytes())

    song = build_song(song_module, work_dir)

    before = [event for event in song.track.getAllEvents() if isinstance(event[1], song_module.Note)]

    song.save()

    reloaded = build_song(song_module, work_dir)
    after = [event for event in reloaded.track.getAllEvents() if isinstance(event[1], song_module.Note)]

    assert len(before) == len(after)
    for (time1, note1), (time2, note2) in zip(before, after):
        assert isinstance(note1, song_module.Note)
        assert isinstance(note2, song_module.Note)
        assert abs(time1 - time2) < 2
        assert abs(note1.length - note2.length) < 2
        assert note1.number == note2.number
