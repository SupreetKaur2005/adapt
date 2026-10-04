"""Tests for `adapt.routing.model_scheduler`."""
import threading
import time

from adapt.routing.model_router import ModelHandle
from adapt.routing.model_scheduler import acquire


def test_sequential_acquire_does_not_deadlock():
    handle = ModelHandle(tier="lightweight", model_name="mistral:7b")
    with acquire(handle):
        pass
    with acquire(handle):
        pass


def test_second_thread_blocks_until_first_releases():
    handle = ModelHandle(tier="mid", model_name="qwen3.5")
    order: list[str] = []

    def hold_lock():
        with acquire(handle):
            order.append("first-acquired")
            time.sleep(0.1)
            order.append("first-released")

    t = threading.Thread(target=hold_lock)
    t.start()
    time.sleep(0.02)  # let the first thread grab the lock first

    with acquire(handle):
        order.append("second-acquired")

    t.join()
    assert order.index("first-released") < order.index("second-acquired")
