from asyncio import create_task
from itertools import count
from weakref import WeakValueDictionary
import json

import bson


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
        if message['type'] == 'preview':
            fn = self.send_bytes
            data = bson.dumps(message)
        else:
            fn = self.send_str
            data = json.dumps(message)
        for ws in self.websockets.values():
            create_task(fn(ws, data))

    async def send_str(self, ws, data):
        await ws.send_str(data)

    async def send_bytes(self, ws, data):
        await ws.send_bytes(data)
