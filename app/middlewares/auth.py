

import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from app.constants import logger
from flask import make_response, request


def auth_required(f):
    @wraps(f)
    def session_validator(*args, **kwargs):
        token = request.cookies.get("token")
        secret = os.environ["JWT_SECRET"]
        excluded = ["change-password", "logout"]

        if not token:
            return {"error": "Unauthorized"}, 401


        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])

            payload.update({"exp": datetime.utcnow() + timedelta(minutes=15)})

            request.user = payload

            excluded = next((endpoint for endpoint in excluded if endpoint in request.url), None)
            if excluded:
                return f(*args, **kwargs)

            token = jwt.encode(payload, secret, algorithm="HS256")

            response = make_response(f(*args, **kwargs))
            response.set_cookie("token", token, max_age=3600, httponly=True, secure=True, samesite="None")

            return response
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            return {"error": "Token expired"}, 401
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            return {"error": "Invalid token"}, 401

    return session_validator
