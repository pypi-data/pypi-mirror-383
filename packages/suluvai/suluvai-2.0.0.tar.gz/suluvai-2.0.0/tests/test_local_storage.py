"""
Tests for local storage functionality
"""

import pytest
from suluvai.local_storage import LocalFileStorage, FileMetadata


def test_create_storage(temp_storage_path):
    """Test storage initialization"""
    storage = LocalFileStorage(temp_storage_path)
    assert storage.base_path.exists()
    assert storage.metadata_file.exists()


def test_write_and_read_file(temp_storage_path):
    """Test writing and reading files"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write file
    content = "Hello, World!"
    metadata = storage.write_file("test.txt", content)
    
    assert metadata.path == "test.txt"
    assert metadata.size == len(content.encode('utf-8'))
    
    # Read file
    read_content = storage.read_file("test.txt")
    assert read_content == content


def test_nested_directories(temp_storage_path):
    """Test multi-level directory creation"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write to nested path
    storage.write_file("data/sales/2024/q1.csv", "product,revenue\nA,1000")
    
    # Verify file exists
    content = storage.read_file("data/sales/2024/q1.csv")
    assert "product,revenue" in content


def test_list_files(temp_storage_path, sample_files):
    """Test listing files"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write sample files
    for path, content in sample_files.items():
        storage.write_file(path, content)
    
    # List all files
    all_files = storage.list_files()
    assert len(all_files) == len(sample_files)
    
    # List files in specific directory
    data_files = storage.list_files("data", recursive=False)
    assert len(data_files) == 1
    assert any("sales.csv" in f for f in data_files)


def test_search_files(temp_storage_path, sample_files):
    """Test file search"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write sample files
    for path, content in sample_files.items():
        storage.write_file(path, content)
    
    # Search for CSV files
    csv_files = storage.search_files("*.csv")
    assert len(csv_files) == 1
    assert "sales.csv" in csv_files[0]
    
    # Search for markdown files
    md_files = storage.search_files("*.md")
    assert len(md_files) == 1


def test_delete_file(temp_storage_path):
    """Test file deletion"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write and delete
    storage.write_file("temp.txt", "temporary")
    assert storage.delete_file("temp.txt")
    
    # Verify deletion
    with pytest.raises(FileNotFoundError):
        storage.read_file("temp.txt")


def test_copy_and_move_file(temp_storage_path):
    """Test file copy and move operations"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write original file
    storage.write_file("original.txt", "content")
    
    # Copy file
    storage.copy_file("original.txt", "copy.txt")
    assert storage.read_file("copy.txt") == "content"
    assert storage.read_file("original.txt") == "content"
    
    # Move file
    storage.move_file("copy.txt", "moved.txt")
    assert storage.read_file("moved.txt") == "content"
    with pytest.raises(FileNotFoundError):
        storage.read_file("copy.txt")


def test_directory_tree(temp_storage_path, sample_files):
    """Test directory tree generation"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write sample files
    for path, content in sample_files.items():
        storage.write_file(path, content)
    
    # Get tree
    tree = storage.get_tree()
    assert "data" in tree
    assert "reports" in tree


def test_storage_info(temp_storage_path, sample_files):
    """Test storage information"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Write sample files
    for path, content in sample_files.items():
        storage.write_file(path, content)
    
    # Get info
    info = storage.get_storage_info()
    assert info["total_files"] == len(sample_files)
    assert info["total_size_bytes"] > 0
    assert "base_path" in info


def test_create_and_list_directories(temp_storage_path):
    """Test directory operations"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Create directories
    storage.create_directory("dir1/subdir1")
    storage.create_directory("dir2/subdir2")
    
    # List directories
    dirs = storage.list_directories()
    assert len(dirs) >= 2
    assert any("dir1" in d for d in dirs)
    assert any("dir2" in d for d in dirs)


def test_metadata_persistence(temp_storage_path):
    """Test metadata persistence across instances"""
    # Create storage and write file
    storage1 = LocalFileStorage(temp_storage_path)
    storage1.write_file("test.txt", "content")
    
    # Create new storage instance
    storage2 = LocalFileStorage(temp_storage_path)
    
    # Verify metadata persisted
    metadata = storage2.get_metadata("test.txt")
    assert metadata is not None
    assert metadata.path == "test.txt"


def test_security_path_validation(temp_storage_path):
    """Test path security validation"""
    storage = LocalFileStorage(temp_storage_path)
    
    # Try to write outside base path
    with pytest.raises(ValueError):
        storage.write_file("../outside.txt", "content")
    
    with pytest.raises(ValueError):
        storage.write_file("../../etc/passwd", "content")
