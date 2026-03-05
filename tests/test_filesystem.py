"""Tests for SimpleFileSystem."""

import pytest

from src.core.block_device import BlockDevice
from src.core.filesystem import SimpleFileSystem


@pytest.fixture
def fs():
    device = BlockDevice("fs-test", block_size=512, block_count=64)
    return SimpleFileSystem(device)


class TestSimpleFileSystem:
    def test_create_file(self, fs):
        inode = fs.create_file("hello.txt", b"Hello, World!")
        assert inode.name == "hello.txt"
        assert inode.size == 13

    def test_read_file(self, fs):
        fs.create_file("test.txt", b"IBM Storage")
        data = fs.read_file("test.txt")
        assert data == b"IBM Storage"

    def test_write_file(self, fs):
        fs.create_file("test.txt", b"original")
        fs.write_file("test.txt", b"updated content")
        assert fs.read_file("test.txt") == b"updated content"

    def test_delete_file(self, fs):
        fs.create_file("temp.txt", b"delete me")
        fs.delete_file("temp.txt")
        with pytest.raises(FileNotFoundError):
            fs.read_file("temp.txt")

    def test_list_files(self, fs):
        fs.create_file("a.txt", b"aaa")
        fs.create_file("b.txt", b"bbb")
        files = fs.list_files()
        names = [f.name for f in files]
        assert "a.txt" in names
        assert "b.txt" in names
        assert len(files) == 2

    def test_stat(self, fs):
        fs.create_file("info.txt", b"metadata test")
        inode = fs.stat("info.txt")
        assert inode.size == 13
        assert inode.inode_id > 0

    def test_duplicate_file_error(self, fs):
        fs.create_file("dup.txt", b"first")
        with pytest.raises(FileExistsError):
            fs.create_file("dup.txt", b"second")

    def test_read_nonexistent(self, fs):
        with pytest.raises(FileNotFoundError):
            fs.read_file("nope.txt")

    def test_large_file_spans_blocks(self, fs):
        big_data = b"\xAA" * 2048  # 4 blocks at 512 bytes each
        inode = fs.create_file("big.bin", big_data)
        assert len(inode.blocks) == 4
        assert fs.read_file("big.bin") == big_data

    def test_free_space_decreases(self, fs):
        initial_free = fs.free_space
        fs.create_file("file.txt", b"\x00" * 512)
        assert fs.free_space < initial_free

    def test_to_dict_serialization(self, fs):
        fs.create_file("serial.txt", b"data")
        d = fs.to_dict()
        assert d["device"] == "fs-test"
        assert len(d["files"]) == 1
        assert d["files"][0]["name"] == "serial.txt"
