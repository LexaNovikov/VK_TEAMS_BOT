import json
FILE = 'users.json'
POSTS_FILE = 'posts.json'
def load_data():
    try:
        with open(FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except(FileNotFoundError, json.JSONDecodeError):
        return {"users":{}}
def load_posts_data():
    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except(FileNotFoundError, json.JSONDecodeError):
        return {"users":{}}
def write_posts_data(data):
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
def write_data(data):
    with open(FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
def save_user(user_id):
    data = load_data()
    data["users"][user_id]={}
    data["users"][user_id]["status"] = "user"
    data["users"][user_id]["name"] = False
    data["users"][user_id]["sex"] = False
    data["users"][user_id]["age"] = False
    data["users"][user_id]["registered"] = False
    write_data(data)
def save_admin(user_id):
    data = load_data()
    data["users"][user_id] = {}
    data["users"][user_id]["status"] = "admin"
    data["users"][user_id]["name"] = False
    data["users"][user_id]["sex"] = False
    data["users"][user_id]["age"] = False
    data["users"][user_id]["registered"] = False
    write_data(data)


