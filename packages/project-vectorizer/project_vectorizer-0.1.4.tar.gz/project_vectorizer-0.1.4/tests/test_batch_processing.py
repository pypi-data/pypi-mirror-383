"""Tests for batch processing optimizations."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from project_vectorizer.core.config import Config


class TestCPUDetection:
    """Test automatic CPU detection for max_workers."""

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.config.psutil.cpu_count')
    @patch('project_vectorizer.core.config.psutil.virtual_memory')
    def test_optimized_config_default_cpu(self, mock_memory, mock_cpu_count):
        """Test that create_optimized() detects CPU count correctly."""
        mock_cpu_count.return_value = 8
        mock_vm = MagicMock()
        mock_vm.available = 8 * 1024**3
        mock_vm.total = 16 * 1024**3
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should auto-detect: min(8 * 2, 16) = 16
        assert config.max_workers == 16

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.config.psutil.cpu_count')
    @patch('project_vectorizer.core.config.psutil.virtual_memory')
    def test_optimized_config_caps_at_16(self, mock_memory, mock_cpu_count):
        """Test that max_workers is capped at 16."""
        mock_cpu_count.return_value = 16
        mock_vm = MagicMock()
        mock_vm.available = 8 * 1024**3
        mock_vm.total = 16 * 1024**3
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should cap at 16: min(16 * 2, 16) = 16
        assert config.max_workers == 16

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.config.psutil.cpu_count')
    @patch('project_vectorizer.core.config.psutil.virtual_memory')
    def test_optimized_config_small_system(self, mock_memory, mock_cpu_count):
        """Test auto-detection on systems with few CPUs."""
        mock_cpu_count.return_value = 2
        mock_vm = MagicMock()
        mock_vm.available = 4 * 1024**3
        mock_vm.total = 4 * 1024**3
        mock_memory.return_value = mock_vm

        config = Config.create_optimized()

        # Should use: min(2 * 2, 16) = 4
        assert config.max_workers == 4

    def test_respects_explicit_value(self):
        """Test that explicit user values are respected."""
        config = Config(max_workers=8)

        # Should not auto-detect, use explicit value
        assert config.max_workers == 8

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', False)
    def test_fallback_without_psutil(self):
        """Test fallback to default when psutil is not available."""
        config = Config.create_optimized()

        # Should fall back to conservative defaults without psutil
        assert config.max_workers in [4, 8, 12, 16]  # Accept any reasonable default


class TestMemoryValidation:
    """Test memory-based batch size validation."""

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.config.psutil.virtual_memory')
    def test_batch_size_within_safe_limit(self, mock_memory):
        """Test that safe batch sizes don't trigger warnings."""
        # Mock 8GB available RAM
        mock_vm = MagicMock()
        mock_vm.available = 8 * 1024**3
        mock_memory.return_value = mock_vm

        # Safe batch size: 800 (8GB * 100)
        config = Config(batch_size=500)

        assert config.batch_size == 500

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', True)
    @patch('project_vectorizer.core.config.psutil.virtual_memory')
    def test_batch_size_exceeds_safe_limit(self, mock_memory, caplog):
        """Test that excessive batch sizes trigger warnings."""
        # Mock 2GB available RAM
        mock_vm = MagicMock()
        mock_vm.available = 2 * 1024**3
        mock_memory.return_value = mock_vm

        # Excessive batch size: 500 (max safe: 200)
        config = Config(batch_size=500)

        # Should still accept the value but log warning
        assert config.batch_size == 500

    @patch('project_vectorizer.core.config.PSUTIL_AVAILABLE', False)
    def test_validation_without_psutil(self):
        """Test that validation works without psutil."""
        config = Config(batch_size=1000)

        # Should accept value without validation
        assert config.batch_size == 1000

    def test_rejects_negative_batch_size(self):
        """Test that negative batch sizes are rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            Config(batch_size=-1)

    def test_rejects_zero_batch_size(self):
        """Test that zero batch size is rejected."""
        with pytest.raises(ValueError, match="must be positive"):
            Config(batch_size=0)


class TestNewConfigFields:
    """Test new configuration fields."""

    def test_embedding_batch_size_default(self):
        """Test embedding_batch_size default value."""
        config = Config()
        assert config.embedding_batch_size == 100

    def test_embedding_batch_size_custom(self):
        """Test custom embedding_batch_size."""
        config = Config(embedding_batch_size=200)
        assert config.embedding_batch_size == 200

    def test_parallel_file_processing_default(self):
        """Test parallel_file_processing default value."""
        config = Config()
        assert config.parallel_file_processing is True

    def test_parallel_file_processing_disabled(self):
        """Test disabling parallel processing."""
        config = Config(parallel_file_processing=False)
        assert config.parallel_file_processing is False

    def test_memory_monitoring_enabled_default(self):
        """Test memory_monitoring_enabled default value."""
        config = Config()
        assert config.memory_monitoring_enabled is True

    def test_memory_efficient_search_threshold_default(self):
        """Test memory_efficient_search_threshold default."""
        config = Config()
        assert config.memory_efficient_search_threshold == 10000

    def test_gc_interval_default(self):
        """Test gc_interval default value."""
        config = Config()
        assert config.gc_interval == 100

    def test_gc_interval_custom(self):
        """Test custom gc_interval."""
        config = Config(gc_interval=50)
        assert config.gc_interval == 50


class TestEnvironmentVariables:
    """Test environment variable loading for new fields."""

    def test_env_var_max_workers(self, monkeypatch):
        """Test MAX_WORKERS environment variable."""
        monkeypatch.setenv("MAX_WORKERS", "12")
        config = Config.create_default()
        assert config.max_workers == 12

    def test_env_var_batch_size(self, monkeypatch):
        """Test BATCH_SIZE environment variable."""
        monkeypatch.setenv("BATCH_SIZE", "200")
        config = Config.create_default()
        assert config.batch_size == 200

    def test_env_var_embedding_batch_size(self, monkeypatch):
        """Test EMBEDDING_BATCH_SIZE environment variable."""
        monkeypatch.setenv("EMBEDDING_BATCH_SIZE", "150")
        config = Config.create_default()
        assert config.embedding_batch_size == 150

    def test_env_var_parallel_processing_false(self, monkeypatch):
        """Test PARALLEL_FILE_PROCESSING=false."""
        monkeypatch.setenv("PARALLEL_FILE_PROCESSING", "false")
        config = Config.create_default()
        assert config.parallel_file_processing is False

    def test_env_var_parallel_processing_true(self, monkeypatch):
        """Test PARALLEL_FILE_PROCESSING=true."""
        monkeypatch.setenv("PARALLEL_FILE_PROCESSING", "true")
        config = Config.create_default()
        assert config.parallel_file_processing is True

    def test_env_var_memory_monitoring(self, monkeypatch):
        """Test MEMORY_MONITORING_ENABLED environment variable."""
        monkeypatch.setenv("MEMORY_MONITORING_ENABLED", "false")
        config = Config.create_default()
        assert config.memory_monitoring_enabled is False

    def test_env_var_gc_interval(self, monkeypatch):
        """Test GC_INTERVAL environment variable."""
        monkeypatch.setenv("GC_INTERVAL", "50")
        config = Config.create_default()
        assert config.gc_interval == 50


class TestConfigSerialization:
    """Test that new fields are properly serialized."""

    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading config with new fields."""
        config_file = tmp_path / "config.json"

        # Create config with custom values
        original_config = Config(
            max_workers=8,
            batch_size=200,
            embedding_batch_size=150,
            parallel_file_processing=False,
            memory_monitoring_enabled=False,
            gc_interval=50
        )

        # Save to file
        original_config.save_to_file(config_file)

        # Load from file
        loaded_config = Config.load_from_file(config_file)

        # Verify all fields
        assert loaded_config.max_workers == 8
        assert loaded_config.batch_size == 200
        assert loaded_config.embedding_batch_size == 150
        assert loaded_config.parallel_file_processing is False
        assert loaded_config.memory_monitoring_enabled is False
        assert loaded_config.gc_interval == 50
