from urllib.parse import quote

from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert 300 <= response.status_code < 400
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities_returns_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload


def test_signup_success_with_encoded_activity_name(client):
    activity_name = "Chess Club"
    encoded_activity = quote(activity_name, safe="")
    new_email = "new.student@mergington.edu"

    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": new_email})

    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert new_email in activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_returns_400_when_student_already_signed_up(client):
    activity_name = "Soccer Club"
    existing_email = activities[activity_name]["participants"][0]
    encoded_activity = quote(activity_name, safe="")

    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": existing_email})

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_returns_400_when_activity_is_full(client):
    activity_name = "Math Olympiad Prep"
    encoded_activity = quote(activity_name, safe="")

    activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(activities[activity_name]["max_participants"])
    ]

    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": "overflow.student@mergington.edu"},
    )

    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]


def test_signup_returns_422_when_email_is_missing(client):
    encoded_activity = quote("Art Studio", safe="")

    response = client.post(f"/activities/{encoded_activity}/signup")

    assert response.status_code == 422


def test_unregister_success_with_encoded_activity_name(client):
    activity_name = "Drama Club"
    encoded_activity = quote(activity_name, safe="")
    existing_email = activities[activity_name]["participants"][0]

    response = client.delete(f"/activities/{encoded_activity}/signup", params={"email": existing_email})

    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_returns_404_when_student_not_signed_up(client):
    encoded_activity = quote("Basketball Team", safe="")

    response = client.delete(
        f"/activities/{encoded_activity}/signup",
        params={"email": "not.signed.up@mergington.edu"},
    )

    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"]


def test_unregister_returns_422_when_email_is_missing(client):
    encoded_activity = quote("Programming Class", safe="")

    response = client.delete(f"/activities/{encoded_activity}/signup")

    assert response.status_code == 422
