import os

from app.models.user import User
from app.services.auth import AuthService

service = AuthService()

class TestAuthService:

    @staticmethod
    def test_check_password_ok():
        usr = User()
        usr.password = "1234"
        hashed_password = usr.hash_password()

        service = AuthService()
        result = service.check_password("1234", hashed_password)

        assert result is True

    @staticmethod
    def test_check_password_error():
        usr = User()
        usr.password = "1234"
        hashed_password = usr.hash_password()

        result = service.check_password("aaaa", hashed_password)

        assert result is False

    @staticmethod
    def test_generate_token():
        os.environ["JWT_SECRET"] = "mysecret"
        token = service.create_access_token({
            "name": "test"
        })
        assert isinstance(token, str)
        assert token is not None

