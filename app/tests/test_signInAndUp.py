from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routes.signInAndUp import router, get_db

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_email_for_verification_code(monkeypatch):
    def fake_randint(a, b): return 123456
    monkeypatch.setattr("app.routes.signInAndUp.random.randint", fake_randint)

    class FakeRedis:
        def __init__(self): self.store = {}
        def setex(self, key, ttl, value): self.store[key] = value
        def get(self, key): return self.store.get(key)
    fake_redis = FakeRedis()
    monkeypatch.setattr("app.routes.signInAndUp.r", fake_redis)

    class FakeSMTP:
        def starttls(self): pass
        def login(self, sender, password): pass
        def sendmail(self, sender, receiver, message): return True
        def quit(self): pass
    monkeypatch.setattr("app.routes.signInAndUp.sever", FakeSMTP())

    resp = client.post("/emailForVerificationCode", json={"email": "test@example.com"})
    assert resp.status_code == 200
    assert resp.json()["ok"] == "True"
    assert "test@example.com" in fake_redis.store


def test_sign_up_success(monkeypatch):
    
    class FakeRedis:
        def __init__(self): self.store = {"user@example.com": "hashed_123456"}
        def get(self, key): return self.store.get(key)
    monkeypatch.setattr("app.routes.signInAndUp.r", FakeRedis())

    class FakeHash:
        def hexdigest(self): return "hashed_123456"
    monkeypatch.setattr("app.routes.signInAndUp.hashlib.sha256", lambda x: FakeHash())

    
    class FakeDB:
        def __init__(self):
            self._state = 0
            self._user_obj = None
        def query(self, model): return self
        def filter(self, cond): return self
        def first(self):
            if self._state == 0: 
                self._state = 1
                return None
            if self._state == 1: 
                self._state = 2
                return None
            return self._user_obj 
        def add(self, obj):
            if "user_name" in dir(obj) and self._user_obj is None:
                self._user_obj = obj
                self._state = 3
        def commit(self): pass
        def refresh(self, obj):
            if obj == self._user_obj:
                obj.id = 1

    def fake_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = fake_get_db

    
    payload = {
        "username": "newuser",
        "email": "user@example.com",
        "passwordPlainText": "123456",
        "verificationCode": "123456",
    }
    resp = client.post("/signUp", json=payload)


    app.dependency_overrides = {}

   
    assert resp.status_code == 200
    assert resp.json()["status"] == "SuccessfullySignedUp"


def test_sign_up_incorrect_code(monkeypatch):
    class FakeRedis:
        def get(self, key): return "right_code"
    monkeypatch.setattr("app.routes.signInAndUp.r", FakeRedis())

    def fake_get_db():
        yield None
    monkeypatch.setattr("app.routes.signInAndUp.get_db", fake_get_db)

    class FakeHash:
        def hexdigest(self): return "wrong_code"
    monkeypatch.setattr("app.routes.signInAndUp.hashlib.sha256", lambda x: FakeHash())

    payload = {
        "username": "wrongcodeuser",
        "email": "wrong@example.com",
        "passwordPlainText": "123456",
        "verificationCode": "badcode",
    }
    resp = client.post("/signUp", json=payload)
    assert resp.json()["status"] == "incorrectVerificationCode"


def test_sign_up_email_exists(monkeypatch):
    class FakeRedis:
        def get(self, key): return "correct_code"
    monkeypatch.setattr("app.routes.signInAndUp.r", FakeRedis())

    class FakeDB:
        def query(self, model): return self
        def filter(self, cond): return self
        def first(self):
            return type("UserObj", (), {"id": 99, "email": "dup@example.com"})()
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass

    def fake_get_db():
        yield FakeDB()
    monkeypatch.setattr("app.routes.signInAndUp.get_db", fake_get_db)

    class FakeHash:
        def hexdigest(self): return "correct_code"
    monkeypatch.setattr("app.routes.signInAndUp.hashlib.sha256", lambda x: FakeHash())

    payload = {
        "username": "userexists",
        "email": "dup@example.com",
        "passwordPlainText": "123456",
        "verificationCode": "123456",
    }
    resp = client.post("/signUp", json=payload)
    assert resp.json()["status"] == "emailAlreadyExists"


def test_sign_in_success(monkeypatch):
    class FakeUser:
        def __init__(self):
            self.id = 1
            self.user_name = "loginuser"
            self.email = "login@example.com"
            self.hashed_password = "$2b$12$123fakehash"  # str, .encode(...) in code

    class FakeDB:
        def query(self, model): return self
        def filter(self, cond): return self
        def first(self): return FakeUser()  # user exists
        def join(self, *args, **kwargs): return self
        def filter_by(self, *args, **kwargs): return self
        def all(self): return [("NormalUser",)]  # roles list

    def fake_get_db():
        yield FakeDB()
    app.dependency_overrides[get_db] = fake_get_db

    monkeypatch.setattr("app.routes.signInAndUp.bcrypt.checkpw", lambda p, h: True)
    monkeypatch.setattr("app.routes.signInAndUp.create_access_token", lambda **kwargs: "fake.jwt.token")

    payload = {"email": "login@example.com", "passwordPlainText": "123456"}
    resp = client.post("/signIn", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["access_token"] == "fake.jwt.token"


def test_sign_in_wrong_password(monkeypatch):
    class FakeUser:
        def __init__(self):
            self.id = 1
            self.user_name = "loginuser"
            self.email = "login@example.com"
            self.hashed_password = "$2b$12$123fakehash"
    class FakeDB:
        def query(self, model): return self
        def filter(self, cond): return self
        def first(self): return FakeUser()

    def fake_get_db():
        yield FakeDB()
    monkeypatch.setattr("app.routes.signInAndUp.get_db", fake_get_db)

    monkeypatch.setattr("app.routes.signInAndUp.bcrypt.checkpw", lambda p, h: False)

    payload = {"email": "login@example.com", "passwordPlainText": "wrongpw"}
    resp = client.post("/signIn", json=payload)
    assert resp.json()["status"] == "emailAndPasswordDoesNotMatch"
