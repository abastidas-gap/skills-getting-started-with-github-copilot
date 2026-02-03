"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Tests for getting activities"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Soccer Team" in activities
        assert "Basketball Club" in activities
        assert "Art Studio" in activities

    def test_activity_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        soccer = activities["Soccer Team"]
        assert "description" in soccer
        assert "schedule" in soccer
        assert "max_participants" in soccer
        assert "participants" in soccer
        assert isinstance(soccer["participants"], list)

    def test_initial_participants(self):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check that soccer team has initial participants
        assert len(activities["Soccer Team"]["participants"]) > 0
        assert "alex@mergington.edu" in activities["Soccer Team"]["participants"]


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Soccer Team" in result["message"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        email = "testsignup@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self):
        """Test signup for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_already_registered(self):
        """Test that a student can't sign up twice"""
        email = "doublecheck@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup to different activity should fail
        response2 = client.post(
            f"/activities/Debate%20Team/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_success(self):
        """Test successful unregister"""
        email = "unregistertest@mergington.edu"
        
        # First sign up
        client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        
        # Then unregister
        response = client.post(
            f"/activities/Programming%20Class/unregister?email={email}"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert email in result["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "removetest@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/Science%20Olympiad/signup?email={email}"
        )
        
        # Verify they're registered
        activities = client.get("/activities").json()
        assert email in activities["Science Olympiad"]["participants"]
        
        # Unregister
        client.post(
            f"/activities/Science%20Olympiad/unregister?email={email}"
        )
        
        # Verify they're removed
        activities = client.get("/activities").json()
        assert email not in activities["Science Olympiad"]["participants"]

    def test_unregister_not_registered(self):
        """Test unregister for student not in activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from nonexistent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRoot:
    """Tests for root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
