from datetime import datetime

from bson import ObjectId

from app.models.model import Model
import pandas as pd


class TestModel:

    @staticmethod
    def test_to_dict():
        model = Model()

        model.date = datetime.strptime("2024-01-01", "%Y-%m-%d")
        model._id = ObjectId("670aea38af650cd24b23b1ec")
        model.model = Model()
        model.models = [Model()]
        model.na = pd.NaT
        model.name = "Test"

        obj = model.to_dict(exclude=["model", "models", "_id", "date"])

        assert obj["name"] == "Test"
        assert obj["na"] is None
