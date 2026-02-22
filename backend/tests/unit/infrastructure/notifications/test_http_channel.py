"""Tests for app.infrastructure.notifications.channels.http.HttpNotificationChannel."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from tests.common import BaseTestCase

from app.infrastructure.notifications.channels.http import HttpNotificationChannel


class TestHttpNotificationChannelInit(BaseTestCase):
    """Tests for HttpNotificationChannel.__init__."""

    def test_init_success_sets_attributes(self) -> None:
        name = self.fake.word()
        url = self.fake.url()
        headers = {"Authorization": self.fake.sha256()}
        channel = HttpNotificationChannel(name=name, url=url, headers=headers)
        self.assertEqual(channel._name, name)
        self.assertEqual(channel._url, url)
        self.assertEqual(channel._headers, headers)

    def test_init_success_default_headers(self) -> None:
        channel = HttpNotificationChannel(name="ch", url="http://example.com")
        self.assertEqual(channel._headers, {})


class TestHttpNotificationChannelSend(BaseTestCase):
    """Tests for HttpNotificationChannel.send()."""

    def test_send_success_calls_client(self) -> None:
        channel = HttpNotificationChannel(
            name=self.fake.word(),
            url=self.fake.url(),
        )
        channel._client = MagicMock()
        channel._client.post = AsyncMock(return_value=True)

        payload = {"event": self.fake.word()}
        asyncio.run(channel.send(payload))
        channel._client.post.assert_called_once()

    def test_send_error_logs_failure(self) -> None:
        channel = HttpNotificationChannel(
            name="test_channel",
            url="http://example.com/webhook",
        )
        channel._client = MagicMock()
        channel._client.post = AsyncMock(return_value=False)

        with patch("app.infrastructure.notifications.channels.http.logger") as mock_logger:
            asyncio.run(channel.send({"data": "test"}))
            mock_logger.error.assert_called_once()
