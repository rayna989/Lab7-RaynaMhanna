# Author: Rayna Mhanna (AUB ID: 202404585)
# EECE 435L - Lab 7: Python testing (built on the Lab 5 Flask user app)
import sqlite3

# Path of the SQLite database file. Kept as a module variable so the tests
# can point it at a temporary file and never touch the real database.
DB_NAME = 'database.db'

# Users inserted automatically the first time the app creates the database.
INITIAL_USERS = [
    {
        "name": "Rayna Mhanna",
        "email": "rayna@example.com",
        "phone": "067765434567",
        "address": "Main Street, Beirut",
        "country": "Lebanon",
    },
    {
        "name": "Ali Haddad",
        "email": "ali.haddad@example.com",
        "phone": "03123456",
        "address": "Hamra Street, Beirut",
        "country": "Lebanon",
    },
    {
        "name": "Maya Khoury",
        "email": "maya.khoury@example.com",
        "phone": "71987654",
        "address": "Bliss Street, Beirut",
        "country": "Lebanon",
    },
]


def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_db_table():
    """Create the users table. Returns True if it was created now,
    False if it already existed (or creation failed)."""
    conn = connect_to_db()
    created = False
    try:
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        conn.commit()
        created = True
        print("User table created successfully")
    except Exception as e:
        print("User table creation failed - maybe table already exists:", e)
    finally:
        conn.close()
    return created


def init_db():
    """Create the database on first run and fill it with INITIAL_USERS.
    Running it again later does not duplicate the users."""
    if create_db_table():
        for user in INITIAL_USERS:
            insert_user(user)


def insert_user(user):
    inserted_user = {}
    conn = connect_to_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
            (user['name'], user['email'], user['phone'], user['address'], user['country'])
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception:
        conn.rollback()
        new_id = None
    finally:
        conn.close()
    if new_id:
        inserted_user = get_user_by_id(new_id)
    return inserted_user


def get_users():
    users = []
    conn = connect_to_db()
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for i in rows:
            users.append({
                "user_id": i["user_id"],
                "name": i["name"],
                "email": i["email"],
                "phone": i["phone"],
                "address": i["address"],
                "country": i["country"],
            })
    except Exception:
        users = []
    finally:
        conn.close()
    return users


def get_user_by_id(user_id):
    user = {}
    conn = connect_to_db()
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        user["user_id"] = row["user_id"]
        user["name"] = row["name"]
        user["email"] = row["email"]
        user["phone"] = row["phone"]
        user["address"] = row["address"]
        user["country"] = row["country"]
    except Exception:
        user = {}
    finally:
        conn.close()
    return user


def update_user(user):
    updated_user = {}
    conn = connect_to_db()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET name = ?, email = ?, phone = ?, address = ?, country = ? WHERE user_id = ?",
            (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"])
        )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()
    updated_user = get_user_by_id(user["user_id"])
    return updated_user


def delete_user(user_id):
    message = {}
    conn = connect_to_db()
    try:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except Exception:
        conn.rollback()
        message["status"] = "Cannot delete user"
    finally:
        conn.close()
    return message


if __name__ == "__main__":
    init_db()
