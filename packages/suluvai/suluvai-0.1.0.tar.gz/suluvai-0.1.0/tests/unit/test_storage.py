"""
Unit Tests: Storage Systems
Tests virtual, local, and hybrid storage implementations
Developed by SagaraGlobal
"""
import pytest
import tempfile
from pathlib import Path
from suluvai.storage import VirtualStorage, LocalStorage, HybridStorage


class TestVirtualStorage:
    """Test VirtualStorage (in-memory) operations"""
    
    def test_create(self):
        """Test VirtualStorage creation"""
        storage = VirtualStorage()
        assert storage is not None
        assert storage.files == {}
    
    def test_write_read(self):
        """Test writing and reading files"""
        storage = VirtualStorage()
        storage.write_file("test.txt", "Hello World")
        content = storage.read_file("test.txt")
        assert content == "Hello World"
    
    def test_nested_directories(self):
        """Test multi-level directory support"""
        storage = VirtualStorage()
        storage.write_file("dir1/dir2/dir3/file.txt", "nested content")
        content = storage.read_file("dir1/dir2/dir3/file.txt")
        assert content == "nested content"
    
    def test_list_files(self):
        """Test listing files"""
        storage = VirtualStorage()
        storage.write_file("file1.txt", "content1")
        storage.write_file("file2.txt", "content2")
        storage.write_file("dir/file3.txt", "content3")
        
        files = storage.list_files()
        assert "file1.txt" in files
        assert "file2.txt" in files
        assert "dir/file3.txt" in files
        assert len(files) == 3
    
    def test_delete(self):
        """Test deleting files"""
        storage = VirtualStorage()
        storage.write_file("test.txt", "content")
        assert "test.txt" in storage.files
        
        result = storage.delete_file("test.txt")
        assert result is True
        assert "test.txt" not in storage.files
    
    def test_search_pattern(self):
        """Test searching files with glob patterns"""
        storage = VirtualStorage()
        storage.write_file("test1.txt", "content")
        storage.write_file("test2.txt", "content")
        storage.write_file("data.csv", "content")
        storage.write_file("dir/test3.txt", "content")
        
        txt_files = storage.search_files("*.txt")
        assert len(txt_files) >= 2
        assert any("test1.txt" in f for f in txt_files)
        assert any("test2.txt" in f for f in txt_files)
    
    def test_copy_file(self):
        """Test copying files"""
        storage = VirtualStorage()
        storage.write_file("source.txt", "original content")
        storage.copy_file("source.txt", "dest.txt")
        
        assert "source.txt" in storage.files
        assert "dest.txt" in storage.files
        assert storage.read_file("dest.txt") == "original content"
    
    def test_move_file(self):
        """Test moving files"""
        storage = VirtualStorage()
        storage.write_file("source.txt", "content")
        storage.move_file("source.txt", "dest.txt")
        
        assert "source.txt" not in storage.files
        assert "dest.txt" in storage.files
        assert storage.read_file("dest.txt") == "content"
    
    def test_get_tree(self):
        """Test getting directory tree structure"""
        storage = VirtualStorage()
        storage.write_file("a/file1.txt", "content")
        storage.write_file("a/b/file2.txt", "content")
        storage.write_file("c/file3.txt", "content")
        
        tree = storage.get_tree()
        assert tree is not None
        assert isinstance(tree, dict)


class TestLocalStorage:
    """Test LocalStorage (disk-based) operations"""
    
    def test_create(self):
        """Test LocalStorage creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            assert storage is not None
            assert Path(tmpdir).exists()
    
    def test_write_read(self):
        """Test writing and reading files to disk"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            storage.write_file("test.txt", "Hello Disk")
            content = storage.read_file("test.txt")
            
            assert content == "Hello Disk"
            assert Path(tmpdir, "test.txt").exists()
    
    def test_nested_directories(self):
        """Test nested directories on disk"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            storage.write_file("a/b/c/deep.txt", "deep content")
            content = storage.read_file("a/b/c/deep.txt")
            
            assert content == "deep content"
            assert Path(tmpdir, "a", "b", "c", "deep.txt").exists()
    
    def test_list_files(self):
        """Test listing files on disk"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            storage.write_file("file1.txt", "content")
            storage.write_file("dir/file2.txt", "content")
            
            files = storage.list_files()
            assert len(files) >= 2
    
    def test_delete(self):
        """Test deleting files from disk"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalStorage(tmpdir)
            storage.write_file("test.txt", "content")
            assert Path(tmpdir, "test.txt").exists()
            
            storage.delete_file("test.txt")
            assert not Path(tmpdir, "test.txt").exists()


class TestHybridStorage:
    """Test HybridStorage (virtual + local) operations"""
    
    def test_create(self):
        """Test HybridStorage creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = HybridStorage(tmpdir)
            assert storage is not None
            assert hasattr(storage, 'virtual')
            assert hasattr(storage, 'local')
    
    def test_virtual_files(self):
        """Test that temp files go to virtual storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = HybridStorage(tmpdir)
            storage.write_file("temp.txt", "temporary")
            
            # Should be in virtual, not on disk
            assert "temp.txt" in storage.virtual.files
            assert not Path(tmpdir, "temp.txt").exists()
    
    def test_local_files(self):
        """Test that output files go to local storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = HybridStorage(tmpdir)
            storage.write_file("output/result.txt", "final output")
            
            # Should be on disk
            content = storage.read_file("output/result.txt")
            assert content == "final output"
            assert Path(tmpdir, "output", "result.txt").exists()
    
    def test_read_from_both(self):
        """Test reading from both virtual and local"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = HybridStorage(tmpdir)
            storage.write_file("temp.txt", "virtual content")
            storage.write_file("output/saved.txt", "local content")
            
            assert storage.read_file("temp.txt") == "virtual content"
            assert storage.read_file("output/saved.txt") == "local content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
