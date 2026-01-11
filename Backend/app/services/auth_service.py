import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
USER_FILE = os.path.join(BASE_DIR, "Dataset", "users.json")

def authenticate(username, password):
    if not os.path.exists(USER_FILE):
        return None

    with open(USER_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    for user in users:
        if user["username"] == username and user["password"] == password:
            return {
                "username": user["username"],
                "role": user["role"]
            }

    return None
