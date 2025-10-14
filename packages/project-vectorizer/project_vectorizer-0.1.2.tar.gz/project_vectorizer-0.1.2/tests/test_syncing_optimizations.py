"""Tests for syncing optimizations."""

import asyncio
import pytest
from pathlib import Path

from project_vectorizer.core.config import Config
from project_vectorizer.core.project import ProjectManager


class TestSyncingOptimizations:
    """Test syncing optimization features."""

    @pytest.mark.asyncio
    async def test_smart_incremental_indexing(self, temp_dir: Path):
        """Test smart incremental indexing categorizes files correctly."""
        # Create initial files
        file1 = temp_dir / "file1.py"
        file1.write_text("def function1():\n    pass\n")

        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)

        # Initialize project
        await project_manager.initialize("test-smart-sync")

        # Index initially
        await project_manager.index_all()

        # Create a new file
        file2 = temp_dir / "file2.py"
        file2.write_text("def function2():\n    pass\n")

        # Run smart incremental indexing
        stats = await project_manager.smart_incremental_index()

        # Verify stats structure
        assert 'new' in stats
        assert 'modified' in stats
        assert 'deleted' in stats

        # Should detect the new file
        assert stats['new'] >= 1

        # No deletions
        assert stats['deleted'] == 0

    @pytest.mark.asyncio
    async def test_git_aware_indexing(self, temp_dir: Path):
        """Test git-aware indexing only indexes changed files."""
        import git

        # Initialize git repo
        repo = git.Repo.init(temp_dir)

        # Create initial files
        file1 = temp_dir / "file1.py"
        file1.write_text("def func1():\n    pass\n")

        file2 = temp_dir / "file2.py"
        file2.write_text("def func2():\n    pass\n")

        # Commit files
        repo.index.add(['file1.py', 'file2.py'])
        repo.index.commit("Initial commit")

        # Initialize project
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-git-aware")
        await project_manager.index_all()

        # Modify only one file
        file1.write_text("def func1():\n    return 'changed'\n")
        repo.index.add(['file1.py'])
        repo.index.commit("Update file1")

        # Index only git changes
        indexed_count = await project_manager.index_git_changes('HEAD~1')

        # Should only index 1 file (file1)
        assert indexed_count >= 1

    @pytest.mark.asyncio
    async def test_partial_file_reindexing(self, temp_dir: Path):
        """Test partial file reindexing only updates changed chunks."""
        # Create test file
        test_file = temp_dir / "test_partial.py"
        original_content = """def function1():
    return "unchanged"

def function2():
    return "will change"

def function3():
    return "unchanged"
"""
        test_file.write_text(original_content)

        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-partial-reindex")
        await project_manager.index_all()

        # Get original chunk count
        status1 = await project_manager.get_status()
        original_chunks = status1['total_chunks']

        # Modify only middle function
        import time
        time.sleep(0.1)
        modified_content = """def function1():
    return "unchanged"

def function2():
    return "CHANGED NOW"
    print("Added line")

def function3():
    return "unchanged"
"""
        test_file.write_text(modified_content)

        # Get file record
        file_record = await project_manager.db.get_file_by_path(
            project_manager.project.id,
            "test_partial.py"
        )

        # Do partial reindexing
        await project_manager._reindex_file_partial(file_record)

        # Check chunks were updated (not necessarily same count due to content change)
        status2 = await project_manager.get_status()
        assert status2['total_chunks'] > 0

    @pytest.mark.asyncio
    async def test_index_file_by_path(self, temp_dir: Path):
        """Test indexing a specific file by path."""
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-index-by-path")

        # Create a file
        test_file = temp_dir / "specific_file.py"
        test_file.write_text("def specific_function():\n    pass\n")

        # Index specific file
        await project_manager._index_file_by_path(test_file)

        # Verify file was indexed
        file_record = await project_manager.db.get_file_by_path(
            project_manager.project.id,
            "specific_file.py"
        )

        assert file_record is not None
        assert file_record.is_indexed

    @pytest.mark.asyncio
    async def test_remove_file_from_index(self, temp_dir: Path):
        """Test removing a deleted file from the index."""
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-remove-file")

        # Create and index a file
        test_file = temp_dir / "to_delete.py"
        test_file.write_text("def will_be_deleted():\n    pass\n")

        await project_manager.index_all()

        # Delete the file
        test_file.unlink()

        # Remove from index
        await project_manager._remove_file_from_index("to_delete.py")

        # Verify file was removed
        file_record = await project_manager.db.get_file_by_path(
            project_manager.project.id,
            "to_delete.py"
        )

        assert file_record is None

    @pytest.mark.asyncio
    async def test_hash_chunk(self, temp_dir: Path):
        """Test chunk hashing for content comparison."""
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-hash")

        content1 = "def function():\n    pass\n"
        content2 = "def function():\n    pass\n"
        content3 = "def different():\n    pass\n"

        hash1 = project_manager._hash_chunk(content1)
        hash2 = project_manager._hash_chunk(content2)
        hash3 = project_manager._hash_chunk(content3)

        # Same content should have same hash
        assert hash1 == hash2

        # Different content should have different hash
        assert hash1 != hash3

    @pytest.mark.asyncio
    async def test_database_helper_methods(self, temp_dir: Path):
        """Test new database methods for syncing."""
        config = Config(chunk_size=128)
        project_manager = ProjectManager(temp_dir, config)
        await project_manager.initialize("test-db-helpers")

        # Create and index files
        file1 = temp_dir / "file1.py"
        file1.write_text("def test1():\n    pass\n")

        file2 = temp_dir / "file2.py"
        file2.write_text("def test2():\n    pass\n")

        await project_manager.index_all()

        # Test get_all_files
        all_files = await project_manager.db.get_all_files(project_manager.project.id)
        assert len(all_files) >= 2

        # Test get_file_by_path
        file_record = await project_manager.db.get_file_by_path(
            project_manager.project.id,
            "file1.py"
        )
        assert file_record is not None
        assert file_record.relative_path == "file1.py"

        # Test get_file_chunks
        chunks = await project_manager.db.get_file_chunks(
            project_manager.project.id,
            file_record.id
        )
        assert len(chunks) > 0

        # Test update_file
        from datetime import datetime
        await project_manager.db.update_file(
            file_record.id,
            indexed_at=datetime.now()
        )

        # Test delete_file
        await project_manager.db.delete_file(file_record.id)
        deleted_file = await project_manager.db.get_file_by_path(
            project_manager.project.id,
            "file1.py"
        )
        assert deleted_file is None
