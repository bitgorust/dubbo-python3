"""Bootstrap class"""
from __future__ import annotations
from typing import Optional, Tuple, Union
from dubbo.config import ApplicationConfig, CenterConfig, ProtocolConfig, ReferenceConfig
from dubbo.proxy import Proxy
from dubbo.registry import Registry

__all__ = ('instance',)


class Bootstrap():

    __slots__ = ('_application_config', '_protocol_config', '_registry_config', '_metadata_report_config', '_reference_config', '_registry_center', '_reference_proxy')

    _application_config: Optional[ApplicationConfig]
    _protocol_config: dict[str, ProtocolConfig]
    _registry_config: dict[str, CenterConfig]
    _metadata_report_config: dict[str, CenterConfig]
    _reference_config: dict[str, ReferenceConfig]

    _registry_center: dict[str, Registry]
    _reference_proxy: dict[str, Proxy]

    def __init__(self) -> None:
        self._protocol_config = dict()
        self._registry_config = dict()
        self._metadata_report_config = dict()
        self._reference_config = dict()

    def application(self, config: Union[str, ApplicationConfig]) -> Bootstrap:
        if isinstance(config, str):
            self._application_config = ApplicationConfig(config)
        else:
            self._application_config = config
        return self

    def protocol(self, config: ProtocolConfig) -> Bootstrap:
        self._protocol_config[config.id] = config
        return self

    def registry(self, config: Union[str, CenterConfig]) -> Bootstrap:
        registry_config = CenterConfig(config) if isinstance(config, str) else config
        self._registry_config[registry_config.id] = registry_config
        return self

    def metadata_report(self, config: Union[str, CenterConfig]) -> Bootstrap:
        metadata_report_config = CenterConfig(config) if isinstance(config, str) else config
        self._metadata_report_config[metadata_report_config.id] = metadata_report_config
        return self

    def reference(self, config: ReferenceConfig,
                  name: Optional[str] = None,
                  protocols: Optional[Tuple[str]] = None,
                  registries: Optional[Tuple[str]] = None,
                  metadata_report: Optional[str] = None) -> Bootstrap:
        key = config.id if not name else name
        assert key not in self._reference_config

        if not config.protocols:
            if protocols is None:
                config.protocols = tuple(self._protocol_config.values())
            else:
                config.protocols = tuple([self._protocol_config[key] for key in protocols if key in self._protocol_config])
        else:
            self._protocol_config.update(config.protocols)
        assert len(config.protocols) > 0

        if not config.registries:
            if (registries is None):
                config.registries = tuple(self._registry_config.values())
            else:
                config.registries = tuple([self._registry_config[key] for key in registries if key in self._registry_config])
        else:
            self._registry_config.update(config.registries)
        assert len(config.registries) > 0

        if not config.metadata_report:
            if metadata_report is not None:
                config.metadata_report = self._metadata_report_config[metadata_report]
        else:
            self._metadata_report_config.setdefault(config.metadata_report.id, config.metadata_report)

        self._reference_config[key] = config
        return self

    def start(self) -> None:
        self._registry_center = {}
        pass


instance = Bootstrap()
