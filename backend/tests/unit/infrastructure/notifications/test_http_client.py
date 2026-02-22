"""Tests for app.infrastructure.notifications.clients.http_client.HttpClient."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from tests.common import BaseTestCase

from app.infrastructure.notifications.clients.http_client import HttpClient


class TestHttpClientInit(BaseTestCase):
    """Tests for HttpClient.__init__."""

    def test_init_success_default_timeout(self) -> None:
        client = HttpClient()
        self.assertEqual(client.timeout, 10)

    def test_init_success_custom_timeout(self) -> None:
        client = HttpClient(timeout=30)
        self.assertEqual(client.timeout, 30)


class TestHttpClientPost(BaseTestCase):
    """Tests for HttpClient.post()."""

    def test_post_success_first_attempt(self) -> None:
        client = HttpClient(timeout=5)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.infrastructure.notifications.clients.http_client.httpx.AsyncClient", return_value=mock_async_client):
            result = asyncio.run(client.post(self.fake.url(), {"key": "value"}))

        self.assertTrue(result)

    def test_post_success_with_headers(self) -> None:
        client = HttpClient(timeout=5)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)

        headers = {"X-Custom": self.fake.word()}
        with patch("app.infrastructure.notifications.clients.http_client.httpx.AsyncClient", return_value=mock_async_client):
            result = asyncio.run(client.post(self.fake.url(), {"key": "val"}, headers=headers))

        self.assertTrue(result)

    def test_post_error_all_retries_fail(self) -> None:
        client = HttpClient(timeout=5)

        mock_async_client = AsyncMock()
        mock_async_client.post.side_effect = httpx.HTTPError("connection error")
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.infrastructure.notifications.clients.http_client.httpx.AsyncClient", return_value=mock_async_client):
            with patch("app.infrastructure.notifications.clients.http_client.asyncio.sleep", new_callable=AsyncMock):
                result = asyncio.run(client.post(self.fake.url(), {"key": "val"}, max_retries=3))

        self.assertFalse(result)
        self.assertEqual(mock_async_client.post.call_count, 3)

    def test_post_success_after_retry(self) -> None:
        client = HttpClient(timeout=5)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_async_client = AsyncMock()
        mock_async_client.post.side_effect = [
            httpx.HTTPError("fail"),
            mock_response,
        ]
        mock_async_client.__aenter__ = AsyncMock(return_value=mock_async_client)
        mock_async_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.infrastructure.notifications.clients.http_client.httpx.AsyncClient", return_value=mock_async_client):
            with patch("app.infrastructure.notifications.clients.http_client.asyncio.sleep", new_callable=AsyncMock):
                result = asyncio.run(client.post(self.fake.url(), {"key": "val"}, max_retries=3))

        self.assertTrue(result)
        self.assertEqual(mock_async_client.post.call_count, 2)
