"""Timer behaviour tests."""
import pytest
import pygame

from src.fretsonfire.Timer import Timer


@pytest.fixture(autouse=True)
def pygame_env():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


def test_frame_limiter_average_fps():
    timer = Timer(fps=60)
    fps_samples = []

    while timer.frame < 100:
        list(timer.advanceFrame())
        fps_samples.append(timer.fpsEstimate)

    stable_samples = [value for value in fps_samples[30:] if value]
    assert stable_samples, "Expected non-zero FPS samples after warm-up"

    avg_fps = sum(stable_samples) / len(stable_samples)
    assert 0.8 * timer.fps < avg_fps < 1.2 * timer.fps

