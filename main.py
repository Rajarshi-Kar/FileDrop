from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from room_manager import RoomManager
import os, uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

rooms = RoomManager()
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    fid = str(uuid.uuid4())
    path = f"uploads/{fid}"
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"url": f"/download/{fid}"}

@app.get("/download/{fid}")
async def download(fid: str):
    return FileResponse(f"uploads/{fid}")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    await rooms.connect(room_id, websocket)

    await rooms.broadcast(room_id, {
        "type": "system",
        "text": "Someone joined the room"
    })

    await rooms.broadcast(room_id, {
        "type": "count",
        "value": rooms.count(room_id)
    })

    try:
        while True:
            data = await websocket.receive_json()
            await rooms.broadcast(room_id, data, sender=websocket)

    except WebSocketDisconnect:
        await rooms.disconnect(room_id, websocket)

        await rooms.broadcast(room_id, {
            "type": "count",
            "value": rooms.count(room_id)
        })

        await rooms.broadcast(room_id, {
            "type": "system",
            "text": "Someone left the room"
        })
