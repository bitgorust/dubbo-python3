"""Registry classes"""
from abc import abstractmethod
from typing import Optional

from dubbo.config import CenterConfig

__all__ = ('get_providers', 'Registry', 'RegistryFactory')


def get_providers(interface: str, version: Optional[str] = None, group: Optional[str] = None):
    pass


class Registry():

    __slots__ = ('_scheme', '_hosts')

    _scheme: str
    _hosts: str

    def __init__(self, config: CenterConfig) -> None:
        self._scheme, self._hosts = config.address.split('://')

    @property
    def scheme(self) -> str:
        return self._scheme

    @property
    def hosts(self) -> str:
        return self._hosts

    @abstractmethod
    def subscribe(self, node: str) -> None:
        pass

    @abstractmethod
    def children(self, node: str) -> None:
        pass


class ZookeeperRegistry(Registry):

    __slots__ = ()

    def __init__(self, config: CenterConfig) -> None:
        super().__init__(config)


class NacosRegistry(Registry):

    __slots__ = ()

    def __init__(self, config: CenterConfig) -> None:
        super().__init__(config)


class RegistryFactory():

    __slots__ = ()

    @staticmethod
    def get_registry(config: CenterConfig) -> Registry:
        assert config.address is not None and ('zk://' in config.address or 'nacos://' in config.address)
        return ZookeeperRegistry(config) if 'zk://' in config.address else NacosRegistry(config)
