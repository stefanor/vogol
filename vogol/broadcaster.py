from asyncio import create_task
from itertools import count
from weakref import WeakValueDictionary
import json

from bson import BSON


class WSBroadcaster:
    def __init__(self):
        self.wsid_iter = count()
        self.websockets = WeakValueDictionary()

    def add_ws(self, ws, username):
        """Add a websocket to the pool, return its id"""
        wsid = next(self.wsid_iter)
        self.websockets[(username, wsid)] = ws
        self.broadcast_connected_users()
        return wsid

    def remove_ws(self, username, wsid):
        self.websockets.pop((username, wsid))
        self.broadcast_connected_users()

    def list_connected_users(self):
        return sorted(set(username for username, wsid in self.websockets))

    def broadcast_connected_users(self):
        self.broadcast({
            'type': 'connected_users',
            'users': self.list_connected_users(),
        })

    def broadcast(self, message):
        if message['type'] == 'preview':
            fn = self.send_bytes
            data = BSON.encode(message)
        else:
            fn = self.send_str
            data = json.dumps(message)
        for ws in self.websockets.values():
            create_task(fn(ws, data))

    async def send_str(self, ws, data):
        await ws.send_str(data)

    async def send_bytes(self, ws, data):
        await ws.send_bytes(data)
