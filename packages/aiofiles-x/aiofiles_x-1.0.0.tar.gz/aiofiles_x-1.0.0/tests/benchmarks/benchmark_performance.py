"""
Performance benchmarks for aiofiles-x.

Aiofiles-X
Copyright (C) 2025 ohmyarthur

This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
Please read the GNU Affero General Public License in
<https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.
"""

import asyncio
import os
import tempfile
import pytest

try:
    import aiofiles
except ImportError:
    pytest.skip("aiofiles not installed", allow_module_level=True)


def test_benchmark_read_small_file(benchmark):
    """Benchmark reading a small file (1KB)."""
    data = "x" * 1024  # 1KB

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write(data)

    try:

        async def read_file():
            async with aiofiles.open(temp_file, mode="r") as f:
                return await f.read()

        benchmark(lambda: asyncio.run(read_file()))
    finally:
        os.unlink(temp_file)


def test_benchmark_read_medium_file(benchmark):
    """Benchmark reading a medium file (1MB)."""
    data = "x" * (1024 * 1024)  # 1MB

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write(data)

    try:

        async def read_file():
            async with aiofiles.open(temp_file, mode="r") as f:
                return await f.read()

        benchmark(lambda: asyncio.run(read_file()))
    finally:
        os.unlink(temp_file)


def test_benchmark_write_small_file(benchmark):
    """Benchmark writing a small file (1KB)."""
    data = "x" * 1024  # 1KB

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:

        async def write_file():
            async with aiofiles.open(temp_file, mode="w") as f:
                await f.write(data)

        benchmark(lambda: asyncio.run(write_file()))
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_benchmark_write_medium_file(benchmark):
    """Benchmark writing a medium file (1MB)."""
    data = "x" * (1024 * 1024)  # 1MB

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:

        async def write_file():
            async with aiofiles.open(temp_file, mode="w") as f:
                await f.write(data)

        benchmark(lambda: asyncio.run(write_file()))
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_benchmark_concurrent_reads(benchmark):
    """Benchmark concurrent file reads."""
    num_files = 100
    temp_files = []

    try:
        # Create temp files
        for i in range(num_files):
            tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
            temp_files.append(tf.name)
            tf.write(f"Content {i}" * 100)
            tf.close()

        async def concurrent_reads():
            async def read_file(filename):
                async with aiofiles.open(filename, mode="r") as f:
                    return await f.read()

            tasks = [read_file(f) for f in temp_files]
            return await asyncio.gather(*tasks)

        benchmark(lambda: asyncio.run(concurrent_reads()))
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def test_benchmark_concurrent_writes(benchmark):
    """Benchmark concurrent file writes."""
    num_files = 100
    temp_files = []

    try:
        for i in range(num_files):
            temp_files.append(tempfile.mktemp())

        async def concurrent_writes():
            async def write_file(filename, content):
                async with aiofiles.open(filename, mode="w") as f:
                    await f.write(content)

            tasks = [write_file(temp_files[i], f"Content {i}" * 100) for i in range(num_files)]
            return await asyncio.gather(*tasks)

        benchmark(lambda: asyncio.run(concurrent_writes()))
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


def test_benchmark_line_iteration(benchmark):
    """Benchmark line-by-line iteration."""
    num_lines = 10000

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        for i in range(num_lines):
            tf.write(f"Line {i}\n")

    try:

        async def iterate_lines():
            lines = []
            async with aiofiles.open(temp_file, mode="r") as f:
                async for line in f:
                    lines.append(line)
            return lines

        benchmark(lambda: asyncio.run(iterate_lines()))
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "--benchmark-only", "-v"])
