"""Tests for activity listing endpoints.

Covers GET / (root redirect) and GET /activities endpoints.
Tests both unit-level data validation and integration-level HTTP contracts.
"""

import pytest


class TestRootRedirect:
    """Tests for the root endpoint (GET /)."""

    def test_root_redirects_to_static(self, client):
        """Integration: Verify GET / returns a redirect to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_follow(self, client):
        """Integration: Verify following the redirect returns 200."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Integration: Verify GET /activities returns 200 OK."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_json(self, client):
        """Integration: Verify response is valid JSON."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Unit: Verify the response contains all expected activities."""
        response = client.get("/activities")
        data = response.json()
        
        # Check that expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in data, f"Expected {activity} in activities"

    def test_activity_structure_is_valid(self, client):
        """Unit: Verify each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, \
                    f"Activity '{activity_name}' missing field '{field}'"

    def test_participants_are_lists(self, client):
        """Unit: Verify participants field is always a list."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity '{activity_name}' participants should be a list"

    def test_get_activities_includes_initial_participants(self, client):
        """Unit: Verify initial participant data is loaded correctly."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 initial participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
