import logging
import unittest
from queue import Empty, Full
from time import sleep
from unittest.mock import MagicMock, patch

from backgroundlog.handlers.thread_handler import ThreadHandler


class TestThreadHandlerQueue(unittest.TestCase):
    def setUp(self) -> None:
        super()
        self.mock_handler = MagicMock(spec=logging.Handler)
        self.logger_name = 'bg'
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.INFO)

        queue_class_patcher = patch(
            'backgroundlog.handlers.thread_handler.Queue',
        )
        self.mock_queue_class = queue_class_patcher.start()
        self.addCleanup(queue_class_patcher.stop)

    def test_queue_put_nowait_full_error(self) -> None:
        mock_queue = MagicMock()
        mock_queue.get.side_effect = Empty
        mock_queue.put_nowait.side_effect = Full
        self.mock_queue_class.return_value = mock_queue

        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        self.logger.info('Test message')

        sleep(1)

        self.assertEqual(0, self.mock_handler.emit.call_count)
        self.assertEqual(1, thread_handler.dropped_log_record_count)

    def test_queue_put_error(self) -> None:
        exception_message = 'Something went wrong'

        mock_queue = MagicMock()
        mock_queue.get.side_effect = Empty
        mock_queue.put.side_effect = Exception(exception_message)
        self.mock_queue_class.return_value = mock_queue

        thread_handler = ThreadHandler(self.mock_handler)
        self.logger.addHandler(thread_handler)

        with self.assertRaises(Exception) as context:
            self.logger.error('Test message')

        self.assertEqual(exception_message, str(context.exception))
        self.assertEqual(0, self.mock_handler.emit.call_count)
        self.assertEqual(0, thread_handler.dropped_log_record_count)
