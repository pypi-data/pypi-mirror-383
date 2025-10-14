"""
Unit tests for basic aiofiles-x functionality.

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


@pytest.mark.asyncio
async def test_open_write_read():
    """Test basic open, write, and read operations."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:
        async with aiofiles.open(temp_file, mode="w") as f:
            await f.write("Hello, aiofiles-x!")

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()

        assert content == "Hello, aiofiles-x!"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_readline():
    """Test readline operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("Line 1\nLine 2\nLine 3\n")

    try:
        async with aiofiles.open(temp_file, mode="r") as f:
            line1 = await f.readline()
            line2 = await f.readline()
            line3 = await f.readline()

        assert line1 == "Line 1\n"
        assert line2 == "Line 2\n"
        assert line3 == "Line 3\n"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_readlines():
    """Test readlines operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("Line 1\nLine 2\nLine 3\n")

    try:
        async with aiofiles.open(temp_file, mode="r") as f:
            lines = await f.readlines()

        assert len(lines) == 3
        assert lines[0] == "Line 1\n"
        assert lines[1] == "Line 2\n"
        assert lines[2] == "Line 3\n"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_writelines():
    """Test writelines operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:
        lines = ["Line 1\n", "Line 2\n", "Line 3\n"]

        async with aiofiles.open(temp_file, mode="w") as f:
            await f.writelines(lines)

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()

        assert content == "Line 1\nLine 2\nLine 3\n"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_seek_tell():
    """Test seek and tell operations."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("0123456789")

    try:
        async with aiofiles.open(temp_file, mode="r") as f:
            pos = await f.tell()
            assert pos == 0

            data = await f.read(5)
            assert data == "01234"

            pos = await f.tell()
            assert pos == 5

            await f.seek(0)
            pos = await f.tell()
            assert pos == 0

            data = await f.read(5)
            assert data == "01234"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_async_iteration():
    """Test async iteration over file lines."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("Line 1\nLine 2\nLine 3\n")

    try:
        lines = []
        async with aiofiles.open(temp_file, mode="r") as f:
            async for line in f:
                lines.append(line)

        assert len(lines) == 3
        assert lines[0] == "Line 1\n"
        assert lines[1] == "Line 2\n"
        assert lines[2] == "Line 3\n"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_binary_mode():
    """Test binary mode operations."""
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tf:
        temp_file = tf.name

    try:
        data = b"Binary data \x00\x01\x02"

        async with aiofiles.open(temp_file, mode="wb") as f:
            await f.write(data)

        async with aiofiles.open(temp_file, mode="rb") as f:
            read_data = await f.read()

        assert read_data == data
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_append_mode():
    """Test append mode."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("Initial data\n")

    try:
        async with aiofiles.open(temp_file, mode="a") as f:
            await f.write("Appended data\n")

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()

        assert content == "Initial data\nAppended data\n"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_flush():
    """Test flush operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:
        async with aiofiles.open(temp_file, mode="w") as f:
            await f.write("Data to flush")
            await f.flush()

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()

        assert content == "Data to flush"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_context_manager_closes_file():
    """Test that context manager properly closes files."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name

    try:
        async with aiofiles.open(temp_file, mode="w") as f:
            await f.write("Test data")

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()
            assert content == "Test data"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test concurrent file operations."""
    num_files = 10
    temp_files = []

    try:
        for i in range(num_files):
            tf = tempfile.NamedTemporaryFile(mode="w", delete=False)
            temp_files.append(tf.name)
            tf.close()

        async def write_file(filename, content):
            async with aiofiles.open(filename, mode="w") as f:
                await f.write(content)

        tasks = [write_file(temp_files[i], f"Content {i}") for i in range(num_files)]
        await asyncio.gather(*tasks)

        async def read_file(filename):
            async with aiofiles.open(filename, mode="r") as f:
                return await f.read()

        tasks = [read_file(temp_files[i]) for i in range(num_files)]
        results = await asyncio.gather(*tasks)

        for i in range(num_files):
            assert results[i] == f"Content {i}"

    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


@pytest.mark.asyncio
async def test_readall():
    """Test readall operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("Test content for readall")

    try:
        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.readall()
        assert content == "Test content for readall"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_read1():
    """Test read1 operation."""
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tf:
        temp_file = tf.name
        tf.write(b"x" * 1000)

    try:
        async with aiofiles.open(temp_file, mode="rb") as f:
            chunk = await f.read1(100)
            assert len(chunk) <= 100
            assert isinstance(chunk, bytes)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_readinto():
    """Test readinto operation."""
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tf:
        temp_file = tf.name
        tf.write(b"Test data for readinto")

    try:
        async with aiofiles.open(temp_file, mode="rb") as f:
            buffer = bytearray(10)
            bytes_read = await f.readinto(buffer)
            assert bytes_read == 10
            assert buffer == b"Test data "
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_truncate():
    """Test truncate operation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
        temp_file = tf.name
        tf.write("0123456789")

    try:
        async with aiofiles.open(temp_file, mode="r+") as f:
            await f.truncate(5)

        async with aiofiles.open(temp_file, mode="r") as f:
            content = await f.read()
            assert content == "01234"
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
