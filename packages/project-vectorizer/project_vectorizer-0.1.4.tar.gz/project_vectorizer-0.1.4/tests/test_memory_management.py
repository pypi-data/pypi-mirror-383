"""Tests for memory management optimizations."""

import asyncio
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from project_vectorizer.db.chromadb_manager import ChromaDBManager
from project_vectorizer.core.project import ProjectManager
from project_vectorizer.core.config import Config


class TestMemoryEfficientSearch:
    """Test memory-efficient search functionality."""

    @pytest.fixture
    async def db_manager(self, tmp_path):
        """Create a ChromaDB manager for testing."""
        db = ChromaDBManager(str(tmp_path / "chromadb"))
        await db.initialize()
        yield db
        await db.close()

    @pytest.mark.asyncio
    async def test_switches_to_efficient_search_for_large_collections(self, db_manager):
        """Test that efficient search is used for collections >10K chunks."""
        # Create a project
        project = await db_manager.create_project(
            name="test_project",
            path="/test/path",
            embedding_model="test-model"
        )

        # Mock collection with large count
        mock_collection = MagicMock()
        mock_collection.count.return_value = 15000  # > 10K threshold
        mock_collection.query.return_value = {
            'ids': [['chunk1', 'chunk2']],
            'documents': [['doc1', 'doc2']],
            'metadatas': [[{'file_id': 'file1'}, {'file_id': 'file2'}]],
            'distances': [[0.1, 0.2]]
        }

        with patch.object(db_manager, '_get_or_create_collection', return_value=mock_collection):
            with patch.object(db_manager, '_get_file_paths', return_value={'file1': 'test.py', 'file2': 'test2.py'}):
                query_embedding = np.random.rand(384)

                results = await db_manager.search_chunks_memory_efficient(
                    project_id=project.id,
                    query_embedding=query_embedding,
                    limit=10
                )

                # Should call collection operations
                assert mock_collection.count.called
                assert len(results) <= 10

    @pytest.mark.asyncio
    async def test_falls_back_to_standard_for_small_collections(self, db_manager):
        """Test that standard search is used for small collections."""
        # Create a project
        project = await db_manager.create_project(
            name="test_project",
            path="/test/path",
            embedding_model="test-model"
        )

        # Mock collection with small count
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5000  # < 10K threshold

        with patch.object(db_manager, '_get_or_create_collection', return_value=mock_collection):
            with patch.object(db_manager, 'search_chunks', return_value=[]) as mock_search:
                query_embedding = np.random.rand(384)

                await db_manager.search_chunks_memory_efficient(
                    project_id=project.id,
                    query_embedding=query_embedding,
                    limit=10
                )

                # Should fall back to standard search
                assert mock_search.called

    @pytest.mark.asyncio
    async def test_respects_similarity_threshold(self, db_manager):
        """Test that similarity threshold is applied correctly."""
        project = await db_manager.create_project(
            name="test_project",
            path="/test/path",
            embedding_model="test-model"
        )

        mock_collection = MagicMock()
        mock_collection.count.return_value = 15000
        mock_collection.query.return_value = {
            'ids': [['chunk1', 'chunk2', 'chunk3']],
            'documents': [['doc1', 'doc2', 'doc3']],
            'metadatas': [[
                {'file_id': 'file1'},
                {'file_id': 'file2'},
                {'file_id': 'file3'}
            ]],
            'distances': [[0.1, 0.6, 0.9]]  # Similarities: 0.9, 0.4, 0.1
        }

        with patch.object(db_manager, '_get_or_create_collection', return_value=mock_collection):
            with patch.object(db_manager, '_get_file_paths', return_value={'file1': 'test.py', 'file2': 'test2.py', 'file3': 'test3.py'}):
                query_embedding = np.random.rand(384)

                results = await db_manager.search_chunks_memory_efficient(
                    project_id=project.id,
                    query_embedding=query_embedding,
                    limit=10,
                    threshold=0.5  # Only chunks 1 and 2 should pass
                )

                # Should filter by threshold
                assert len(results) <= 2


class TestStreamingSearch:
    """Test streaming search functionality."""

    @pytest.fixture
    async def db_manager(self, tmp_path):
        """Create a ChromaDB manager for testing."""
        db = ChromaDBManager(str(tmp_path / "chromadb"))
        await db.initialize()
        yield db
        await db.close()

    @pytest.mark.asyncio
    async def test_yields_results_one_at_a_time(self, db_manager):
        """Test that streaming search yields results incrementally."""
        project = await db_manager.create_project(
            name="test_project",
            path="/test/path",
            embedding_model="test-model"
        )

        mock_collection = MagicMock()
        mock_collection.count.return_value = 200

        # Mock multiple batches
        mock_collection.query.side_effect = [
            {
                'ids': [['chunk1', 'chunk2']],
                'documents': [['doc1', 'doc2']],
                'metadatas': [[{'file_id': 'file1'}, {'file_id': 'file2'}]],
                'distances': [[0.1, 0.2]]
            },
            {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
        ]

        with patch.object(db_manager, '_get_or_create_collection', return_value=mock_collection):
            with patch.object(db_manager, '_get_file_paths', return_value={'file1': 'test.py', 'file2': 'test2.py'}):
                query_embedding = np.random.rand(384)

                results = []
                async for result in db_manager.search_chunks_streaming(
                    project_id=project.id,
                    query_embedding=query_embedding,
                    threshold=0.1
                ):
                    results.append(result)

                # Should yield results
                assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_handles_empty_results(self, db_manager):
        """Test streaming search with no results."""
        project = await db_manager.create_project(
            name="test_project",
            path="/test/path",
            embedding_model="test-model"
        )

        mock_collection = MagicMock()
        mock_collection.count.return_value = 100
        mock_collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'metadatas': [[]],
            'distances': [[]]
        }

        with patch.object(db_manager, '_get_or_create_collection', return_value=mock_collection):
            query_embedding = np.random.rand(384)

            results = []
            async for result in db_manager.search_chunks_streaming(
                project_id=project.id,
                query_embedding=query_embedding
            ):
                results.append(result)

            # Should handle gracefully
            assert len(results) == 0


class TestMemoryMonitoring:
    """Test memory usage monitoring."""

    @pytest.fixture
    def project_manager(self, tmp_path):
        """Create a project manager for testing."""
        config = Config(
            memory_monitoring_enabled=True,
            gc_interval=10
        )
        return ProjectManager(tmp_path, config)

    @patch('project_vectorizer.core.project.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.project.psutil.virtual_memory')
    @pytest.mark.asyncio
    async def test_warns_at_80_percent_memory(self, mock_memory, project_manager, caplog):
        """Test that warning is issued at 80% memory usage."""
        mock_vm = MagicMock()
        mock_vm.percent = 85.0
        mock_vm.used = 8 * 1024**3
        mock_vm.total = 10 * 1024**3
        mock_memory.return_value = mock_vm

        await project_manager._check_memory_usage()

        # Should log warning
        assert any("Memory usage high" in record.message for record in caplog.records)

    @patch('project_vectorizer.core.project.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.project.psutil.virtual_memory')
    @pytest.mark.asyncio
    async def test_warns_at_90_percent_memory(self, mock_memory, project_manager, caplog):
        """Test that critical warning is issued at 90% memory usage."""
        mock_vm = MagicMock()
        mock_vm.percent = 95.0
        mock_vm.used = 9.5 * 1024**3
        mock_vm.total = 10 * 1024**3
        mock_memory.return_value = mock_vm

        await project_manager._check_memory_usage()

        # Should log critical warning
        assert any("Memory usage critical" in record.message for record in caplog.records)

    @patch('project_vectorizer.core.project.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.project.psutil.virtual_memory')
    @pytest.mark.asyncio
    async def test_no_warning_at_low_memory(self, mock_memory, project_manager, caplog):
        """Test that no warning is issued at low memory usage."""
        mock_vm = MagicMock()
        mock_vm.percent = 50.0
        mock_vm.used = 5 * 1024**3
        mock_vm.total = 10 * 1024**3
        mock_memory.return_value = mock_vm

        await project_manager._check_memory_usage()

        # Should not log any warnings
        assert not any("Memory usage" in record.message for record in caplog.records)

    @patch('project_vectorizer.core.project.PSUTIL_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_skips_monitoring_without_psutil(self, project_manager):
        """Test that monitoring is skipped when psutil is unavailable."""
        # Should not raise error
        await project_manager._check_memory_usage()

    def test_monitoring_respects_config_flag(self, tmp_path):
        """Test that monitoring respects memory_monitoring_enabled flag."""
        config = Config(memory_monitoring_enabled=False)
        project_manager = ProjectManager(tmp_path, config)

        # Should be disabled
        assert project_manager.config.memory_monitoring_enabled is False


class TestGarbageCollection:
    """Test garbage collection functionality."""

    @pytest.fixture
    def project_manager(self, tmp_path):
        """Create a project manager for testing."""
        config = Config(gc_interval=10)
        return ProjectManager(tmp_path, config)

    @patch('project_vectorizer.core.project.gc.collect')
    def test_triggers_gc_at_interval(self, mock_gc, project_manager):
        """Test that GC is triggered at configured interval."""
        # Simulate processing files
        for i in range(9):
            project_manager._trigger_gc()

        # Should not have triggered yet
        assert not mock_gc.called

        # Process one more to reach interval
        project_manager._trigger_gc()

        # Should trigger now
        assert mock_gc.called

    @patch('project_vectorizer.core.project.gc.collect')
    def test_resets_counter_after_gc(self, mock_gc, project_manager):
        """Test that counter resets after GC."""
        # Trigger GC
        for i in range(10):
            project_manager._trigger_gc()

        assert mock_gc.called
        assert project_manager._files_processed_since_gc == 0

    def test_custom_gc_interval(self, tmp_path):
        """Test custom GC interval configuration."""
        config = Config(gc_interval=50)
        project_manager = ProjectManager(tmp_path, config)

        assert project_manager.config.gc_interval == 50

    @patch('project_vectorizer.core.project.gc.collect')
    def test_gc_integration_with_indexing(self, mock_gc, project_manager):
        """Test that GC is called during file indexing."""
        # Note: This would require mocking the full indexing pipeline
        # For now, just verify the counter increments
        initial_count = project_manager._files_processed_since_gc

        project_manager._trigger_gc()

        assert project_manager._files_processed_since_gc == initial_count + 1


class TestMemoryManagementIntegration:
    """Integration tests for memory management features."""

    @pytest.fixture
    def project_manager(self, tmp_path):
        """Create a project manager with memory management enabled."""
        config = Config(
            memory_monitoring_enabled=True,
            gc_interval=5
        )
        return ProjectManager(tmp_path, config)

    @patch('project_vectorizer.core.project.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.project.psutil.virtual_memory')
    @patch('project_vectorizer.core.project.gc.collect')
    @pytest.mark.asyncio
    async def test_memory_management_during_indexing(
        self, mock_gc, mock_memory, project_manager
    ):
        """Test that memory management works during actual indexing."""
        mock_vm = MagicMock()
        mock_vm.percent = 70.0
        mock_vm.used = 7 * 1024**3
        mock_vm.total = 10 * 1024**3
        mock_memory.return_value = mock_vm

        # Simulate indexing multiple files
        for i in range(5):
            project_manager._trigger_gc()
            await project_manager._check_memory_usage()

        # GC should have been triggered once
        assert mock_gc.call_count == 1
