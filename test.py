import pandas as pd

from app.db import Database

df = pd.read_excel("../resources/servicios.xlsx")

grouped = df.groupby("PAT_TYPE").apply(lambda x: x["WARD"].str.lower().str.strip().dropna().to_list())

grouped.to_json("services.json")


db = Database()
col = db.get_collection("services")

col.insert_many([{"PAT_TYPE": key, "WARDS": value} for key, value in grouped.items()])