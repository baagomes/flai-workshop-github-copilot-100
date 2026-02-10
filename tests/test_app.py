"""Tests for the High School Management System API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original activities
    original_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball team for interschool tournaments",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performance and acting workshops",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Society": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through hands-on experiments",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Reset activities dictionary before test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivities:
    """Test the activities endpoints"""
    
    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have all activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignup:
    """Test the signup endpoints"""
    
    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup", params={"email": "student@mergington.edu"})
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # michael@mergington.edu is already in Chess Club
        response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        student_email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post("/activities/Chess Club/signup", params={"email": student_email})
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post("/activities/Programming Class/signup", params={"email": student_email})
        assert response2.status_code == 200
        
        # Verify the student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email in activities_data["Chess Club"]["participants"]
        assert student_email in activities_data["Programming Class"]["participants"]


class TestUnregister:
    """Test the unregister endpoints"""
    
    def test_unregister_existing_student(self, client):
        """Test unregistering a student who is registered"""
        # michael@mergington.edu is already in Chess Club
        response = client.post("/activities/Chess Club/unregister", params={"email": "michael@mergington.edu"})
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post("/activities/Nonexistent Club/unregister", params={"email": "student@mergington.edu"})
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_student_not_registered(self, client):
        """Test unregistering a student who is not registered for the activity"""
        response = client.post("/activities/Chess Club/unregister", params={"email": "notstudent@mergington.edu"})
        assert response.status_code == 400
        
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_and_resignup(self, client):
        """Test that a student can unregister and then sign up again"""
        student_email = "flexiblestudent@mergington.edu"
        
        # First, sign up
        response1 = client.post("/activities/Chess Club/signup", params={"email": student_email})
        assert response1.status_code == 200
        
        # Then, unregister
        response2 = client.post("/activities/Chess Club/unregister", params={"email": student_email})
        assert response2.status_code == 200
        
        # Finally, sign up again
        response3 = client.post("/activities/Chess Club/signup", params={"email": student_email})
        assert response3.status_code == 200
        
        # Verify the student is registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert student_email in activities_data["Chess Club"]["participants"]
