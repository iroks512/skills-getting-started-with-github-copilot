"""Pytest configuration and fixtures for testing the FastAPI application."""

import pytest
import copy
from fastapi.testclient import TestClient
from src import app as app_module


def get_fresh_activities():
    """Create a fresh copy of activities data."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }


@pytest.fixture
def client(monkeypatch):
    """Provide a FastAPI TestClient with isolated test data.
    
    This fixture ensures test isolation by replacing the global activities
    dictionary with a fresh copy for each test, preventing state leakage.
    """
    # Replace the global activities dict with a fresh copy
    fresh_activities = get_fresh_activities()
    monkeypatch.setattr(app_module, 'activities', fresh_activities)
    
    # Return a TestClient that uses the patched activities
    return TestClient(app_module.app)


@pytest.fixture
def test_activities():
    """Provide a clean copy of activities data for each test.
    
    This ensures test isolation by giving each test its own in-memory copy
    of the activities dictionary, preventing state leakage between tests.
    """
    return get_fresh_activities()


@pytest.fixture
def sample_emails():
    """Provide sample email addresses for testing participant operations."""
    return {
        "existing_chess": "michael@mergington.edu",
        "existing_programming": "emma@mergington.edu",
        "new_student": "newstudent@mergington.edu",
        "another_student": "anotherstudent@mergington.edu",
    }
