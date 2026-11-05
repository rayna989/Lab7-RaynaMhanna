# Author: Rayna Mhanna (AUB ID: 202404585)
# EECE 435L - Lab 7: Python testing (built on the Lab 5 Flask user app)
from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_users, get_user_by_id, insert_user, update_user, delete_user, init_db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# First run: creates database.db and inserts the initial users.
init_db()


@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())


@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))


@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user = request.get_json()
    return jsonify(insert_user(user))


@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))


@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))


if __name__ == "__main__":
    app.run(debug=True)
