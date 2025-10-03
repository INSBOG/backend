
from app.services.users import UsersService

class UsersController:
    def __init__(self, user_service: UsersService):
        self.user_service = user_service