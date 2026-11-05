# test_user_Rayna_Mhanna.py
# Author: Rayna Mhanna (AUB ID: 202404585)
# EECE 435L - Lab 7: Python testing
#
# Tests the Lab 5 Flask user app (db.py + app.py):
#   1. The database is created with the specified users when the app first runs
#   2. insert_user()       3. get_users()        4. get_user_by_id()
#   5. update_user()       6. delete_user()
#   7. api_get_user()      8. api_add_user()     9. api_update_user()
#  10. api_delete_user()
# For every API method we check the response status code and the data
# sent (uploaded) / received (downloaded).
#
# Run from the project folder with:  pytest -v

import os
import sqlite3

import pytest
from flask import json

import db
from app import app


# ---------------------------------------------------------------- fixtures

@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Point db.py at a fresh, empty database file for each test,
    so the tests never touch the real database.db."""
    path = str(tmp_path / "test_database.db")
    monkeypatch.setattr(db, "DB_NAME", path)
    return path


@pytest.fixture
def seeded_db(db_path):
    """A database created the same way the app does on its first run."""
    db.init_db()
    return db_path


@pytest.fixture
def client(seeded_db):
    """Flask test client working on the seeded test database."""
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def new_user():
    return {
        "name": "Rayna Mhanna Test",
        "email": "rayna.test@mail.aub.edu",
        "phone": "70111222",
        "address": "AUB Campus, Beirut",
        "country": "Lebanon",
    }


def without_id(user):
    return {k: v for k, v in user.items() if k != "user_id"}


# ------------------------------------------- 1. database created with users

def test_database_created_with_initial_users(db_path):
    assert not os.path.exists(db_path)          # nothing before the first run

    db.init_db()                                # what app.py does on start

    assert os.path.exists(db_path)              # database file was created
    conn = sqlite3.connect(db_path)
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    conn.close()
    assert "users" in tables                    # users table was created

    users = db.get_users()
    assert len(users) == len(db.INITIAL_USERS)  # all specified users inserted
    assert [without_id(u) for u in users] == db.INITIAL_USERS
    assert [u["user_id"] for u in users] == [1, 2, 3]
    assert users[0]["name"] == "Rayna Mhanna"


def test_second_run_does_not_duplicate_initial_users(seeded_db):
    db.init_db()                                # app started a second time
    assert len(db.get_users()) == len(db.INITIAL_USERS)


# ------------------------------------------------------------ 2. insert_user

def test_insert_user(seeded_db, new_user):
    inserted = db.insert_user(new_user)

    assert inserted["user_id"] == 4             # next id after the 3 seeds
    assert without_id(inserted) == new_user
    assert len(db.get_users()) == 4
    assert db.get_user_by_id(4) == inserted     # really stored in the DB


def test_insert_user_with_missing_field_returns_empty(seeded_db):
    assert db.insert_user({"name": "No Email"}) == {}
    assert len(db.get_users()) == 3             # nothing was added


# -------------------------------------------------------------- 3. get_users

def test_get_users(seeded_db):
    users = db.get_users()

    assert isinstance(users, list)
    assert len(users) == 3
    for user in users:
        assert set(user) == {"user_id", "name", "email",
                             "phone", "address", "country"}
    assert [u["email"] for u in users] == [u["email"] for u in db.INITIAL_USERS]


# --------------------------------------------------------- 4. get_user_by_id

def test_get_user_by_id(seeded_db):
    user = db.get_user_by_id(2)

    assert user["user_id"] == 2
    assert without_id(user) == db.INITIAL_USERS[1]


def test_get_user_by_id_not_found(seeded_db):
    assert db.get_user_by_id(999) == {}


# ------------------------------------------------------------ 5. update_user

def test_update_user(seeded_db):
    changes = {
        "user_id": 1,
        "name": "Rayna Mhanna",
        "email": "rayna.mhanna@mail.aub.edu",
        "phone": "76000111",
        "address": "Bliss Street, Beirut",
        "country": "Lebanon",
    }
    updated = db.update_user(changes)

    assert updated == changes
    assert db.get_user_by_id(1) == changes      # change saved in the DB
    assert db.get_user_by_id(2) == {"user_id": 2, **db.INITIAL_USERS[1]}  # others untouched


# ------------------------------------------------------------ 6. delete_user

def test_delete_user(seeded_db):
    result = db.delete_user(3)

    assert result == {"status": "User deleted successfully"}
    assert db.get_user_by_id(3) == {}
    assert len(db.get_users()) == 2
    assert 3 not in [u["user_id"] for u in db.get_users()]


# ----------------------------------------------- 7. api_get_user (+ all users)

def test_api_get_users(client):
    response = client.get('/api/users')
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert isinstance(data, list)               # array of dictionaries
    assert len(data) == 3
    assert "Rayna Mhanna" in str(response.data)


def test_api_get_user(client):
    response = client.get('/api/users/1')
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {"user_id": 1, **db.INITIAL_USERS[0]}


def test_api_get_user_not_found(client):
    response = client.get('/api/users/999')

    assert response.status_code == 200
    assert json.loads(response.get_data(as_text=True)) == {}


# ----------------------------------------------------------- 8. api_add_user

def test_api_add_user(client, new_user):
    response = client.post(
        '/api/users/add',
        data=json.dumps(new_user),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data["user_id"] == 4
    assert without_id(data) == new_user         # uploaded data came back

    check = client.get('/api/users/4')          # and is downloadable again
    assert check.status_code == 200
    assert json.loads(check.get_data(as_text=True)) == data
    assert len(json.loads(client.get('/api/users').get_data(as_text=True))) == 4


# -------------------------------------------------------- 9. api_update_user

def test_api_update_user(client):
    changes = {
        "user_id": 2,
        "name": "Ali Haddad",
        "email": "ali.haddad@mail.aub.edu",
        "phone": "03999888",
        "address": "Verdun, Beirut",
        "country": "Lebanon",
    }
    response = client.put(
        '/api/users/update',
        data=json.dumps(changes),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == changes

    check = client.get('/api/users/2')
    assert json.loads(check.get_data(as_text=True)) == changes


# ------------------------------------------------------- 10. api_delete_user

def test_api_delete_user(client):
    response = client.delete('/api/users/delete/3')
    data = json.loads(response.get_data(as_text=True))

    assert response.status_code == 200
    assert data == {"status": "User deleted successfully"}

    check = client.get('/api/users/3')
    assert json.loads(check.get_data(as_text=True)) == {}
    remaining = json.loads(client.get('/api/users').get_data(as_text=True))
    assert [u["user_id"] for u in remaining] == [1, 2]


def test_api_wrong_method_not_allowed(client):
    assert client.delete('/api/users/1').status_code == 405     # GET only
    assert client.get('/api/users/delete/1').status_code == 405  # DELETE only
    assert client.post('/api/users').status_code == 405          # GET only
