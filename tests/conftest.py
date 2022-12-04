import pytest


from .fixtures import *


@pytest.fixture
def kwargify():
    def _kwargify(**kwargs):
        return {
            k: v
            for k, v in kwargs.items() if v is not None
        }
    return _kwargify
