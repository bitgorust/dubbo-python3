import unittest

from dubbo.config import ApplicationConfig, CenterConfig, ProtocolConfig, ReferenceConfig


class TestConfig(unittest.TestCase):

    def test_application_config(self):
        application_config = ApplicationConfig('test_application_config')
        self.assertIsNotNone(application_config)
        print(application_config.id)
        self.assertEqual('test_application_config', application_config.id)
        print(application_config.name)
        self.assertEqual('test_application_config', application_config.name)
        print(application_config.environment)
        self.assertEqual('test', application_config.environment)

    def test_reference_config(self):
        reference_config = ReferenceConfig('com.qiyi.azeroth.corpus.play.control.api.PlayControlService', '1.0')
        self.assertIsNotNone(reference_config)
        self.assertEqual('com.qiyi.azeroth.corpus.play.control.api.PlayControlService:1.0:', reference_config.id)
        print(reference_config)
        reference_config.protocols = (ProtocolConfig('dubbo', 20880),)
        reference_config.registries = (CenterConfig('test'),)
        self.assertEqual(1, len(reference_config.protocols or {}))
        self.assertEqual(1, len(reference_config.registries or {}))
        print(reference_config)


if __name__ == '__main__':
    unittest.main()
