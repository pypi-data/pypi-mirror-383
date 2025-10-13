import logging
import statistics
import uuid
from pathlib import Path
from time import time

from backgroundlog.handlers.thread_handler import ThreadHandler

DIR_PATH = Path(__file__).parent
LOGGING_FILE_HANDLER_FILE_PATH = DIR_PATH / 'test_file_handler.log'
LOGGING_STREAM_HANDLER_FILE_PATH = DIR_PATH / 'test_stream_handler.log'


def main() -> None:
    stream_handler = logging.StreamHandler(
        LOGGING_STREAM_HANDLER_FILE_PATH.open('w'),
    )
    file_handler = logging.FileHandler(
        LOGGING_FILE_HANDLER_FILE_PATH,
        mode='a',
        encoding='utf-8',
    )
    thread_handler_stream_handler = ThreadHandler(stream_handler)
    thread_handler_file_handler = ThreadHandler(file_handler)

    log_handlers = (
        stream_handler,
        file_handler,
        thread_handler_stream_handler,
        thread_handler_file_handler,
    )

    results: list[tuple[str, float, float]] = []
    for handler in log_handlers:
        avg_spent_time, std_dev_spent_time = __run_performance_test(handler)
        results.append(
            (
                f"{handler.__class__.__name__} {
                    f'({handler.wrapped_handler.__class__.__name__})'
                    if isinstance(handler, ThreadHandler) else ''
                }",
                avg_spent_time,
                std_dev_spent_time,
            ),
        )

    baseline_mean = results[0][1]

    table_rows = ''
    for result in results:
        delta = 100.0 * (result[1] - baseline_mean) / baseline_mean
        if delta == 0.0:
            delta_str = 'baseline'
        else:
            sign = __sign(delta)
            delta_str = f'{sign}{abs(round(delta, 3))}%'

        table_rows += (
            f'|  {result[0]} | '
            f'{round(result[1], 3)} | '
            f'{round(result[2], 3)} | '
            f'{delta_str} |\n'
        )

    table = f"""
| Logging Handler  | Spent Time         |                  | vs. Baseline |
|------------------|--------------------|------------------|--------------|
|                  | Mean Time (ms)     | Std Dev (ms)     |              |
{table_rows}
    """

    print(table)

    __cleanup()


def __run_performance_test(
    handler: logging.Handler,
    iterations: int = 100_000,
    loops: int = 5,
) -> tuple[float, float]:
    logger = logging.getLogger(f'logger{uuid.uuid4()}')
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(handler)

    spent_times = []
    for _ in range(0, loops):
        start_time = time()
        for log_index in range(iterations):
            logger.info('Test message')
        spent_times.append(time() - start_time)

    avg_spent_times = statistics.mean(spent_times)
    std_dev_spent_times = statistics.stdev(spent_times)

    return avg_spent_times, std_dev_spent_times


def __sign(value: float) -> str:
    if value < 0:
        return '-'
    if value > 0:
        return '+'
    return ''


def __cleanup() -> None:
    LOGGING_FILE_HANDLER_FILE_PATH.unlink()
    LOGGING_STREAM_HANDLER_FILE_PATH.unlink()


if __name__ == '__main__':
    main()
