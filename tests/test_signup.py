"""Tests for student signup endpoint.

Covers POST /activities/{activity_name}/signup endpoint.
Tests success paths, validation, and error handling.
"""

import pytest


class TestSignupSuccessPath:
    """Tests for successful signup operations."""

    def test_signup_endpoint_returns_200_for_valid_request(self, client, sample_emails):
        """Integration: Verify POST signup returns 200 for valid input."""
        email = sample_emails["new_student"]
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup?email={email}",
            follow_redirects=True
        )
        
        assert response.status_code == 200

    def test_signup_endpoint_returns_success_message(self, client, sample_emails):
        """Integration: Verify response contains success message."""
        email = sample_emails["new_student"]
        activity = "Programming Class"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_emails):
        """Integration: Verify participant is added to the activity's participant list."""
        email = sample_emails["new_student"]
        activity = "Chess Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]

    def test_signup_increases_participant_count(self, client, sample_emails):
        """Unit: Verify signup increases the participant count."""
        email = sample_emails["new_student"]
        activity = "Programming Class"
        
        # Get initial count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated count
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])
        
        assert count_after == count_before + 1


class TestSignupValidation:
    """Tests for signup validation and error handling."""

    def test_signup_duplicate_returns_400(self, client, sample_emails):
        """Integration: Verify duplicate signup returns 400 Bad Request."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400

    def test_signup_duplicate_contains_error_message(self, client, sample_emails):
        """Integration: Verify error message indicates duplicate signup."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, sample_emails):
        """Integration: Verify signup to non-existent activity returns 404."""
        email = sample_emails["new_student"]
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404

    def test_signup_nonexistent_activity_contains_error_message(self, client, sample_emails):
        """Integration: Verify error message for missing activity."""
        email = sample_emails["new_student"]
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_multiple_activities_independent(self, client, sample_emails):
        """Integration: Verify signup to one activity doesn't affect others."""
        email = sample_emails["new_student"]
        
        # Sign up for Chess Club
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify not in Programming Class
        response = client.get("/activities")
        data = response.json()
        
        assert email in data["Chess Club"]["participants"]
        assert email not in data["Programming Class"]["participants"]

    def test_signup_different_students_same_activity(self, client, sample_emails):
        """Integration: Verify multiple different students can sign up for same activity."""
        email1 = sample_emails["new_student"]
        email2 = sample_emails["another_student"]
        activity = "Gym Class"
        
        # Sign up both students
        client.post(f"/activities/{activity}/signup?email={email1}")
        client.post(f"/activities/{activity}/signup?email={email2}")
        
        # Verify both are in participants
        response = client.get("/activities")
        data = response.json()
        
        assert email1 in data[activity]["participants"]
        assert email2 in data[activity]["participants"]
