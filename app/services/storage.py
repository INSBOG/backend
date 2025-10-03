import json
import zipfile
from base64 import b64encode
from datetime import datetime
from io import BytesIO
from uuid import uuid4

from bson import ObjectId
from flask import jsonify, request

from app.adapters.minio import MinioAdapter
from app.controllers.rabbitmq import RabbitMQ
from app.db import Database

from app.services.file_converter import FileConverter


class StorageService:

    def __init__(self) -> None:
        self.adapter = MinioAdapter()
        self.db = Database()
        self.queue_controller = RabbitMQ()

    def upload_file(self):
        try:
            file = request.files['file']
            data = json.loads(request.form["data"])

            filename = f"{uuid4()}.xlsx"
            ext = file.filename.split(".")[1]

            if ext.lower() == "dbf":
                file_stream = FileConverter.dbf_to_xlsx(file)
            else:
                file_stream = BytesIO(file.read())
                file_stream.seek(0)

            col = self.db.get_collection("reportes")
            report_data = {
                "date": datetime.now(),
                "filename": filename,
                "department": ObjectId(data["department"]),
                "month": data["month"],
                "user": ObjectId(data["user"]),
                "original_filename": file.filename,
                "status": 1,
                "progress": 0
            }

            col.insert_one(report_data)

            self.adapter.upload_file(filename, file_stream, "files")

            self.queue_controller.public_message(
                "reports", json.dumps(report_data, default=str))

            return {
                "status_code": 200,
                "message": "File uploaded"
            }
        except Exception as e:
            return {
                "status_code": 500,
                "message": str(e)
            }, 500

    def download_files(self):
        data = json.loads(request.data)
        col = self.db.get_collection("reportes")
        
        # If there's only one file, return it directly
        if len(data) == 1:
            report = col.find_one({"_id": ObjectId(data[0])})
            response = self.adapter.get_file(
                report["processed_file"], "processed")
            file_data = response.read()
            response.close()
            file_b64 = b64encode(file_data).decode("utf-8")
            return {
                "status_code": 200,
                "message": "Archivo descargado",
                "data": {
                    "filename": f"Errores_{report['original_filename']}",
                    "content": file_b64
                },
                "single_file": True
            }
        
        # For multiple files, create a zip
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for id in data:
                report = col.find_one({"_id": ObjectId(id)})
                response = self.adapter.get_file(
                    report["processed_file"], "processed")
                file_data = response.read()
                filename = f"{uuid4()}-{report['original_filename']}"
                zip_file.writestr(filename, file_data)
                response.close()
        zip_buffer.seek(0)
        zip_b64 = b64encode(zip_buffer.getvalue()).decode("utf-8")
        return {
            "status_code": 200,
            "message": "Archivos descargados",
            "data": zip_b64,
            "single_file": False
        }

    def get_reports(self):
        col = self.db.get_collection("reportes")
        data = list(col.aggregate([
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user",
                    "foreignField": "_id",
                    "as": "usr"
                }
            },
            {
                "$unwind": {
                    "path": "$usr",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "locations",
                    "localField": "department",
                    "foreignField": "_id",
                    "as": "dpto"
                }
            },
            {
                "$unwind": {
                    "path": "$dpto",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "data": 0,
                    "usr.password": 0,
                    "dpto.ward": 0,
                    "dpto.ward_type": 0,
                    "dpto._id": 0
                }
            }
        ]))

        return json.dumps(data, default=str)

    def delete_data(self):
        data = json.loads(request.data)
        col = self.db.get_collection("reportes")

        for item in data["selected"]:
            report = col.find_one({"_id": ObjectId(item)})
            self.adapter.delete_file(report["filename"], "files")
            if "processed_file" in report:
                self.adapter.delete_file(report["processed_file"], "processed")

        for_del = [ObjectId(item) for item in data["selected"]]

        col.delete_many({
            "_id": {
                "$in": for_del
            }
        })

        return {
            "status_code": 200,
            "message": "Data deleted"
        }

    def get_dptos(self):
        col = self.db.get_collection("locations")
        locations = list(col.find({}, {
            "_id": 1,
            "dpto": 1
        })
            .sort("dpto", 1))
        return jsonify({
            "data": json.loads(json.dumps(locations, default=str))
        })
