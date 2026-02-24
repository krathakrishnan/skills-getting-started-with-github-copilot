import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)
