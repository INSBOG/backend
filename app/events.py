import json
from bson import ObjectId
from flask import request
from flask_socketio import SocketIO

from app.db import Database


socketio = SocketIO(cors_allowed_origins="*")

@socketio.event
def connect():
    id = request.sid
    print("Cliente conectado", id)

@socketio.event
def handle_file_processed(msg):
    socketio.emit("update_reports", msg)

@socketio.event
def progress(msg):
    data = json.loads(msg)
    db = Database()
    col = db.get_collection('reportes')
    report = col.find_one({"_id": ObjectId(data["report"])})
    print(report)
    if report:
        report["progress"] = data["progress"]
        col.update_one({"_id": ObjectId(data["report"])}, {"$set": report})

    socketio.emit("progress", msg)