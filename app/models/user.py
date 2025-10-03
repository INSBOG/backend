

from datetime import datetime
import bcrypt
from app.models.model import Model


class PasswordChangeEvent(Model):
    def __init__(self, data: dict = {}):
        self.date = data.get("date")
        self.password = data.get("password")

class User(Model):

    def __init__(self, data: dict = {}):
        self.id = data.get("_id")
        self.username = data.get("username")
        self.name = data.get("name")
        self.email = data.get("email")
        self.password = data.get("password")
        self.password_exp = data.get("password_exp") or 0
        self.admin = data.get("admin") or False
        self.temp_password = data.get("temp_password") or False
        self.password_history: list[PasswordChangeEvent] = [
            PasswordChangeEvent(event) for event in data.get("password_history", [])
        ]

    def struct_for_save(self) -> dict:
        return {
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "password": self.hash_password(),
            "password_exp": self.password_exp,
            "admin": self.admin,
            "temp_password": self.temp_password,
            "password_history": [event.to_dict() for event in self.password_history]
        }

    def hash_password(self):
        return bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()
    
    @property
    def is_password_expired(self):
        return datetime.now().timestamp() > self.password_exp
