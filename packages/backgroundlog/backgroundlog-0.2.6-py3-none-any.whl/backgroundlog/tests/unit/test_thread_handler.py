import logging
import unittest
from time import sleep
from unittest.mock import MagicMock

from backgroundlog.handlers.thread_handler import ThreadHandler


class TestThreadHandler(unittest.TestCase):
    def setUp(self) -> None:
        super()
        self.mock_handler = MagicMock(spec=logging.Handler)
        self.logger_name = 'bg'
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.INFO)

    def test_wrapped_handler(self) -> None:
        thread_handler = ThreadHandler(self.mock_handler)

        self.assertEqual(self.mock_handler, thread_handler.wrapped_handler)

    def test_an_info_message_success(self) -> None:
        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        self.logger.info('Test message')

        sleep(1)

        self.assertEqual(1, self.mock_handler.emit.call_count)
        record_arg: logging.LogRecord = self.mock_handler.emit.call_args[0][0]
        self.assertEqual('Test message', record_arg.getMessage())

    def test_an_error_message_success(self) -> None:
        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        self.logger.error('Test error message')

        sleep(1)

        self.assertEqual(1, self.mock_handler.emit.call_count)
        record_arg: logging.LogRecord = self.mock_handler.emit.call_args[0][0]
        self.assertEqual('Test error message', record_arg.getMessage())

    def test_one_thousand_messages_success(self) -> None:
        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        for log_index in range(1000):
            self.logger.info(f'Test message {log_index}')

        sleep(1)

        self.assertEqual(1000, self.mock_handler.emit.call_count)
        record_arg: logging.LogRecord = self.mock_handler.emit.call_args[0][0]
        self.assertEqual('Test message 999', record_arg.getMessage())

    def test_an_info_message_dropped_message_error(self) -> None:
        thread_handler = ThreadHandler(self.mock_handler, queue_size=1)
        self.logger.addHandler(thread_handler)

        self.logger.info('Test message 1')
        self.logger.info('Test message 3')
        self.logger.info('Test message 3')
        self.logger.info('Test message 4')

        self.assertEqual(3, thread_handler.dropped_log_record_count)

    def test_emit_error(self) -> None:
        self.mock_handler.emit.side_effect = RuntimeError
        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        self.logger.info('Test message')

        sleep(1)

        self.assertEqual(1, self.mock_handler.emit.call_count)
        self.assertEqual(1, self.mock_handler.handleError.call_count)
