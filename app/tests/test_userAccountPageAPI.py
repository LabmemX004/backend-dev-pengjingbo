import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

from app.routes.userAccountPageAPI import router

from app.routes.userAccountPageAPI import get_db
from app.auth.jwt_bearer import jwtBearer, get_current_user

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def fake_get_current_user_id_1():
    return {"user_id": 1, "username": "testuser", "roles": ["NormalUser"]}

def fake_get_current_user_id_99():
    return {"user_id": 99, "username": "attacker", "roles": ["NormalUser"]}

def fake_jwt_bearer_pass():
    pass

def test_get_user_info_success():
    class MockUser:
        id = 1
        user_name = "testuser"
        email = "test@example.com"
        created_at = datetime.now()

    class FakeDB:
        def query(self, model):
            return self
        def filter(self, cond):
            return self
        def first(self):
            return MockUser()
        
        def scalars(self, select_statement):
            return self
        def all(self):
            return ["NormalUser", "EventProvider"]
        
    def fake_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = fake_get_current_user_id_1
    app.dependency_overrides[jwtBearer] = fake_jwt_bearer_pass

    resp = client.get("/getUserInfo/1")

    app.dependency_overrides = {}

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 1
    assert data["user_name"] == "testuser"
    assert "roles" in data
    assert data["roles"] == ["NormalUser", "EventProvider"]

def test_get_user_info_forbidden():
    app.dependency_overrides[get_current_user] = fake_get_current_user_id_99
    app.dependency_overrides[jwtBearer] = fake_jwt_bearer_pass

    resp = client.get("/getUserInfo/1")
    app.dependency_overrides = {} 

    assert resp.status_code == 403
    assert resp.json()["detail"] == "User ID does not match the token"

def test_get_user_info_not_found():
    class FakeDB:
        def query(self, model): return self
        def filter(self, cond): return self
        def first(self):
            
            return None
        
        
        def scalars(self, select_statement):
            return self 
        def all(self):
            return [] 
            
    def fake_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = fake_get_current_user_id_1
    app.dependency_overrides[jwtBearer] = fake_jwt_bearer_pass

    resp = client.get("/getUserInfo/1")
    app.dependency_overrides = {} 

    # 现在路由代码会成功运行到 "if user is None:" 那一行
    # 并正确返回 404
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"


def test_get_user_booked_events_success():
    class MockBooking:
        id = 100
        number_of_tickets = 2
        status = "Confirmed"
        ticket_code = "ABC123"

    class MockEvent:
        id = 200
        event_title = "Test Event"
        event_type = "Music"
        event_provider_id = 5
        event_start_date_and_time = datetime.now()
        event_duration_in_minutes = 120
        event_location = "Online"
        event_imageUrl = "http://example.com/image.png"
        event_description = "A great event"

    class FakeDB:
        def query(self, model, *args): return self
        def join(self, *args, **kwargs): return self
        def filter(self, cond): return self
        def order_by(self, cond): return self
        def all(self):
            return [(MockBooking(), MockEvent())]
        
    def fake_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = fake_get_current_user_id_1
    app.dependency_overrides[jwtBearer] = fake_jwt_bearer_pass

    resp = client.get("/getUserBookedEventsInfo/1")
    app.dependency_overrides = {} 

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["booking_id"] == 100
    assert data[0]["event_title"] == "Test Event"


def test_get_events_provided_by_user_success():
    class MockEvent:
        id = 300
        event_title = "My Provided Event"
        event_type = "Workshop"
        event_provider_id = 1 
        event_start_date_and_time = datetime.now()
        event_duration_in_minutes = 90
        event_location = "Campus"
        event_imageUrl = "http://example.com/image2.png"
        event_description = "A workshop event"
        event_total_ticket_number = 100
        event_remaining_ticket_number = 50

    class FakeDB:
        def query(self, model): return self
        def filter(self, cond): return self
        def order_by(self, cond): return self
        def all(self):
            return [MockEvent()]
        
    def fake_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = fake_get_db
    app.dependency_overrides[get_current_user] = fake_get_current_user_id_1
    app.dependency_overrides[jwtBearer] = fake_jwt_bearer_pass

    resp = client.get("/getEventsThatProvidedByTheUser/1")
    app.dependency_overrides = {} 

    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["event_id"] == 300
    assert data[0]["event_title"] == "My Provided Event"