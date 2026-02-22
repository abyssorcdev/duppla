"""Tests for app.infrastructure.notifications.dispatcher."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from tests.common import BaseTestCase

from app.infrastructure.notifications.dispatcher import (
    DispatchResult,
    NotificationDispatcher,
)


class TestDispatchResult(BaseTestCase):
    """Tests for DispatchResult dataclass."""

    def test_dispatch_result_success_all_succeeded(self) -> None:
        r = DispatchResult(succeeded=["ch1", "ch2"], failed=[])
        self.assertTrue(r.all_succeeded)

    def test_dispatch_result_success_has_failures(self) -> None:
        r = DispatchResult(succeeded=["ch1"], failed=["ch2"])
        self.assertFalse(r.all_succeeded)

    def test_dispatch_result_success_str(self) -> None:
        r = DispatchResult(succeeded=["a"], failed=["b"])
        text = str(r)
        self.assertIn("succeeded", text)
        self.assertIn("failed", text)

    def test_dispatch_result_success_empty(self) -> None:
        r = DispatchResult()
        self.assertTrue(r.all_succeeded)
        self.assertEqual(r.succeeded, [])
        self.assertEqual(r.failed, [])


class TestNotificationDispatcherInit(BaseTestCase):
    """Tests for NotificationDispatcher.__init__."""

    def test_init_success_stores_channels(self) -> None:
        channels = [MagicMock(), MagicMock()]
        dispatcher = NotificationDispatcher(channels)
        self.assertEqual(len(dispatcher._channels), 2)


class TestNotificationDispatcherFromConfig(BaseTestCase):
    """Tests for NotificationDispatcher.from_config()."""

    def test_from_config_success_returns_dispatcher(self) -> None:
        with patch("app.infrastructure.notifications.channels.factory.build_channels", return_value=[]):
            dispatcher = NotificationDispatcher.from_config()
        self.assertIsInstance(dispatcher, NotificationDispatcher)


class TestNotificationDispatcherDispatch(BaseTestCase):
    """Tests for NotificationDispatcher.dispatch()."""

    def test_dispatch_success_all_channels(self) -> None:
        ch1 = MagicMock()
        ch1._name = "ch1"
        ch1.send = AsyncMock()
        ch2 = MagicMock()
        ch2._name = "ch2"
        ch2.send = AsyncMock()

        dispatcher = NotificationDispatcher([ch1, ch2])
        result = asyncio.run(dispatcher.dispatch({"event": "test"}))

        self.assertTrue(result.all_succeeded)
        self.assertEqual(len(result.succeeded), 2)

    def test_dispatch_success_with_failure(self) -> None:
        ch_ok = MagicMock()
        ch_ok._name = "ok"
        ch_ok.send = AsyncMock()

        ch_fail = MagicMock()
        ch_fail._name = "fail"
        ch_fail.send = AsyncMock(side_effect=Exception("boom"))

        dispatcher = NotificationDispatcher([ch_ok, ch_fail])
        result = asyncio.run(dispatcher.dispatch({"event": "test"}))

        self.assertFalse(result.all_succeeded)
        self.assertIn("ok", result.succeeded)
        self.assertIn("fail", result.failed)

    def test_dispatch_success_no_channels(self) -> None:
        dispatcher = NotificationDispatcher([])
        result = asyncio.run(dispatcher.dispatch({"event": "test"}))
        self.assertTrue(result.all_succeeded)

    def test_dispatch_success_channel_without_name(self) -> None:
        ch = MagicMock(spec=[])
        ch.send = AsyncMock()
        type(ch).__name__ = "CustomChannel"

        dispatcher = NotificationDispatcher([ch])
        result = asyncio.run(dispatcher.dispatch({"event": "test"}))
        self.assertTrue(result.all_succeeded)
