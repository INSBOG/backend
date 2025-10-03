import time
from datetime import datetime, timedelta

import schedule

from app.adapters.minio import MinioAdapter
from app.db import Database

from app.db import Database


def remove_expired_files():
    db = Database()
    col = db.get_collection("reportes")
    data = list(col.find())
    minio_adapter = MinioAdapter()

    for item in data:
        date = item["date"]
        if date + timedelta(days=1) <= datetime.now():
            col.delete_one({"_id": item["_id"]})
            minio_adapter.delete_file(item["file"])


def run_jobs():
    schedule.every(1).minutes.do(remove_expired_files)
    while True:
        schedule.run_pending()
        time.sleep(1)
