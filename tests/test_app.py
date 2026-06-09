"""Integration tests for the Mergington High School API endpoints."""

import pytest
from src.app import app


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        # Check that Chess Club (first activity) has all required fields
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_activity_and_email(self, client):
        """Test successful signup for a valid activity and email."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "test@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        email = "newcomer@mergington.edu"
        
        # Get initial participant count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Programming Class"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response_after = client.get("/activities")
        final_count = len(response_after.json()["Programming Class"]["participants"])
        assert final_count == initial_count + 1
        assert email in response_after.json()["Programming Class"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup returns 400."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities_allowed(self, client):
        """Test that the same student can sign up for multiple activities."""
        email = "versatile@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Soccer Team"]["participants"]


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_valid_participant(self, client):
        """Test successful removal of a valid participant."""
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant
        
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_actually_removes_participant(self, client):
        """Test that removal actually removes the participant from the activity."""
        activity = "Programming Class"
        email = "emma@mergington.edu"  # Already a participant
        
        # Verify participant exists before removal
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity]["participants"]
        
        # Remove participant
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity]["participants"]

    def test_remove_nonexistent_activity_returns_404(self, client):
        """Test that removal from nonexistent activity returns 404."""
        response = client.delete(
            "/activities/Fake Club/participants/someone@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removal of nonexistent participant returns 404."""
        response = client.delete(
            "/activities/Chess Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_participant_idempotent_attempts(self, client):
        """Test that attempting to remove a participant twice fails appropriately."""
        activity = "Gym Class"
        email = "john@mergington.edu"  # Already a participant
        
        # First removal should succeed
        response1 = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response1.status_code == 200
        
        # Second removal should fail (participant no longer exists)
        response2 = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response2.status_code == 404
