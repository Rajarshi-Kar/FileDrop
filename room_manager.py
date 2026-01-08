class RoomManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, room, ws):
        self.rooms.setdefault(room, set()).add(ws)

    async def disconnect(self, room, ws):
        if room in self.rooms:
            self.rooms[room].discard(ws)
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast(self, room, message, sender=None):
        for ws in list(self.rooms.get(room, [])):
            if ws != sender:
                await ws.send_json(message)

    def count(self, room):
        return len(self.rooms.get(room, []))
