"""
Tests for aiofiles.tempfile module.

Aiofiles-X
Copyright (C) 2025 ohmyarthur

This file is part of <https://github.com/ohmyarthur/aiofiles-x/>
Please read the GNU Affero General Public License in
<https://github.com/ohmyarthur/aiofiles-x/blob/master/LICENSE/>.
"""

import os
import pytest

try:
    import aiofiles.tempfile
except ImportError:
    pytest.skip("aiofiles not installed", allow_module_level=True)


@pytest.mark.asyncio
async def test_temporary_file():
    """Test TemporaryFile."""
    async with aiofiles.tempfile.TemporaryFile("w+") as f:
        await f.write("Temporary data")
        await f.seek(0)
        content = await f.read()
        assert content == "Temporary data"


@pytest.mark.asyncio
async def test_named_temporary_file():
    """Test NamedTemporaryFile."""
    filename = None
    async with aiofiles.tempfile.NamedTemporaryFile("w+", delete=False) as f:
        filename = f.name
        await f.write("Named temporary data")
        await f.seek(0)
        content = await f.read()
        assert content == "Named temporary data"

    assert os.path.exists(filename)

    os.unlink(filename)


@pytest.mark.asyncio
async def test_named_temporary_file_delete():
    """Test NamedTemporaryFile with auto-delete."""
    async with aiofiles.tempfile.NamedTemporaryFile("w+", delete=True) as f:
        await f.write("Data")


@pytest.mark.asyncio
async def test_spooled_temporary_file():
    """Test SpooledTemporaryFile."""
    async with aiofiles.tempfile.SpooledTemporaryFile(max_size=1024, mode="w+") as f:
        await f.write("Spooled temporary data")
        await f.seek(0)
        content = await f.read()
        assert content == "Spooled temporary data"


@pytest.mark.asyncio
async def test_temporary_directory():
    """Test TemporaryDirectory."""
    dirname = None
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        dirname = tmpdir
        assert os.path.isdir(dirname)

        test_file = os.path.join(dirname, "test.txt")
        with open(test_file, "w") as f:
            f.write("Test")

        assert os.path.exists(test_file)


@pytest.mark.asyncio
async def test_binary_temporary_file():
    """Test binary mode in TemporaryFile."""
    async with aiofiles.tempfile.TemporaryFile("w+b") as f:
        data = b"Binary \x00\x01\x02 data"
        await f.write(data)
        await f.seek(0)
        content = await f.read()
        assert content == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
