"""Registry classes"""
from typing import Any, Callable, Optional
from abc import abstractmethod
import asyncio
import threading
import urllib.parse

from kazoo.client import KazooClient, KazooState, WatchedEvent

from dubbo.config import ApplicationConfig, CenterConfig

__all__ = ('Registry', 'RegistryFactory')


class Registry():

    __slots__ = ('_application', '_scheme', '_hosts')

    _application: str
    _scheme: str
    _hosts: str

    def __init__(self, application_config: ApplicationConfig, registry_config: CenterConfig) -> None:
        self._application = application_config.name
        self._scheme, self._hosts = registry_config.address.split('://')

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def hosts(self) -> str:
        return self._hosts

    @abstractmethod
    def ready(self) -> bool:
        pass

    @abstractmethod
    async def children(self, interface: str) -> list[str]:
        pass


class ZookeeperRegistry(Registry):

    __slots__ = ('_client', '_lock', '_loop', '_nodes')

    _client: KazooClient
    _lock: threading.Lock
    _loop: asyncio.AbstractEventLoop
    _nodes: dict[str, list[str]]

    PROVIDER_PATH: str = '/dubbo/{}/providers'

    def __init__(self, application_config: ApplicationConfig, registry_config: CenterConfig) -> None:
        super().__init__(application_config, registry_config)
        self._lock = threading.Lock()
        try:
            self._loop = asyncio.get_running_loop()
        except:
            self._loop = asyncio.new_event_loop()
        self._client = KazooClient(hosts=self.hosts)
        self._client.add_listener(self._state_listener)
        self._client.start()
        self._nodes = dict()

    @property
    def ready(self) -> bool:
        return self._client.connected

    async def children(self, interface: str) -> list[str]:
        if interface not in self._nodes:
            with self._lock:
                if interface not in self._nodes:
                    path = self.PROVIDER_PATH.format(interface)
                    children = await self._loop.run_in_executor(None, self._client.get_children, urllib.parse.quote(path), self._node_watcher)
                    self._nodes[interface] = children or []
        return self._nodes.get(interface, [])

    def _state_listener(self, state: KazooState) -> None:
        if state == KazooState.CONNECTED:
            threading.Thread(target=self._resubscribe).start()
        else:
            self._client.logger.debug('zookeeper connection state: %s', state)

    def _resubscribe(self) -> None:
        for interface in self._nodes.keys():
            path = self.PROVIDER_PATH.format(interface)
            children = self._client.get_children(urllib.parse.quote(path), watch=self._node_watcher)
            self._nodes[interface] = children or []

    async def _node_watcher(self, event: WatchedEvent) -> None:
        interface = event.path.split('/')[2]
        children = await self._loop.run_in_executor(None, lambda: self._client.get_children(urllib.parse.quote(event.path), watch=self._node_watcher))
        self._nodes[interface] = children or []


class NacosRegistry(Registry):

    __slots__ = ()

    def __init__(self, application_config: ApplicationConfig, registry_config: CenterConfig) -> None:
        super().__init__(application_config, registry_config)


class RegistryFactory():

    __slots__ = ()

    @staticmethod
    def get_registry(application_config: ApplicationConfig, registry_config: CenterConfig) -> Registry:
        assert registry_config.address is not None and ('zk://' in registry_config.address or 'nacos://' in registry_config.address)
        return ZookeeperRegistry(application_config, registry_config) if 'zk://' in registry_config.address else NacosRegistry(application_config, registry_config)
