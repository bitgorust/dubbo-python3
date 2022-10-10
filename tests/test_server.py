import time

import uvicorn

class Client():

    def __init__(self) -> None:
        print(time.monotonic_ns())

    def hello(self) -> None:
        print("hello")


class App:

    def __init__(self, client) -> None:
        self._client = client

    async def __call__(self, scope, receive, send):
        self._client.hello()
        assert scope['type'] == 'http'
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, world!',
        })


client = Client()

def create_app():
    return App(client)


if __name__ == "__main__":
    uvicorn.run("test_server:create_app", port=5000, log_level="info", workers=4, factory=True)
