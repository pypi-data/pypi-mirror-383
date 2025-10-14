"""
Tests for aiofiles.os module.

Aiofiles-X
Copyright (C) 2025 ohmyarthur

This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
Please read the GNU Affero General Public License in
<https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.
"""

import os
import tempfile
import pytest

try:
    import aiofiles.os
except ImportError:
    pytest.skip("aiofiles not installed", allow_module_level=True)


@pytest.mark.asyncio
async def test_stat():
    """Test stat operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_file = tf.name
        tf.write(b"Test data")

    try:
        stat_result = await aiofiles.os.stat(temp_file)
        assert stat_result.st_size == 9
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_rename():
    """Test rename operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        old_name = tf.name

    new_name = old_name + ".renamed"

    try:
        await aiofiles.os.rename(old_name, new_name)
        assert os.path.exists(new_name)
        assert not os.path.exists(old_name)
    finally:
        if os.path.exists(new_name):
            os.unlink(new_name)
        if os.path.exists(old_name):
            os.unlink(old_name)


@pytest.mark.asyncio
async def test_remove():
    """Test remove operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_file = tf.name

    assert os.path.exists(temp_file)
    await aiofiles.os.remove(temp_file)
    assert not os.path.exists(temp_file)


@pytest.mark.asyncio
async def test_mkdir_rmdir():
    """Test mkdir and rmdir operations."""
    temp_dir = tempfile.mktemp()

    try:
        await aiofiles.os.mkdir(temp_dir)
        assert os.path.isdir(temp_dir)

        await aiofiles.os.rmdir(temp_dir)
        assert not os.path.exists(temp_dir)
    finally:
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)


@pytest.mark.asyncio
async def test_listdir():
    """Test listdir operation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(3):
            open(os.path.join(tmpdir, f"file{i}.txt"), "w").close()

        files = await aiofiles.os.listdir(tmpdir)
        assert len(files) == 3
        assert "file0.txt" in files
        assert "file1.txt" in files
        assert "file2.txt" in files


@pytest.mark.asyncio
async def test_getcwd():
    """Test getcwd operation."""
    cwd = await aiofiles.os.getcwd()
    assert cwd == os.getcwd()


@pytest.mark.asyncio
async def test_path_exists():
    """Test path.exists operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_file = tf.name

    try:
        exists = await aiofiles.os.path.exists(temp_file)
        assert exists is True

        await aiofiles.os.remove(temp_file)
        exists = await aiofiles.os.path.exists(temp_file)
        assert exists is False
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_path_isfile():
    """Test path.isfile operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_file = tf.name

    try:
        is_file = await aiofiles.os.path.isfile(temp_file)
        assert is_file is True
    finally:
        os.unlink(temp_file)


@pytest.mark.asyncio
async def test_path_isdir():
    """Test path.isdir operation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        is_dir = await aiofiles.os.path.isdir(tmpdir)
        assert is_dir is True


@pytest.mark.asyncio
async def test_path_getsize():
    """Test path.getsize operation."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_file = tf.name
        tf.write(b"12345")

    try:
        size = await aiofiles.os.path.getsize(temp_file)
        assert size == 5
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
