"""
tests/test_search_utils.py - Async tests for search utilities
"""

import pytest

from chuk_virtual_fs.node_info import EnhancedNodeInfo
from chuk_virtual_fs.providers.memory import AsyncMemoryStorageProvider
from chuk_virtual_fs.search_utils import SearchUtils


@pytest.fixture
async def memory_provider():
    """Create an async memory storage provider with test structure"""
    provider = AsyncMemoryStorageProvider()
    await provider.initialize()

    # Create test directory structure
    await provider.create_node(EnhancedNodeInfo("test_search", True, "/"))

    # Create nested directory
    await provider.create_node(EnhancedNodeInfo("nested", True, "/test_search"))

    # Create test files
    test_files = [
        ("file1.txt", "/test_search"),
        ("file2.txt", "/test_search"),
        ("document.doc", "/test_search"),
        ("script.py", "/test_search"),
        ("file3.txt", "/test_search/nested"),
        ("file4.log", "/test_search/nested"),
    ]

    for file_name, parent_path in test_files:
        await provider.create_node(EnhancedNodeInfo(file_name, False, parent_path))

    yield provider
    await provider.close()


@pytest.mark.asyncio
async def test_find_all_files(memory_provider):
    """Test finding all files in a directory"""
    results = await SearchUtils.find(memory_provider, "/test_search")

    assert len(results) == 7  # 6 files + 1 nested directory
    assert set(results) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/document.doc",
        "/test_search/script.py",
        "/test_search/nested",
        "/test_search/nested/file3.txt",
        "/test_search/nested/file4.log",
    }


@pytest.mark.asyncio
async def test_find_non_recursive(memory_provider):
    """Test finding files without recursing into subdirectories"""
    results = await SearchUtils.find(memory_provider, "/test_search", recursive=False)

    assert len(results) == 5  # 4 files + 1 nested directory
    assert set(results) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/document.doc",
        "/test_search/script.py",
        "/test_search/nested",
    }


@pytest.mark.asyncio
async def test_search_with_wildcard(memory_provider):
    """Test searching files with wildcard pattern"""
    # Find all text files
    txt_files = await SearchUtils.search(memory_provider, "/test_search", "*.txt")
    assert len(txt_files) == 2  # Only top-level txt files
    assert set(txt_files) == {"/test_search/file1.txt", "/test_search/file2.txt"}

    # Find all text files recursively
    txt_files_recursive = await SearchUtils.search(
        memory_provider, "/test_search", "*.txt", recursive=True
    )
    assert len(txt_files_recursive) == 3
    assert set(txt_files_recursive) == {
        "/test_search/file1.txt",
        "/test_search/file2.txt",
        "/test_search/nested/file3.txt",
    }

    # Find log files
    log_files = await SearchUtils.search(
        memory_provider, "/test_search", "*.log", recursive=True
    )
    assert len(log_files) == 1
    assert log_files == ["/test_search/nested/file4.log"]


@pytest.mark.asyncio
async def test_search_in_subdirectory(memory_provider):
    """Test searching in a specific subdirectory"""
    nested_files = await SearchUtils.search(
        memory_provider, "/test_search/nested", "*.txt"
    )
    assert len(nested_files) == 1
    assert nested_files == ["/test_search/nested/file3.txt"]


@pytest.mark.asyncio
async def test_search_no_matches(memory_provider):
    """Test searching with a pattern that doesn't match any files"""
    no_matches = await SearchUtils.search(memory_provider, "/test_search", "*.xml")
    assert len(no_matches) == 0
