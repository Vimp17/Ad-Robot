#!/usr/bin/env python3
"""Measure download speed by fetching one URL several times in sequence."""

from __future__ import annotations

import argparse
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def download_once(url: str, timeout: float, chunk_size: int) -> tuple[float, int]:
    """Return elapsed seconds and bytes actually read for one successful GET."""
    request = Request(url, headers={"User-Agent": "net-speed-measurer/1.0"})
    started = time.perf_counter()
    size = 0
    with urlopen(request, timeout=timeout) as response:
        while chunk := response.read(chunk_size):
            size += len(chunk)
    return time.perf_counter() - started, size


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("число должно быть больше нуля")
    return number


def positive_float(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("число должно быть больше нуля")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Последовательно скачивает файл по URL и измеряет скорость."
    )
    parser.add_argument("url", help="адрес файла, например URL большой картинки")
    parser.add_argument("-n", "--requests", type=positive_int, default=10,
                        help="число запросов (по умолчанию: 10)")
    parser.add_argument("--timeout", type=positive_float, default=60,
                        help="таймаут одного запроса в секундах (по умолчанию: 60)")
    parser.add_argument("--chunk-size", type=positive_int, default=64 * 1024,
                        help="размер блока чтения в байтах (по умолчанию: 65536)")
    args = parser.parse_args()

    durations: list[float] = []
    total_bytes = 0
    print(f"Измерение: {args.url}\nЗапросов: {args.requests}\n")
    try:
        for index in range(1, args.requests + 1):
            elapsed, size = download_once(args.url, args.timeout, args.chunk_size)
            durations.append(elapsed)
            total_bytes += size
            print(f"Запрос {index}/{args.requests}: {size:,} байт за {elapsed:.3f} с")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        print(f"Ошибка запроса: {error}", file=sys.stderr)
        return 1

    total_time = sum(durations)
    average_time = total_time / len(durations)
    # Decimal MB/s, matching the common networking convention: 1 MB = 1,000,000 B.
    speed_mb_s = total_bytes / total_time / 1_000_000 if total_time else 0.0
    print("\nИтог:")
    print(f"  Среднее время запроса: {average_time:.3f} с")
    print(f"  Скачано всего:         {total_bytes:,} байт ({total_bytes / 1_000_000:.3f} МБ)")
    print(f"  Средняя скорость:      {speed_mb_s:.3f} МБ/с ({speed_mb_s * 8:.3f} Мбит/с)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
