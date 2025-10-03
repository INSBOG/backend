import os
from datetime import datetime, timedelta

import jwt
import json

import requests
from bcrypt import checkpw
from bson import ObjectId
from app.constants import logger
from app.db import Database
from flask import jsonify, make_response, request
from app.models.user import PasswordChangeEvent, User

SITE_SECRET = os.getenv("SITE_SECRET")

class AuthService:

    def __init__(self):
        self.db = Database()

    def check_password(self, password: str, hashed_password: str):
        return checkpw(password.encode(), hashed_password.encode())

    def create_access_token(self, data: dict):
        data.update({"exp": datetime.utcnow() + timedelta(minutes=15)})
        return jwt.encode(data, os.environ["JWT_SECRET"], algorithm="HS256")

    def register_user(self):
        user = request.get_json()
        usr = User(data=user)
        data = usr.struct_for_save()

        col = self.db.get_collection("users")

        if col.find_one({
            "$or": [
                {"username": data["username"]},
                {"email": data["email"]}
            ]
        }):
            return {"error": "User already exists"}, 409

        result = col.insert_one(data)

        creator = request.user["username"]

        logger.info(f"{creator} registered a new user {usr.username}")

        return {"_id": str(result.inserted_id)}

    def login(self):
        try:
            body = request.get_json()
            username_or_email = body["username"]
            password = body["password"]

            # Buscar usuario por username o email
            col = self.db.get_collection("users")
            user_data = col.find_one({
                "$or": [
                    {"username": username_or_email},
                    {"email": username_or_email}
                ]
            })

            if not user_data:
                return {"status_code": 404, "error": "User not found"}, 404

            user = User(data=user_data)

            # Validar la contraseña
            if not self.check_password(password, user.password):
                return {"status_code": 401, "error": "Invalid password"}, 401

            # Generar token y respuesta
            response_token = self.create_access_token(user.to_dict(["password", "password_history"]))
            response = make_response(jsonify({"status_code": 200, "message": "Logged in"}))
            response.set_cookie("token", response_token, max_age=3600,
                                httponly=True, secure=True, samesite="None")

            logger.info(f"User {user.username} logged in")
            return response

        except KeyError as e:
            logger.error(f"Missing key: {str(e)}")
            return {"status_code": 400, "error": "Bad request"}, 400
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return {"status_code": 500, "error": "Internal server error"}, 500


    def change_password(self):
        body = request.get_json()

        user_id = body.get("user_id")
        new_password = body.get("new_password")
        old_password = body.get("old_password")

        col = self.db.get_collection("users")
        user_data = col.find_one({"_id": ObjectId(user_id)})

        if not user_data:
            return {"status_code": 404, "error": "User not found"}, 404

        user = User(data=user_data)

        # Check password validity
        if (not user.is_password_expired and not user.temp_password) and not self.check_password(old_password, user.password):
            return {"status_code": 401, "error": "Invalid password"}, 401

        # Password history check
        limit_date = datetime.now() - timedelta(days=90)
        if any(
            self.check_password(new_password, event.password) and 
            datetime.strptime(event.date, "%Y-%m-%d %H:%M:%S") > limit_date 
            for event in user.password_history
        ):
            return {"status_code": 400, "error": "Password already used"}, 400

        # Update password and history
        user.password = new_password
        hashed_password = user.hash_password()
        user.password_history.append(
            PasswordChangeEvent({
                "date": datetime.now(),
                "password": hashed_password,
                "user": user.id
            })
        )
        user.password_exp = (datetime.now() + timedelta(days=30)).timestamp()
        user.temp_password = False

        # Update user document in the database
        col.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password": hashed_password,
                    "password_exp": user.password_exp,
                    "temp_password": user.temp_password,
                    "password_history": [event.to_dict() for event in user.password_history]
                }
            }
        )

        # Prepare response
        response_token = self.__generate_new_token(user)
        response = make_response(jsonify({
            "status_code": 200,
            "message": "Password updated",
        }))
        response.set_cookie("token", response_token, max_age=3600,
                            httponly=True, secure=True, samesite="None")

        logger.info(f"User {user.username} changed password")

        return response

    def validate_session(self):
        token = request.cookies.get("token")
        try:
            data = jwt.decode(
                token, os.environ["JWT_SECRET"], algorithms=["HS256"])
            return {"status_code": 200, "data": data}
        except jwt.ExpiredSignatureError:
            return {"status_code": 401, "error": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"status_code": 401, "error": "Invalid token"}, 401

    def logout(self):
        user = request.user

        response = make_response(jsonify({
            "status_code": 200,
            "message": "Logged out",
        }))

        response.set_cookie("token", "", expires=0, httponly=True, samesite="None", secure=True)
        logger.info(f"User {user['username']} logged out")

        return response

    def verify(self):
        body = json.loads(request.data)
        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        data = {
            "secret": SITE_SECRET,
            "response": body["token"]
        }
        r = requests.post(url, data=data)
        result = r.json()

        return jsonify(result)

    def __generate_new_token(self, user: User):
        payload = user.to_dict()
        del payload["password"]
        del payload["password_history"]
        payload.update({"exp": datetime.utcnow() + timedelta(minutes=15)})

        token = jwt.encode(
            payload, os.environ["JWT_SECRET"], algorithm="HS256")
        return token
