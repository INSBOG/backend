from datetime import datetime

from bson import ObjectId

from app.db import Database


class Model:

    def to_dict(self, exclude: list[str] = ()) -> dict:
        obj = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Database):
                continue
            if isinstance(value, ObjectId):
                obj[key] = str(value)
            elif isinstance(value, datetime):
                obj[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, Model):
                obj[key] = value.to_dict()
            elif isinstance(value, list) and all(isinstance(v, Model) for v in value):
                obj[key] = [v.to_dict() for v in value]
            else:
                obj[key] = value

        for key in exclude:
            obj.pop(key, None)
        return obj
