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
        zk_registry = RegistryFactory.get_registry(CenterConfig('zk://zk_hosts'))
        self.assertIsNotNone(zk_registry)
        self.assertEqual('zk', zk_registry.scheme)
        self.assertEqual('zk_hosts', zk_registry.hosts)
        nacos_registry = RegistryFactory.get_registry(CenterConfig('nacos://nacos_hosts'))
        self.assertIsNotNone(nacos_registry)
        self.assertEqual('nacos', nacos_registry.scheme)
        self.assertEqual('nacos_hosts', nacos_registry.hosts)


class TestZookeeper(unittest.TestCase):

    def test_client(self):
        zk = KazooClient(hosts='')
        zk.add_listener(my_listener)
        zk.start()

        providers = (zk.get_children(urllib.parse.quote('/dubbo/com.qiyi.qibo.common.PlaybackService/providers')) or []) + (zk.get_children(urllib.parse.quote('/dubbo/com.qiyi.azeroth.corpus.play.control.api.PlayControlService/providers')) or [])
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
