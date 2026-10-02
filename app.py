from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
devices = client["ecse3038"]["devices"]
devices.create_index("name", unique=True)

app = FastAPI()


class Device(BaseModel):
    mac: str
    name: str | None = None
    room: str | None = None


@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))


@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device


@app.post("/devices", status_code=201)
def create_device(device: Device):
    try:
        devices.insert_one(device.model_dump())
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Device already exists")
    return device