"""
Tests for the High School Management System API

Tests cover all API endpoints with both success and error scenarios.
Following AAA (Arrange-Act-Assert) pattern for clarity.
"""
from fastapi.testclient import TestClient


# ===========================
# GET /activities Tests
# ===========================

def test_get_activities_success(client):
    """
    Test that GET /activities returns all activities with correct structure
    """
    # Arrange: (client fixture provides pre-loaded activities)
    
    # Act: Make GET request
    response = client.get("/activities")
    
    # Assert: Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Verify we have all 9 activities
    assert len(data) == 9
    
    # Verify a sample activity has correct structure
    assert "Chess Club" in data
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2


# ===========================
# POST /activities/{activity_name}/signup Tests
# ===========================

def test_signup_success(client):
    """
    Test successful signup for an activity
    """
    # Arrange: Use Tennis Club which has 0 participants
    activity_name = "Tennis Club"
    email = "test.student@mergington.edu"
    
    # Act: Sign up student
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert: Verify success
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify student was added to participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_activity_not_found(client):
    """
    Test that signing up for a non-existent activity returns 404
    """
    # Arrange: Use non-existent activity
    activity_name = "Nonexistent Activity"
    email = "test.student@mergington.edu"
    
    # Act: Attempt to sign up
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert: Verify 404 error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_activity_full(client):
    """
    Test that signing up for a full activity returns 400
    """
    # Arrange: Fill Tennis Club (max 10 participants)
    activity_name = "Tennis Club"
    
    # Add 10 participants to fill it up
    for i in range(10):
        client.post(f"/activities/{activity_name}/signup?email=student{i}@mergington.edu")
    
    # Act: Try to add one more student
    response = client.post(
        f"/activities/{activity_name}/signup?email=overflow@mergington.edu"
    )
    
    # Assert: Verify 400 error for full activity
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "full" in data["detail"].lower()


def test_signup_already_registered(client):
    """
    Test that signing up the same student twice returns 400
    """
    # Arrange: Sign up a student first
    activity_name = "Tennis Club"
    email = "duplicate@mergington.edu"
    
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act: Try to sign up the same student again
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    
    # Assert: Verify 400 error for duplicate signup
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


# ===========================
# DELETE /activities/{activity_name}/unregister Tests
# ===========================

def test_unregister_success(client):
    """
    Test successful unregistration from an activity
    """
    # Arrange: Chess Club has michael@mergington.edu registered
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Verify student is currently registered
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]
    
    # Act: Unregister the student
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert: Verify success
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify student was removed from participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_activity_not_found(client):
    """
    Test that unregistering from a non-existent activity returns 404
    """
    # Arrange: Use non-existent activity
    activity_name = "Nonexistent Activity"
    email = "test.student@mergington.edu"
    
    # Act: Attempt to unregister
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert: Verify 404 error
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered(client):
    """
    Test that unregistering a student who isn't signed up returns 400
    """
    # Arrange: Use Tennis Club which has no participants
    activity_name = "Tennis Club"
    email = "notregistered@mergington.edu"
    
    # Act: Try to unregister student who isn't signed up
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )
    
    # Assert: Verify 400 error
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()


# ===========================
# GET / Root Redirect Test
# ===========================

def test_root_redirect(client):
    """
    Test that root endpoint redirects to static/index.html
    """
    # Arrange: (client fixture provides app)
    
    # Act: Make GET request to root (follow_redirects=False to check redirect)
    response = client.get("/", follow_redirects=False)
    
    # Assert: Verify redirect
    assert response.status_code == 307  # FastAPI uses 307 for RedirectResponse
    assert "location" in response.headers
    assert "/static/index.html" in response.headers["location"]
