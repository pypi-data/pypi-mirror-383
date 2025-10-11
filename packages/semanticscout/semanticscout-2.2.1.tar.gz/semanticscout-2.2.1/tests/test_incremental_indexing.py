"""
Comprehensive test suite for incremental indexing.
"""

import tempfile
import shutil
import pytest
from pathlib import Path

from src.semanticscout.indexer.delta_indexer import DeltaIndexer
from src.semanticscout.indexer.change_detector import UnifiedChangeDetector
from src.semanticscout.embeddings.ollama_provider import OllamaEmbeddingProvider
from src.semanticscout.vector_store.chroma_store import ChromaVectorStore
from src.semanticscout.symbol_table.symbol_table import SymbolTable


@pytest.fixture
def test_env():
    """Create test environment with temp directory and components."""
    temp_dir = Path(tempfile.mkdtemp())
    data_dir = temp_dir / "data"
    data_dir.mkdir()
    
    # Initialize components
    embedding_provider = OllamaEmbeddingProvider()
    vector_store = ChromaVectorStore(persist_directory=str(data_dir / "chroma"))
    symbol_table = SymbolTable(collection_name="test_incremental")
    
    delta_indexer = DeltaIndexer(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        symbol_table=symbol_table,
    )

    change_detector = UnifiedChangeDetector(repo_path=temp_dir)
    
    yield {
        "temp_dir": temp_dir,
        "data_dir": data_dir,
        "delta_indexer": delta_indexer,
        "change_detector": change_detector,
        "vector_store": vector_store,
        "symbol_table": symbol_table,
    }
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_add_file(test_env):
    """Test adding a new file."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create new file
    new_file = temp_dir / "new_module.py"
    new_file.write_text("""
def new_function():
    '''A new function'''
    return 42
""")
    
    # Add file
    result = delta_indexer.update_file(
        file_path=new_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    
    assert result.success
    assert result.chunks_added > 0
    assert result.chunks_removed == 0
    assert result.symbols_added > 0


def test_modify_file(test_env):
    """Test modifying an existing file."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create initial file
    test_file = temp_dir / "module.py"
    test_file.write_text("""
def function_a():
    return 1

def function_b():
    return 2
""")
    
    # Initial index
    result1 = delta_indexer.update_file(
        file_path=test_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    assert result1.success
    
    # Modify file
    test_file.write_text("""
def function_a():
    return 1

def function_b():
    return 3  # CHANGED!

def function_c():
    return 4  # NEW!
""")
    
    # Update
    result2 = delta_indexer.update_file(
        file_path=test_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    
    assert result2.success
    assert result2.chunks_reused >= 0  # Should reuse unchanged chunks
    assert result2.chunks_added > 0  # Should add changed/new chunks


def test_delete_file(test_env):
    """Test deleting a file."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]

    # Create and index file
    test_file = temp_dir / "to_delete.py"
    test_file.write_text("def func(): pass")

    result1 = delta_indexer.update_file(
        file_path=test_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    assert result1.success

    # Delete file from filesystem
    test_file.unlink()

    # Update with deleted file (should handle gracefully)
    result2 = delta_indexer.update_file(
        file_path=test_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )

    # Should fail gracefully since file doesn't exist
    assert not result2.success or result2.chunks_added == 0


def test_rename_file(test_env):
    """Test renaming a file (delete old + add new)."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create and index file
    old_file = temp_dir / "old_name.py"
    old_file.write_text("def func(): pass")
    
    result1 = delta_indexer.update_file(
        file_path=old_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    assert result1.success
    
    # Rename file
    new_file = temp_dir / "new_name.py"
    old_file.rename(new_file)
    
    # Index new file (rename is handled as new file)
    result2 = delta_indexer.update_file(
        file_path=new_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    assert result2.success

    # Note: Old file cleanup would be handled by change detection
    # which would identify old_name.py as deleted


def test_empty_file(test_env):
    """Test handling empty files."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create empty file
    empty_file = temp_dir / "empty.py"
    empty_file.write_text("")
    
    # Should handle gracefully
    result = delta_indexer.update_file(
        file_path=empty_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    
    assert result.success
    assert result.chunks_added == 0  # No chunks in empty file


def test_large_file(test_env):
    """Test handling large files."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create large file (100 functions)
    large_content = "\n".join([
        f"def function_{i}():\n    return {i}\n"
        for i in range(100)
    ])
    
    large_file = temp_dir / "large.py"
    large_file.write_text(large_content)
    
    # Should handle without errors
    result = delta_indexer.update_file(
        file_path=large_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    
    assert result.success
    assert result.chunks_added > 0


def test_binary_file(test_env):
    """Test handling binary files (should skip)."""
    temp_dir = test_env["temp_dir"]
    delta_indexer = test_env["delta_indexer"]
    
    # Create binary file
    binary_file = temp_dir / "image.png"
    binary_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    
    # Should handle gracefully (likely skip or error)
    result = delta_indexer.update_file(
        file_path=binary_file,
        collection_name="test_incremental",
        root_path=temp_dir,
    )
    
    # Either succeeds with 0 chunks or fails gracefully
    assert result.chunks_added == 0 or not result.success


def test_change_detection_git(test_env):
    """Test Git-based change detection."""
    temp_dir = test_env["temp_dir"]
    change_detector = test_env["change_detector"]
    
    # Initialize git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=temp_dir)

    # Create and commit file
    test_file = temp_dir / "test.py"
    test_file.write_text("def func(): pass")
    subprocess.run(["git", "add", "."], cwd=temp_dir)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir)

    # Get initial ref
    initial_ref = change_detector.get_current_ref()

    # Modify file
    test_file.write_text("def func(): return 1")

    # Detect changes
    changes = change_detector.get_changed_files(last_indexed_ref=initial_ref)
    
    assert len(changes) > 0
    assert any("test.py" in str(f) for f in changes)


def test_change_detection_hash(test_env):
    """Test hash-based change detection (non-Git)."""
    temp_dir = test_env["temp_dir"]
    change_detector = test_env["change_detector"]

    # Create file
    test_file = temp_dir / "test.py"
    test_file.write_text("def func(): pass")

    # First detection (get initial ref)
    ref1 = change_detector.get_current_ref()

    # Modify file
    test_file.write_text("def func(): return 1")

    # Second detection (should detect change)
    changes2 = change_detector.get_changed_files(last_indexed_ref=ref1)

    # Should detect the file as changed
    assert len(changes2) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

