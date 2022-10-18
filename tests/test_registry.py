import os
from typing import Optional
from time import sleep
import urllib.parse
import unittest

from kazoo.client import KazooClient
from dubbo.config import CenterConfig

from dubbo.registry import RegistryFactory


def my_listener(state):
    print(state)


class TestRegistry(unittest.TestCase):

    def test_get_registry(self):
        zk_address: Optional[str] = os.getenv('ZK_ADDRESS')
        print(zk_address)
        if zk_address is not None:
            zk_registry = RegistryFactory.get_registry(CenterConfig(zk_address))
            self.assertIsNotNone(zk_registry)
            self.assertEqual('zk', zk_registry.scheme)
            print(zk_registry.hosts)

        nacos_address: Optional[str] = os.getenv('NACOS_ADDRESS')
        print(nacos_address)
        if nacos_address is not None:
            nacos_registry = RegistryFactory.get_registry(CenterConfig(nacos_address))
            self.assertIsNotNone(nacos_registry)
            self.assertEqual('nacos', nacos_registry.scheme)
            print(nacos_registry.hosts)


class TestZookeeper(unittest.TestCase):

    def test_client(self):
        hosts: Optional[str] = os.getenv('ZK_ADDRESS')
        if not hosts:
            return

        zk = KazooClient(hosts=hosts)
        zk.add_listener(my_listener)
        zk.start()

        providers = (zk.get_children(urllib.parse.quote('/dubbo/xxx/providers')) or []) + (zk.get_children(urllib.parse.quote('/dubbo/xxx/providers')) or [])
        provider = urllib.parse.unquote(providers[0])
        print(provider)
        result = urllib.parse.urlparse(provider)
        print(result)
        qs = dict(urllib.parse.parse_qsl(result.query))
        print(qs)
        instances = [item for item in map(lambda x: urllib.parse.unquote(x),  providers) if result.netloc in item]
        for instance in instances:
            print(urllib.parse.urlparse(instance))

        zk.stop()


if __name__ == '__main__':
    unittest.main()
