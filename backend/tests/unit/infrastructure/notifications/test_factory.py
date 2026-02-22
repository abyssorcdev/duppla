"""Tests for app.infrastructure.notifications.channels.factory.build_channels."""

from tests.common import BaseTestCase

from app.infrastructure.notifications.channels.factory import build_channels


class TestBuildChannels(BaseTestCase):
    """Tests for build_channels()."""

    def test_build_channels_success_http_type(self) -> None:
        config = [
            {
                "type": "http",
                "name": self.fake.word(),
                "url": self.fake.url(),
                "headers": {"Content-Type": "application/json"},
            }
        ]
        channels = build_channels(config)
        self.assertEqual(len(channels), 1)

    def test_build_channels_success_multiple(self) -> None:
        config = [
            {"type": "http", "name": "ch1", "url": self.fake.url()},
            {"type": "http", "name": "ch2", "url": self.fake.url()},
        ]
        channels = build_channels(config)
        self.assertEqual(len(channels), 2)

    def test_build_channels_success_skips_unknown(self) -> None:
        config = [{"type": "slack", "name": "unknown"}]
        channels = build_channels(config)
        self.assertEqual(len(channels), 0)

    def test_build_channels_success_skips_none_type(self) -> None:
        config = [{"name": "no-type"}]
        channels = build_channels(config)
        self.assertEqual(len(channels), 0)

    def test_build_channels_success_empty_config(self) -> None:
        channels = build_channels([])
        self.assertEqual(len(channels), 0)

    def test_build_channels_success_mixed(self) -> None:
        config = [
            {"type": "http", "name": "valid", "url": self.fake.url()},
            {"type": "unknown", "name": "invalid"},
        ]
        channels = build_channels(config)
        self.assertEqual(len(channels), 1)
