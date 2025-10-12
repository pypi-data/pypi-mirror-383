import asyncio
import websockets
import json


class KittyBot:
    def __init__(self, cookie, url):
        self.cookie = cookie
        self.url = url
        self.commands = {}

    def command(self, trigger):
        def decorator(func):
            self.commands[trigger] = func
            return func
        return decorator

    async def _connect(self):
        headers = {"Cookie": f"session={self.cookie}"}
        async with websockets.connect(self.url, extra_headers=headers) as ws:
            print(f"connected to {self.url}")
            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    text = data.get("text", "").strip()
                    username = data.get("username", "anon")

                    if text in self.commands:
                        await self.commands[text](ws, username)

                except websockets.ConnectionClosed:
                    print("connection closed, retrying in 3s")
                    await asyncio.sleep(3)
                    return await self._connect()
                except Exception as e:
                    print("err:", e)
                    await asyncio.sleep(1)

    def run(self):
        asyncio.run(self._connect())
