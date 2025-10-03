

from app.services.auth import AuthService


class AuthController:

    def __init__(self, auth_service: AuthService) -> None:
        self.service = auth_service

    def login(self):
        return self.service.login()

    def register(self):
        return self.service.register_user()

    def change_password(self):
        return self.service.change_password()

    def validate(self):
        return self.service.validate_session()

    def verify(self):
        return self.service.verify()

    def logout(self):
        return self.service.logout()
