# Lab 7 – Python testing (Rayna Mhanna)

**Author:** Rayna Mhanna — AUB ID 202404585
**Course:** EECE 435L Software Tools Lab, Fall 2026-2027
**Repository:** https://github.com/rayna989/Lab7-RaynaMhanna
**Based on Lab 5:** https://github.com/rayna989/flask-user-app

Pytest suite for the Lab 5 Flask + SQLite user REST API.

## Files

| File | Purpose |
|------|---------|
| `db.py` | SQLite functions: `init_db`, `create_db_table`, `insert_user`, `get_users`, `get_user_by_id`, `update_user`, `delete_user` |
| `app.py` | Flask REST API (`api_get_users`, `api_get_user`, `api_add_user`, `api_update_user`, `api_delete_user`) |
| `test_user_Rayna_Mhanna.py` | The graded pytest file |
| `requirements.txt` | flask, flask-cors, pytest |

### Change from Lab 5
On its first run the app now creates `database.db` **and fills it with the
users in `db.INITIAL_USERS`** (`init_db()`), so requirement 1 can be tested.
Running it again does not insert them twice. `db.DB_NAME` holds the database
path so the tests can use a temporary database instead of the real one.

## Setup and run (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
```

## What is tested (16 tests)

| # | Requirement | Test(s) |
|---|-------------|---------|
| 1 | Database created with the specified users on first run | `test_database_created_with_initial_users`, `test_second_run_does_not_duplicate_initial_users` |
| 2 | `insert_user()` | `test_insert_user`, `test_insert_user_with_missing_field_returns_empty` |
| 3 | `get_users()` | `test_get_users` |
| 4 | `get_user_by_id()` | `test_get_user_by_id`, `test_get_user_by_id_not_found` |
| 5 | `update_user()` | `test_update_user` |
| 6 | `delete_user()` | `test_delete_user` |
| 7 | `api_get_user()` | `test_api_get_user`, `test_api_get_user_not_found`, `test_api_get_users` |
| 8 | `api_add_user()` | `test_api_add_user` |
| 9 | `api_update_user()` | `test_api_update_user` |
| 10 | `api_delete_user()` | `test_api_delete_user` |
| – | Wrong HTTP method rejected | `test_api_wrong_method_not_allowed` |

Every API test checks the **status code** and the **JSON data** sent and
received, then re-reads the data through the API to confirm the change was stored.

Each test runs on its own fresh temporary database (pytest `tmp_path` +
`monkeypatch`), set up by the `db_path` / `seeded_db` / `client` fixtures,
so the tests are independent and never modify the real `database.db`.
