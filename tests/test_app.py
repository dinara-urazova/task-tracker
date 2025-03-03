import sys
import os
import pytest
from config_reader import Settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

env_config = Settings()


@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client





