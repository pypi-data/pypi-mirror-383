"""Audio subsystem smoke tests."""
import pytest

from src.fretsonfire.Audio import Audio


@pytest.fixture
def audio():
    instance = Audio()
    try:
        yield instance
    finally:
        instance.close()


def test_audio_open_and_close(audio):
    """Audio mixer should open with the default configuration."""
    assert audio.open()

