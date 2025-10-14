"""Tests for optimized config generation."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from project_vectorizer.core.config import Config


class TestOptimizedConfig:
    """Test Config.create_optimized() method."""

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_high_end_system(self, mock_memory, mock_cpu):
        """Test optimization for high-end system (32GB RAM, 8 cores)."""
        mock_cpu.return_value = 8
        mock_vm = MagicMock()
        mock_vm.total = 32 * 1024**3  # 32GB
        mock_vm.available = 16 * 1024**3  # 16GB available
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should set optimal workers: min(8 * 2, 16) = 16
        assert config.max_workers == 16

        # Should set large batch sizes
        # safe_batch_multiplier = 16 * 0.5 = 8
        # optimal_batch_size = min(8 * 100, 500) = 500
        assert config.batch_size == 500
        assert config.embedding_batch_size == 250

        # Should use high threshold for 32GB RAM
        assert config.memory_efficient_search_threshold == 50000

        # Should use relaxed GC for high memory
        assert config.gc_interval == 200

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_mid_range_system(self, mock_memory, mock_cpu):
        """Test optimization for mid-range system (16GB RAM, 4 cores)."""
        mock_cpu.return_value = 4
        mock_vm = MagicMock()
        mock_vm.total = 16 * 1024**3  # 16GB
        mock_vm.available = 8 * 1024**3  # 8GB available
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should set optimal workers: min(4 * 2, 16) = 8
        assert config.max_workers == 8

        # Should set moderate batch sizes
        # safe_batch_multiplier = 8 * 0.5 = 4
        # optimal_batch_size = min(4 * 100, 500) = 400
        assert config.batch_size == 400
        assert config.embedding_batch_size == 200

        # Should use mid threshold for 16GB RAM
        assert config.memory_efficient_search_threshold == 20000

        # Should use standard GC
        assert config.gc_interval == 100

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_low_end_system(self, mock_memory, mock_cpu):
        """Test optimization for low-end system (4GB RAM, 2 cores)."""
        mock_cpu.return_value = 2
        mock_vm = MagicMock()
        mock_vm.total = 4 * 1024**3  # 4GB
        mock_vm.available = 2 * 1024**3  # 2GB available
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should set minimal workers: min(2 * 2, 16) = 4
        assert config.max_workers == 4

        # Should set conservative batch sizes
        # safe_batch_multiplier = 2 * 0.5 = 1
        # optimal_batch_size = max(50, min(1 * 100, 500)) = 100
        assert config.batch_size == 100
        assert config.embedding_batch_size == 50

        # Should use low threshold for <8GB RAM
        assert config.memory_efficient_search_threshold == 5000

        # Should use very aggressive GC for <4GB available RAM
        assert config.gc_interval == 25

        # Should enable memory monitoring for <16GB RAM
        assert config.memory_monitoring_enabled is True

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_with_overrides(self, mock_memory, mock_cpu):
        """Test that overrides work with optimized config."""
        mock_cpu.return_value = 8
        mock_vm = MagicMock()
        mock_vm.total = 16 * 1024**3
        mock_vm.available = 8 * 1024**3
        mock_memory.return_value = mock_vm

        # Override some parameters
        config = Config.create_optimized(
            embedding_model="text-embedding-ada-002",
            embedding_provider="openai",
            max_workers=12,  # Override the auto-detected value
            chunk_size=512
        )

        # Overrides should be applied
        assert config.embedding_model == "text-embedding-ada-002"
        assert config.embedding_provider == "openai"
        assert config.max_workers == 12  # Should use override, not auto-detected 16
        assert config.chunk_size == 512

        # Auto-optimized values should still be set for non-overridden params
        assert config.batch_size == 400
        assert config.embedding_batch_size == 200
        assert config.gc_interval == 100

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', False)
    def test_create_optimized_without_psutil(self):
        """Test that create_optimized falls back gracefully without psutil."""
        config = Config.create_optimized()

        # Should fall back to default values
        assert config.max_workers == 4
        assert config.batch_size == 100
        assert config.embedding_batch_size == 100
        assert config.gc_interval == 100
        assert config.memory_efficient_search_threshold == 10000

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_caps_at_16_workers(self, mock_memory, mock_cpu):
        """Test that max_workers is capped at 16 even on high-core systems."""
        mock_cpu.return_value = 32  # 32 core system
        mock_vm = MagicMock()
        mock_vm.total = 64 * 1024**3  # 64GB
        mock_vm.available = 32 * 1024**3
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should cap at 16: min(32 * 2, 16) = 16
        assert config.max_workers == 16

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_very_low_memory(self, mock_memory, mock_cpu):
        """Test optimization for very low memory system (<4GB available)."""
        mock_cpu.return_value = 2
        mock_vm = MagicMock()
        mock_vm.total = 4 * 1024**3
        mock_vm.available = 1 * 1024**3  # Only 1GB available
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should use minimum batch size (50)
        # safe_batch_multiplier = 1 * 0.5 = 0.5 (int = 0)
        # optimal_batch_size = max(50, min(0 * 100, 500)) = 50
        assert config.batch_size == 50
        assert config.embedding_batch_size == 50

        # Should use very aggressive GC
        assert config.gc_interval == 25

        # Should enable memory monitoring
        assert config.memory_monitoring_enabled is True

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_and_save(self, mock_memory, mock_cpu, tmp_path):
        """Test that optimized config can be saved and loaded."""
        mock_cpu.return_value = 8
        mock_vm = MagicMock()
        mock_vm.total = 16 * 1024**3
        mock_vm.available = 8 * 1024**3
        mock_memory.return_value = mock_vm

        # Create optimized config
        config = Config.create_optimized(
            embedding_model="all-MiniLM-L6-v2"
        )

        # Save to file
        config_file = tmp_path / "config.json"
        config.save_to_file(config_file)

        # Load from file
        loaded_config = Config.load_from_file(config_file)

        # Verify all optimized values are preserved
        assert loaded_config.max_workers == config.max_workers
        assert loaded_config.batch_size == config.batch_size
        assert loaded_config.embedding_batch_size == config.embedding_batch_size
        assert loaded_config.gc_interval == config.gc_interval
        assert loaded_config.memory_efficient_search_threshold == config.memory_efficient_search_threshold
        assert loaded_config.memory_monitoring_enabled == config.memory_monitoring_enabled

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_create_optimized_8gb_system(self, mock_memory, mock_cpu):
        """Test optimization for typical 8GB RAM system."""
        mock_cpu.return_value = 4
        mock_vm = MagicMock()
        mock_vm.total = 8 * 1024**3  # 8GB
        mock_vm.available = 4 * 1024**3  # 4GB available
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should set optimal workers: min(4 * 2, 16) = 8
        assert config.max_workers == 8

        # Should set moderate batch sizes
        # safe_batch_multiplier = 4 * 0.5 = 2
        # optimal_batch_size = min(2 * 100, 500) = 200
        assert config.batch_size == 200
        assert config.embedding_batch_size == 100

        # Should use standard threshold for 8GB RAM
        assert config.memory_efficient_search_threshold == 10000

        # Should use aggressive GC for <8GB available RAM (4GB available)
        assert config.gc_interval == 50

        # Should enable memory monitoring for <16GB RAM
        assert config.memory_monitoring_enabled is True
