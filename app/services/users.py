

from app.models.user import User
from app.db import Database


class UsersService:

    def __init__(self):
        self.db = Database()

    def get_users(self):
        col = self.db.get_collection("users")
        users = [User(item) for item in list(col.find({}))]
        user_list = []
        for user in users:
            data = user.to_dict()
            del data["password"]
            del data["password_history"]
            user_list.append(data)

        return {"users": user_list}
