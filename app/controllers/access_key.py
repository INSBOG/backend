from datetime import datetime, timedelta
import json
import os

from bson import Binary, ObjectId
from flask import jsonify, make_response, request
from itsdangerous import base64_decode
import jwt
from webauthn import (generate_registration_options, options_to_json,
                      verify_authentication_response,
                      verify_registration_response)

from webauthn.helpers.structs import (PublicKeyCredentialDescriptor,
                                      PublicKeyCredentialRequestOptions,
                                      PublicKeyCredentialType)

from app.db import Database
from app.models.user import User


class AccessKeyController:

    def get_register_options(self):
        data = request.get_json()
        options = generate_registration_options(
            rp_id=data.get("rp_id"),
            rp_name=data.get("rp_name"),
            user_id=data.get("user_id", "").encode("utf-8"),
            user_name=data.get("user_name"),
        )

        db = Database()
        db.get_collection("users").update_one({"_id": ObjectId(data.get("user_id"))}, {"$set": {
            "challenge": options.challenge,
        }})
        db.close()

        return json.loads(options_to_json(options))

    def handle_register(self):
        try:
            db = Database()
            data = request.get_json()
            rp_id = data.get("rp_id", "")
            user_name = data.get("user_name", {})

            user = db.get_collection("users").find_one({"username": user_name})

            verification = verify_registration_response(
                credential=data.get("credential"),
                expected_rp_id=rp_id,
                expected_origin=f"http://{rp_id}:81",
                expected_challenge=user.get("challenge"),
            )

            db.get_collection("users").update_one({"username": user_name}, {"$set": {
                "public_key": verification.credential_public_key,
                "credential_id": verification.credential_id,
            }})

            return {"message": "Registration successful"}
        except Exception as e:
            return {"error": str(e)}, 500

    def get_auth_options(self):
        data = request.get_json()
        db = Database()

        if not data.get("username"):
            return {"error": "Username not provided"}, 400

        user = db.get_collection("users").find_one({
            "username": data.get("username")
        })

        if not user:
            return {"error": "User not found"}, 404

        options = PublicKeyCredentialRequestOptions(
            challenge=user.get("challenge", ""),
            rp_id="localhost",
            allow_credentials=[
                PublicKeyCredentialDescriptor(
                    type=PublicKeyCredentialType.PUBLIC_KEY,
                    id=user.get("credential_id"),
                )
            ]
        )

        return json.loads(options_to_json(options))

    def handle_auth(self):
        try:
            data = request.get_json()
            db = Database()

            binary_cred = Binary(base64_decode(data.get("rawId")))

            user = db.get_collection("users").find_one({"credential_id": binary_cred})

            verify_authentication_response(
                credential=data,
                expected_rp_id="localhost",
                expected_origin="http://localhost:81",
                expected_challenge=user.get("challenge"),
                credential_current_sign_count=0,
                credential_public_key=user.get("public_key"),
            )

            usr = User(data=user).to_dict(["password", "password_history"])

            usr.update({"exp": datetime.utcnow() + timedelta(minutes=15)})
        
            response_token = jwt.encode(usr, os.getenv("JWT_SECRET"), algorithm="HS256")
            response = make_response(jsonify({"status_code": 200, "message": "Logged in"}))
            response.set_cookie("token", response_token, max_age=3600,
                                    httponly=True, secure=True, samesite="None")
            
            return response
        except Exception as e:
            return {"error": str(e)}, 500