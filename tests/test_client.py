import unittest
import asyncio

class DubboProtocol():

    async def __init__(self) -> None:
        self._listen()



    async def _listen(self):
        while True:
            yield 1

class DubboClient():

    def __init__(self, loop) -> None:
        self._loop = loop

    async def invoke(self, method, params, delay):
        current_time = self._loop.time()
        await asyncio.sleep(delay)
        return f'{method}:{params}@{current_time}'


async def main():
    client = DubboClient(asyncio.get_running_loop())
    task1 = asyncio.create_task(client.invoke('test1', 'test1', 1))
    task2 = asyncio.create_task(client.invoke('test2', 'test2', 2))
    res1 = await task1
    res2 = await task2
    print(res1)
    print(res2)


class TestClientMethods(unittest.TestCase):

    def test_client(self):
        asyncio.run(main())

if __name__ == '__main__':
    unittest.main()
