"""Tests for student removal endpoint.

Covers DELETE /activities/{activity_name}/signup endpoint.
Tests successful removal, validation, and error handling.
"""

import pytest


class TestRemovalSuccessPath:
    """Tests for successful participant removal operations."""

    def test_remove_participant_returns_200(self, client, sample_emails):
        """Integration: Verify DELETE removal returns 200 OK."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

    def test_remove_participant_returns_success_message(self, client, sample_emails):
        """Integration: Verify removal response contains success message."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_remove_participant_deletes_from_activity(self, client, sample_emails):
        """Integration: Verify participant is removed from the activity."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        # Verify participant is initially present
        response_before = client.get("/activities")
        assert email in response_before.json()[activity]["participants"]
        
        # Remove participant
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Verify participant is removed
        response_after = client.get("/activities")
        assert email not in response_after.json()[activity]["participants"]

    def test_remove_decreases_participant_count(self, client, sample_emails):
        """Unit: Verify removal decreases the participant count."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        # Get initial count
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Remove participant
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Get updated count
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])
        
        assert count_after == count_before - 1

    def test_remove_not_registered_returns_400(self, client, sample_emails):
        """Integration: Verify removing non-registered participant returns 400."""
        email = sample_emails["new_student"]
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400

    def test_remove_not_registered_contains_error_message(self, client, sample_emails):
        """Integration: Verify error message for non-registered participant."""
        email = sample_emails["new_student"]
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()

    def test_remove_from_nonexistent_activity_returns_404(self, client, sample_emails):
        """Integration: Verify removal from non-existent activity returns 404."""
        email = sample_emails["existing_chess"]
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404

    def test_remove_from_nonexistent_activity_contains_error_message(self, client, sample_emails):
        """Integration: Verify error message for non-existent activity."""
        email = sample_emails["existing_chess"]
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestRemovalStateConsistency:
    """Tests for state consistency across signup and removal operations."""

    def test_remove_then_signup_again_works(self, client, sample_emails):
        """Integration: Verify a removed participant can sign up again."""
        email = sample_emails["existing_chess"]
        activity = "Chess Club"
        
        # Remove the participant
        client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Verify they're removed
        response_after_remove = client.get("/activities")
        assert email not in response_after_remove.json()[activity]["participants"]
        
        # Sign them up again
        response_signup = client.post(f"/activities/{activity}/signup?email={email}")
        assert response_signup.status_code == 200
        
        # Verify they're signed up again
        response_final = client.get("/activities")
        assert email in response_final.json()[activity]["participants"]

    def test_remove_from_one_activity_doesnt_affect_others(self, client, sample_emails):
        """Integration: Verify removal from one activity doesn't affect others."""
        email = sample_emails["existing_chess"]
        
        # Sign up for Programming Class
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Remove from Chess Club
        client.delete(f"/activities/Chess Club/signup?email={email}")
        
        # Verify removed from Chess Club but still in Programming Class
        response = client.get("/activities")
        data = response.json()
        
        assert email not in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]

    def test_remove_one_participant_leaves_others(self, client, sample_emails):
        """Integration: Verify removing one participant doesn't affect others."""
        email_to_remove = sample_emails["existing_chess"]
        email_to_keep = "daniel@mergington.edu"  # Other participant in Chess Club
        activity = "Chess Club"
        
        # Remove one participant
        client.delete(f"/activities/{activity}/signup?email={email_to_remove}")
        
        # Verify removed participant is gone, but other remains
        response = client.get("/activities")
        data = response.json()
        
        assert email_to_remove not in data[activity]["participants"]
        assert email_to_keep in data[activity]["participants"]
