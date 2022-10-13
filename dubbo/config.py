"""Dubbo configuration classes."""

__all__ = ()


from typing import Optional


class ApplicationConfig:

    __slots__ = ()

    def __init__(self, name: str, environment: str = 'test') -> None:
        self._name = name
        self._environment = environment

    @property
    def name(self) -> str:
        return self._name

    @property
    def environment(self) -> str:
        return self._environment


class RegistryConfig:

    __slots__ = ()

    def __init__(self, address: str) -> None:
        self._address = address

    @property
    def address(self) -> str:
        return self._address


class MetadataReportConfig:

    __slots__ = ()

    def __init__(self, address: str) -> None:
        self._address = address

    @property
    def address(self) -> str:
        return self._address


class ProtocolConfig:

    __slots__ = ()

    def __init__(self, name: str, port: int) -> None:
        self._name = name
        self._port = port

    @property
    def name(self) -> str:
        return self._name

    @property
    def port(self) -> int:
        return self._port


class ReferenceConfig:

    __slots__ = ()

    def __init__(self, name: str, interface: str,
                 version: Optional[str] = None, group: Optional[str] = "",
                 application: Optional[ApplicationConfig] = None,
                 protocol: Optional[ProtocolConfig] = None,
                 registry: Optional[RegistryConfig] = None,
                 metadata_report: Optional[MetadataReportConfig] = None) -> None:
        self._name = name
        self._interface = interface
        self._version = version
        self._group = group
        self._application = application
        self._protocol = protocol
        self._registry = registry
        self._metadata_report = metadata_report

    @property
    def name(self) -> str:
        return self._name

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
    def application(self) -> Optional[ApplicationConfig]:
        return self._application

    @property
    def protocol(self) -> Optional[ProtocolConfig]:
        return self._protocol

    @property
    def registry(self) -> Optional[RegistryConfig]:
        return self.registry

    @property
    def metadata_report(self) -> Optional[MetadataReportConfig]:
        return self._metadata_report
