"""Dubbo configuration classes."""
__all__ = ("ApplicationConfig", "ProtocolConfig", "CenterConfig", "ReferenceConfig")

from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BaseConfig(ABC):

    __slots__ = ()

    @abstractmethod
    def id(self) -> str:
        pass


class ApplicationConfig(BaseConfig):

    __slots__ = ("_name", "_environment")

    _name: str
    _environment: str

    def __init__(self, name: str, environment: str = "test") -> None:
        self._name = name
        self._environment = environment

    @property
    def id(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def environment(self) -> str:
        return self._environment


class ProtocolConfig(BaseConfig):

    __slots__ = ("_name", "_port")

    _name: str
    _port: int

    def __init__(self, name: str = "dubbo", port: int = 20880) -> None:
        self._name = name
        self._port = port

    @property
    def id(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def port(self) -> int:
        return self._port


class CenterConfig(BaseConfig):

    __slots__ = "_address"

    _address: str

    def __init__(self, address: str) -> None:
        self._address = address

    @property
    def id(self) -> str:
        return self._address

    @property
    def address(self) -> str:
        return self._address


class ReferenceConfig(BaseConfig):

    __slots__ = (
        "_interface",
        "_version",
        "_group",
        "_protocols",
        "_registries",
        "_metadata_report",
    )

    _interface: str
    _version: Optional[str]
    _group: Optional[str]
    _protocols: dict[str, ProtocolConfig]
    _registries: dict[str, CenterConfig]
    _metadata_report: Optional[CenterConfig]

    def __init__(
        self,
        interface: str,
        version: Optional[str] = None,
        group: Optional[str] = None,
        protocols: Optional[Tuple[ProtocolConfig]] = None,
        registries: Optional[Tuple[CenterConfig]] = None,
        metadata_report: Optional[CenterConfig] = None,
    ) -> None:
        self._interface = interface
        self._version = version
        self._group = group
        self.protocols = protocols
        self.registries = registries
        self._metadata_report = metadata_report

    @property
    def id(self) -> str:
        return f"{self._interface}:{self._version or ''}:{self._group or ''}"

    @property
    def interface(self) -> str:
        return self._interface

    @property
    def version(self) -> Optional[str]:
        return self._version

    @property
    def group(self) -> Optional[str]:
        return self._group

    @property
    def protocols(self) -> dict[str, ProtocolConfig]:
        return self._protocols

    @protocols.setter
    def protocols(self, values: Optional[Tuple[ProtocolConfig]]) -> None:
        self._protocols = {} if not values else {config.id: config for config in values}

    @property
    def registries(self) -> dict[str, CenterConfig]:
        return self._registries

    @registries.setter
    def registries(self, values: Optional[Tuple[CenterConfig]]) -> None:
        self._registries = (
            {} if not values else {config.id: config for config in values}
        )

    @property
    def metadata_report(self) -> Optional[CenterConfig]:
        return self._metadata_report

    @metadata_report.setter
    def metadata_report(self, value: Optional[CenterConfig]) -> None:
        self.metadata_report = value
