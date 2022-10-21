"""Registry classes"""
from collections import namedtuple
from typing import Any, Callable, NamedTuple, Optional
from abc import abstractmethod
import asyncio
import threading
import urllib.parse

from kazoo.client import KazooClient, KazooState, WatchedEvent

from common.config import ApplicationConfig, CenterConfig, ReferenceConfig

__all__ = ("Registry", "RegistryFactory")


class Node(NamedTuple):
    scheme: str
    netloc: str
    query: dict[str, str]


class Registry:

    __slots__ = ("_application", "_scheme", "_hosts")

    _application: str
    _scheme: str
    _hosts: str

    def __init__(
        self, application_config: ApplicationConfig, registry_config: CenterConfig
    ) -> None:
        self._application = application_config.name
        self._scheme, self._hosts = registry_config.address.split("://")

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
    async def children(self, reference: ReferenceConfig) -> list[str]:
        pass


class ZookeeperRegistry(Registry):

    __slots__ = ("_client", "_lock", "_loop", "_nodes", "_instances")

    _client: KazooClient
    _lock: threading.Lock
    _loop: asyncio.AbstractEventLoop
    _nodes: dict[str, list[Node]]
    _instances: dict[str, list[str]]

    PROVIDER_PATH: str = "/dubbo/{}/providers"

    def __init__(
        self, application_config: ApplicationConfig, registry_config: CenterConfig
    ) -> None:
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
        self._instances = dict()

    @property
    def ready(self) -> bool:
        return self._client.connected

    async def children(self, reference_config: ReferenceConfig) -> list[str]:
        interface = reference_config.interface
        if interface not in self._nodes:
            with self._lock:
                if interface not in self._nodes:
                    self._nodes[interface] = await self._loop.run_in_executor(
                        None, self._get_nodes, self.PROVIDER_PATH.format(interface)
                    )
                    print(f"{interface} has {len(self._nodes[interface])} nodes")
        if reference_config.id not in self._instances:
            with self._lock:
                if reference_config.id not in self._instances:
                    self._instances[reference_config.id] = self._get_instances(
                        self._nodes[interface],
                        reference_config.version,
                        reference_config.group,
                    )
                    print(
                        f"{reference_config.id} has {len(self._instances[reference_config.id])} instances"
                    )
        return self._instances.get(reference_config.id, [])

    def _state_listener(self, state: KazooState) -> None:
        if state == KazooState.CONNECTED:
            threading.Thread(target=self._resubscribe).start()
        else:
            self._client.logger.debug("zookeeper connection state: %s", state)

    def _resubscribe(self) -> None:
        for interface in self._nodes.keys():
            self._nodes[interface] = self._get_nodes(
                self.PROVIDER_PATH.format(interface)
            )
        for reference in self._instances.keys():
            interface, version, group = reference.split(":")
            self._instances[reference] = self._get_instances(
                self._nodes[interface], version, group
            )

    async def _node_watcher(self, event: WatchedEvent) -> None:
        interface = event.path.split("/")[2]
        self._nodes[interface] = await self._loop.run_in_executor(
            None, self._get_nodes, event.path
        )
        for reference in self._instances.keys():
            if reference.startswith(interface):
                interface, version, group = reference.split(":")
                self._instances[reference] = self._get_instances(
                    self._nodes[interface], version, group
                )

    def _get_nodes(self, path: str) -> list[Node]:
        children = (
            self._client.get_children(
                urllib.parse.quote(path), watch=self._node_watcher
            )
            or []
        )
        return [self._parse_node(child) for child in children]

    def _get_instances(
        self, nodes: list[Node], version: Optional[str], group: Optional[str]
    ) -> list[str]:
        matched = filter(
            lambda node: self._filter_by_version_group(
                node, version or "", group or ""
            ),
            nodes,
        )
        return list(set([node.netloc for node in matched]))

    def _parse_node(self, path: str) -> Node:
        url = urllib.parse.unquote(path)
        parse_result = urllib.parse.urlparse(url)
        query = dict(urllib.parse.parse_qsl(parse_result.query))
        return Node(parse_result.scheme, parse_result.netloc, query)

    def _filter_by_version_group(self, node: Node, version: str, group: str) -> bool:
        if version != "*" and version != node.query.get("version", ""):
            return False
        if group != "*":
            node_group = node.query.get("group", "")
            if not group:
                return not node_group
            else:
                groups = group.split(",")
                return node_group in groups
        return True


class NacosRegistry(Registry):

    __slots__ = ()

    def __init__(
        self, application_config: ApplicationConfig, registry_config: CenterConfig
    ) -> None:
        super().__init__(application_config, registry_config)


class RegistryFactory:

    __slots__ = ()

    @staticmethod
    def get_registry(
        application_config: ApplicationConfig, registry_config: CenterConfig
    ) -> Registry:
        assert registry_config.address is not None and (
            "zk://" in registry_config.address or "nacos://" in registry_config.address
        )
        return (
            ZookeeperRegistry(application_config, registry_config)
            if "zk://" in registry_config.address
            else NacosRegistry(application_config, registry_config)
        )
