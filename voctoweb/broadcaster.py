from asyncio import create_task
from itertools import count
from json import dumps
from weakref import WeakValueDictionary


class WSBroadcaster:
    def __init__(self):
        self.wsid_iter = count()
        self.websockets = WeakValueDictionary()

    def add_ws(self, ws):
        """Add a websocket to the pool, return its id"""
        wsid = next(self.wsid_iter)
        self.websockets[wsid] = ws
        return wsid

    def broadcast(self, message):
        data = dumps(message)
        for ws in self.websockets.values():
            create_task(self.send(ws, data))

    async def send(self, ws, data):
        try:
            await ws.send_str(data)
        except Exception:
            raise
