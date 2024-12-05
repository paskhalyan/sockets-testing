from contextlib import asynccontextmanager
from fastapi import FastAPI
import socketio
import asyncio
import random

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def random_number_generator():
        while True:
            await asyncio.sleep(random.randint(3, 6))
            number = random.randint(1, 100)
            print(f"Generated number: {number}")
            await sio.emit("random_number", {"number": number})

    print("Starting random number generator...")
    task = asyncio.create_task(random_number_generator())
    state["task"] = task

    yield

    print("Shutting down random number generator...")
    task.cancel()
    await task


fastapi_app = FastAPI(lifespan=lifespan)


@fastapi_app.get("/")
async def root():
    return {"message": "FastAPI with Socket.IO"}

@fastapi_app.post("/print-name/{name}")
async def print_name(name: str):
    print(f"Printing name: {name}")
    await sio.emit("print_name", {"name": name})
    return {"message": f"Name {name} has been sent to the frontend"}


app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)


@sio.on("connect")
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
