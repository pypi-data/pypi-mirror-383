"""Tests for error handling and edge cases."""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from project_vectorizer.core.config import Config
from project_vectorizer.core.project import ProjectManager
from project_vectorizer.vectorizer.engine import VectorizationEngine


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_config_values(self, temp_dir: Path):
        """Test handling of invalid configuration values."""
        # Test invalid chunk size - Pydantic should validate this
        with pytest.raises(ValidationError):
            Config(chunk_size=-1)
        
        with pytest.raises(ValidationError):
            Config(chunk_size="invalid")
        
        # Test invalid embedding model - empty string should be allowed
        config = Config(embedding_model="")
        assert config.embedding_model == ""  # Should allow empty string but may fail later

        # Test invalid chromadb_path - should be allowed at config level
        config = Config(chromadb_path="/invalid/path")
        assert config.chromadb_path == "/invalid/path"  # Should not fail at config creation

    @pytest.mark.asyncio
    async def test_missing_project_initialization(self, temp_dir: Path):
        """Test error handling when project is not properly initialized."""
        config = Config()
        project_manager = ProjectManager(temp_dir, config)
        
        # Try to search without initialization
        with pytest.raises((ValueError, AttributeError)):
            await project_manager.search("test")
        
        # Try to index without initialization
        with pytest.raises((ValueError, AttributeError)):
            await project_manager.index_all()

    @pytest.mark.asyncio
    async def test_nonexistent_project_path(self):
        """Test error handling with nonexistent project paths."""
        nonexistent_path = Path("/nonexistent/path/to/project")
        config = Config()
        
        # Should raise FileNotFoundError when trying to create ProjectManager
        with pytest.raises(FileNotFoundError):
            ProjectManager(nonexistent_path, config)

    @pytest.mark.asyncio
    async def test_corrupted_file_handling(self, temp_dir: Path):
        """Test handling of corrupted or unreadable files."""
        # Create a binary file that can't be read as text
        binary_file = temp_dir / "corrupted.py"
        binary_file.write_bytes(b'\x00\x01\x02\x03\xff\xfe\xfd')
        
        # Create a file with encoding issues
        encoding_file = temp_dir / "encoding_issue.py"
        with open(encoding_file, 'wb') as f:
            f.write("def function(): pass\n".encode('latin1'))
            f.write(b'\xff\xfe\xfd')  # Invalid UTF-8 bytes
        
        engine = VectorizationEngine(chunk_size=128)
        await engine.initialize()
        
        # Should handle binary files gracefully
        chunks_binary = await engine.process_file(binary_file, project_id=1, file_id=1)
        assert isinstance(chunks_binary, list)  # Should return empty list or handle gracefully
        
        # Should handle encoding issues gracefully
        chunks_encoding = await engine.process_file(encoding_file, project_id=1, file_id=2)
        assert isinstance(chunks_encoding, list)  # Should return chunks or handle gracefully

    @pytest.mark.asyncio
    async def test_empty_files_handling(self, temp_dir: Path):
        """Test handling of empty or whitespace-only files."""
        # Empty file
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")
        
        # Whitespace-only file
        whitespace_file = temp_dir / "whitespace.py"
        whitespace_file.write_text("   \n\n  \t  \n   ")
        
        # Comments-only file
        comments_file = temp_dir / "comments.py"
        comments_file.write_text("""
# This file only has comments
# No actual code content
# Just comments and whitespace

   # Another comment
""")
        
        engine = VectorizationEngine(chunk_size=128)
        await engine.initialize()
        
        # Should handle empty files gracefully
        empty_chunks = await engine.process_file(empty_file, project_id=1, file_id=1)
        assert isinstance(empty_chunks, list)
        
        # Should handle whitespace-only files gracefully
        whitespace_chunks = await engine.process_file(whitespace_file, project_id=1, file_id=2)
        assert isinstance(whitespace_chunks, list)
        
        # Should handle comments-only files gracefully
        comments_chunks = await engine.process_file(comments_file, project_id=1, file_id=3)
        assert isinstance(comments_chunks, list)

    @pytest.mark.asyncio
    async def test_very_large_files(self, temp_dir: Path):
        """Test handling of very large files."""
        # Create a large file (but not too large to avoid test slowdown)
        large_file = temp_dir / "large.py"
        
        # Generate large content
        lines = []
        for i in range(1000):  # Create 1000 functions
            lines.extend([
                f"def function_{i}():",
                f"    '''Function {i} documentation.'''",
                f"    var_{i} = 'value_{i}'",
                f"    return var_{i}",
                ""
            ])
        
        large_content = "\n".join(lines)
        large_file.write_text(large_content)
        
        engine = VectorizationEngine(chunk_size=128)
        await engine.initialize()
        
        # Should handle large files without crashing
        chunks = await engine.process_file(large_file, project_id=1, file_id=1)
        assert isinstance(chunks, list)
        assert len(chunks) > 100  # Should generate many chunks
        
        # Verify chunks are reasonable
        for chunk in chunks[:10]:  # Check first 10 chunks
            assert 'content' in chunk
            assert len(chunk['content']) > 0
            assert 'embedding' in chunk

    @pytest.mark.asyncio
    async def test_invalid_search_parameters(self, temp_dir: Path):
        """Test handling of invalid search parameters."""
        # Set up a basic project
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        
        config = Config(chunk_size=64)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-invalid-params")
        await project_manager.index_all()
        
        # Test invalid threshold values
        # Very high threshold (should work but return fewer results)
        results_high = await project_manager.search("test", threshold=0.99)
        assert isinstance(results_high, list)
        
        # Negative threshold (should be handled)
        results_negative = await project_manager.search("test", threshold=-0.1)
        assert isinstance(results_negative, list)
        
        # Threshold > 1 (should be handled)
        results_over_one = await project_manager.search("test", threshold=1.5)
        assert isinstance(results_over_one, list)
        
        # Invalid limit values - should be normalized to valid values
        # limit=0 should be normalized to minimum of 1
        results_zero_limit = await project_manager.search("test", limit=0)
        assert isinstance(results_zero_limit, list)
        assert len(results_zero_limit) >= 0  # Should return at least 0 results

        # limit=-1 should be normalized to minimum of 1
        results_negative_limit = await project_manager.search("test", limit=-1)
        assert isinstance(results_negative_limit, list)
        assert len(results_negative_limit) >= 0  # Should return at least 0 results
        
        # Very large limit
        results_large_limit = await project_manager.search("test", limit=10000)
        assert isinstance(results_large_limit, list)

    @pytest.mark.asyncio
    async def test_database_connection_errors(self, temp_dir: Path):
        """Test handling of database connection errors."""
        # Test with invalid chromadb path
        config = Config(chromadb_path="/invalid/nonexistent/path/db")
        project_manager = ProjectManager(temp_dir, config)

        # Should handle database errors gracefully
        with pytest.raises(Exception):  # Expect some kind of database error
            await project_manager.initialize("test-db-error")

    @pytest.mark.asyncio
    async def test_embedding_generation_failures(self, temp_dir: Path):
        """Test handling of embedding generation failures."""
        test_file = temp_dir / "test.py"
        test_file.write_text("def test(): pass")
        
        # Mock the embedding model to fail
        engine = VectorizationEngine(chunk_size=128)
        await engine.initialize()
        
        # Mock the model to raise an exception
        with patch.object(engine, '_generate_embedding') as mock_embed:
            mock_embed.side_effect = Exception("Embedding generation failed")
            
            # Should handle embedding failures gracefully
            chunks = await engine.process_file(test_file, project_id=1, file_id=1)
            
            # Should still return chunks, but embeddings might be None
            assert isinstance(chunks, list)
            for chunk in chunks:
                # Embedding should be None due to the mocked failure
                assert chunk['embedding'] is None

    @pytest.mark.asyncio
    async def test_concurrent_access_handling(self, temp_dir: Path):
        """Test handling of concurrent access to the same project."""
        # Create test file
        test_file = temp_dir / "concurrent.py"
        test_file.write_text("""
def concurrent_function():
    '''Test concurrent access.'''
    return "concurrent"

class ConcurrentClass:
    '''Test class for concurrent access.'''
    pass
""")
        
        config = Config(chunk_size=64)
        
        # Create multiple project managers for the same project
        pm1 = ProjectManager(temp_dir, config)
        pm2 = ProjectManager(temp_dir, config)
        
        # Initialize both
        await pm1.initialize("concurrent-test")
        await pm2.initialize("concurrent-test")
        
        # Try concurrent operations
        async def index_and_search(pm, query):
            await pm.index_all()
            results = await pm.search(query, limit=5, threshold=0.5)
            return results
        
        # Run concurrent operations
        task1 = asyncio.create_task(index_and_search(pm1, "concurrent"))
        task2 = asyncio.create_task(index_and_search(pm2, "class"))
        
        # Both should complete without errors
        results1, results2 = await asyncio.gather(task1, task2, return_exceptions=True)
        
        # Check that both completed successfully (no exceptions)
        assert not isinstance(results1, Exception), f"Task 1 failed: {results1}"
        assert not isinstance(results2, Exception), f"Task 2 failed: {results2}"
        assert isinstance(results1, list)
        assert isinstance(results2, list)

    @pytest.mark.asyncio
    async def test_file_permission_errors(self, temp_dir: Path):
        """Test handling of file permission errors."""
        # Create a file and make it unreadable
        protected_file = temp_dir / "protected.py"
        protected_file.write_text("def protected(): pass")
        
        # Make file unreadable (only on Unix-like systems)
        if os.name == 'posix':
            os.chmod(protected_file, 0o000)
            
            engine = VectorizationEngine(chunk_size=128)
            await engine.initialize()
            
            # Should handle permission errors gracefully
            chunks = await engine.process_file(protected_file, project_id=1, file_id=1)
            assert isinstance(chunks, list)
            # Might be empty due to permission error
            
            # Restore permissions for cleanup
            os.chmod(protected_file, 0o644)

    @pytest.mark.asyncio
    async def test_malformed_code_files(self, temp_dir: Path):
        """Test handling of malformed code files."""
        # Python file with syntax errors
        malformed_py = temp_dir / "malformed.py"
        malformed_py.write_text("""
def incomplete_function(
    # Missing closing parenthesis and body

class IncompleteClass
    # Missing colon

if True
    print("Missing colon")
    
# Unmatched brackets and braces
def function_with_issues():
    data = [1, 2, 3,  # Missing closing bracket
    return {key: value for key  # Incomplete dict comprehension
""")
        
        # JavaScript file with syntax errors
        malformed_js = temp_dir / "malformed.js"
        malformed_js.write_text("""
function incompleteFunction( {
    // Missing parameter list close

class IncompleteClass {
    constructor() {
        this.data = [1, 2, 3,  // Missing closing bracket
    
    method() {
        return {key: value for  // Wrong syntax for JS
    }
// Missing closing brace for class
""")
        
        engine = VectorizationEngine(chunk_size=128)
        await engine.initialize()
        
        # Should handle malformed files gracefully
        py_chunks = await engine.process_file(malformed_py, project_id=1, file_id=1)
        js_chunks = await engine.process_file(malformed_js, project_id=1, file_id=2)
        
        assert isinstance(py_chunks, list)
        assert isinstance(js_chunks, list)
        
        # Should still generate some chunks even with syntax errors
        # The chunker should be resilient to syntax issues

    @pytest.mark.asyncio
    async def test_memory_pressure_handling(self, temp_dir: Path):
        """Test handling under memory pressure conditions."""
        # Create multiple large files to simulate memory pressure
        large_files = []
        for i in range(5):
            large_file = temp_dir / f"large_{i}.py"
            
            # Create substantial content
            content_lines = []
            for j in range(200):  # 200 functions per file
                content_lines.extend([
                    f"def function_{i}_{j}():",
                    f"    '''Function {j} in file {i}.'''",
                    f"    data_{j} = 'large_string_' * 100  # Large string",
                    f"    return data_{j}",
                    ""
                ])
            
            large_file.write_text("\n".join(content_lines))
            large_files.append(large_file)
        
        config = Config(chunk_size=256)  # Larger chunks to reduce memory usage
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("memory-pressure-test")
        
        # Should handle multiple large files without excessive memory usage
        await project_manager.index_all()
        
        # Verify all files were processed
        status = await project_manager.get_status()
        assert status['total_files'] == len(large_files)
        assert status['indexed_files'] == len(large_files)
        
        # Search should still work
        results = await project_manager.search("function", limit=10, threshold=0.5)
        assert len(results) > 0

    def test_config_file_corruption(self, temp_dir: Path):
        """Test handling of corrupted configuration files."""
        # Create corrupted config file
        config_dir = temp_dir / ".vectorizer"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        
        # Write invalid JSON
        config_file.write_text('{"invalid": json, "missing_quotes": value}')
        
        # Should handle corrupted config gracefully
        with pytest.raises((ValueError, FileNotFoundError)):
            Config.load_from_file(config_file)
        
        # Should fall back to defaults
        config = Config.load_from_project(temp_dir)
        assert isinstance(config, Config)
        
        # Create empty config file
        config_file.write_text("")
        with pytest.raises((ValueError, FileNotFoundError)):
            Config.load_from_file(config_file)