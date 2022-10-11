import asyncio
import time
from typing import Any

class EchoClientProtocol(asyncio.Protocol):

    def __init__(self, on_con_lost: asyncio.Future[Any]) -> None:
        print('init')
        self.on_con_lost = on_con_lost

    async def _heartbeat(self):
        while True:
            await asyncio.sleep(60)
            self.transport.write(bytes(b % 256 for b in [-38, -69, -24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]))
            print('heartbeat')

    def connection_made(self, transport: asyncio.Transport) -> None:
        self._time = time.monotonic()
        print('connected')
        self.transport = transport
        self._heartbeat_task = asyncio.create_task(self._heartbeat())

    def data_received(self, data: bytes) -> None:
        print('received')
        print([x if x < 128 else x - 256 for x in data])

    def connection_lost(self, exc: Exception | None) -> None:
        print(time.monotonic() - self._time)
        print('disconnected')
        self._heartbeat_task.cancel()
        self.on_con_lost.set_result(True)

async def main():
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(lambda: EchoClientProtocol(on_con_lost), '10.5.138.251', 20880)

    try:
        await on_con_lost
    finally:
        transport.close()

if __name__ == '__main__':
    asyncio.run(main())
