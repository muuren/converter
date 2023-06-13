import pytest


class CallCounter:
    def __init__(self):
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1


@pytest.fixture(scope="function")
def call_counter():
    return CallCounter()
