import atexit
from logging import CRITICAL, ERROR, Handler, LogRecord
from queue import Empty, Full, Queue
from socket import error as socket_error
from threading import Event, Thread
from typing import Final


class ThreadHandler(Handler):
    DEFAULT_QUEUE_SIZE: Final[int] = 1000
    DEFAULT_BLOCKING_LEVELS: Final[set[int]] = {CRITICAL, ERROR}
    DEFAULT_FLUSH_INTERVAL: Final[float] = 0.1
    DEFAULT_SHUTDOWN_TIMEOUT: Final[float] = 2.0
    EMIT_ERRORS = (
        OSError,
        ValueError,
        TypeError,
        UnicodeEncodeError,
        RuntimeError,
        socket_error,
    )

    def __init__(
        self,
        wrapped_handler: Handler,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        blocking_levels: set[int] | None = None,
        blocking_timeout: float | None = None,
        flush_interval: float = DEFAULT_FLUSH_INTERVAL,
        shutdown_timeout: float | None = DEFAULT_SHUTDOWN_TIMEOUT,
    ) -> None:
        super().__init__()
        self.__wrapped_handler = wrapped_handler
        self.__dropped_log_record_count = 0
        self.__queue: Queue[LogRecord] = Queue(maxsize=queue_size)
        if blocking_levels is None:
            blocking_levels = self.DEFAULT_BLOCKING_LEVELS
        self.__blocking_levels = blocking_levels
        self.__blocking_timeout = blocking_timeout
        self.__flush_interval = flush_interval
        self.__shutdown_timeout = shutdown_timeout
        self.__stop_event = Event()
        self.__feeder = Thread(
            target=self.__feeder_loop,
            daemon=True,
        )
        self.__feeder.start()
        atexit.register(self.__close)

    @property
    def wrapped_handler(self) -> Handler:
        return self.__wrapped_handler

    def emit(self, record: LogRecord) -> None:
        if record.levelno in self.__blocking_levels:
            self.__blocking_queue_put(record=record)
        else:
            self.__non_blocking_queue_put(record=record)

    @property
    def dropped_log_record_count(self) -> int:
        return self.__dropped_log_record_count

    def __non_blocking_queue_put(self, record: LogRecord) -> None:
        try:
            self.__queue.put_nowait(record)
        except Full:
            self.__dropped_log_record_count += 1

    def __blocking_queue_put(self, record: LogRecord) -> None:
        self.__queue.put(record, block=True, timeout=self.__blocking_timeout)

    def __feeder_loop(self) -> None:
        while not self.__stop_event.is_set() or not self.__queue.empty():
            try:
                record = self.__queue.get(
                    block=True,
                    timeout=self.__flush_interval,
                )
                self.__handle(record)
            except Empty:
                continue

    def __handle(self, record: LogRecord) -> None:
        try:
            self.__wrapped_handler.emit(record)
        except self.EMIT_ERRORS:
            self.__wrapped_handler.handleError(record)

    def __close(self) -> None:
        self.__stop_event.set()
        self.__feeder.join(timeout=self.__shutdown_timeout)
        self.__wrapped_handler.close()
        super().close()
