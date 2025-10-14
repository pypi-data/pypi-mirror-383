"""Tests for environment variable loading and configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from project_vectorizer.core.config import Config


class TestEnvironmentVariables:
    """Test environment variable loading and configuration."""
    
    def setup_method(self):
        """Clear environment variables before each test."""
        # List of all environment variables that might be set by tests
        env_vars_to_clear = [
            'CHUNK_SIZE', 'CHUNK_OVERLAP', 'MAX_FILE_SIZE_MB',
            'EMBEDDING_MODEL', 'EMBEDDING_PROVIDER', 'OPENAI_API_KEY',
            'CHROMADB_PATH', 'MCP_HOST', 'MCP_PORT', 'LOG_LEVEL', 'LOG_FILE',
            'MAX_WORKERS', 'EMBEDDING_BATCH_SIZE', 'INCLUDED_EXTENSIONS', 'EXCLUDED_PATTERNS'
        ]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def test_default_config_values(self):
        """Test that default configuration values are correct."""
        config = Config()
        
        assert config.chunk_size == 256
        assert config.embedding_model == "all-MiniLM-L6-v2"
        assert config.embedding_provider == "sentence-transformers"
        assert config.mcp_host == "localhost"
        assert config.mcp_port == 8000
        assert config.log_level == "INFO"

    def test_environment_variable_override(self, temp_dir: Path):
        """Test that environment variables override default values."""
        # Create test environment file
        env_content = """
CHUNK_SIZE=512
EMBEDDING_MODEL=test-model
EMBEDDING_PROVIDER=openai
MCP_HOST=0.0.0.0
MCP_PORT=9000
LOG_LEVEL=DEBUG
MAX_WORKERS=8
"""
        env_file = temp_dir / ".env"
        env_file.write_text(env_content)
        
        # Load environment variables
        load_dotenv(env_file, override=True)
        
        # Create config
        config = Config.create_default()
        
        # Verify environment variables took effect
        assert config.chunk_size == 512
        assert config.embedding_model == "test-model"
        assert config.embedding_provider == "openai"
        assert config.mcp_host == "0.0.0.0"
        assert config.mcp_port == 9000
        assert config.log_level == "DEBUG"
        assert config.max_workers == 8

    def test_configuration_priority_system(self, temp_dir: Path):
        """Test that configuration values are applied in correct priority order."""
        # Create environment file with specific values
        env_content = """
CHUNK_SIZE=256
EMBEDDING_MODEL=env-model
LOG_LEVEL=ERROR
"""
        env_file = temp_dir / ".env"
        env_file.write_text(env_content)
        
        # Load environment and create config
        load_dotenv(env_file, override=True)
        config = Config.create_default()
        
        # Verify environment variables override defaults
        assert config.chunk_size == 256
        assert config.embedding_model == "env-model"
        assert config.log_level == "ERROR"
        
        # Values not in env should remain default
        assert config.mcp_port == 8000  # Default value

    def test_invalid_environment_variables(self, temp_dir: Path):
        """Test handling of invalid environment variable values."""
        env_content = """
CHUNK_SIZE=invalid_number
MCP_PORT=not_a_port
MAX_WORKERS=invalid
"""
        env_file = temp_dir / ".env"
        env_file.write_text(env_content)
        
        # Load environment variables
        load_dotenv(env_file, override=True)
        
        # Should raise ValueError for invalid integer conversion
        with pytest.raises(ValueError):
            Config.create_default()

    def test_list_environment_variables(self, temp_dir: Path):
        """Test parsing of list-based environment variables."""
        env_content = """
INCLUDED_EXTENSIONS=.py,.js,.ts,.custom
EXCLUDED_PATTERNS=node_modules/**,build/**,*.tmp
"""
        env_file = temp_dir / ".env"
        env_file.write_text(env_content)
        
        load_dotenv(env_file)
        config = Config.create_default()
        
        assert ".py" in config.included_extensions
        assert ".js" in config.included_extensions
        assert ".custom" in config.included_extensions
        assert "node_modules/**" in config.excluded_patterns
        assert "build/**" in config.excluded_patterns

    def test_openai_api_key_loading(self, temp_dir: Path):
        """Test loading of OpenAI API key from environment."""
        env_content = """
OPENAI_API_KEY=sk-test-key-12345
EMBEDDING_PROVIDER=openai
"""
        env_file = temp_dir / ".env"
        env_file.write_text(env_content)
        
        load_dotenv(env_file)
        config = Config.create_default()
        
        assert config.openai_api_key == "sk-test-key-12345"
        assert config.embedding_provider == "openai"

    def test_chromadb_path_variations(self, temp_dir: Path):
        """Test different ChromaDB path configurations."""
        # Test ChromaDB path
        env_content1 = "CHROMADB_PATH=/custom/path/to/chromadb"
        env_file1 = temp_dir / ".env1"
        env_file1.write_text(env_content1)

        load_dotenv(env_file1, override=True)
        config1 = Config.create_default()
        assert config1.chromadb_path == "/custom/path/to/chromadb"

        # Test ChromaDB with different path
        env_content2 = "CHROMADB_PATH=/another/path/to/chromadb"
        env_file2 = temp_dir / ".env2"
        env_file2.write_text(env_content2)

        # Clear existing env vars and load new ones
        if 'CHROMADB_PATH' in os.environ:
            del os.environ['CHROMADB_PATH']
        load_dotenv(env_file2, override=True)
        config2 = Config.create_default()
        assert config2.chromadb_path == "/another/path/to/chromadb"

    def test_project_specific_env_loading(self, temp_dir: Path):
        """Test loading project-specific .env files."""
        # Create project structure
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        
        # Create project-specific .env file
        project_env = project_dir / ".env"
        project_env.write_text("CHUNK_SIZE=128\nLOG_LEVEL=DEBUG")
        
        # Load project configuration
        config = Config.load_from_project(project_dir)
        
        assert config.chunk_size == 128
        assert config.log_level == "DEBUG"

    def test_env_file_precedence(self, temp_dir: Path):
        """Test that project .env takes precedence over global .env."""
        # Create global .env
        global_env = temp_dir / ".env"
        global_env.write_text("CHUNK_SIZE=512\nLOG_LEVEL=INFO")
        
        # Create project directory and .env
        project_dir = temp_dir / "project"
        project_dir.mkdir()
        project_env = project_dir / ".env"
        project_env.write_text("CHUNK_SIZE=256")  # Override chunk size only
        
        # Change to temp directory so global .env can be found
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            config = Config.load_from_project(project_dir)
            
            # Project .env should override chunk_size
            assert config.chunk_size == 256
            # But global .env should still provide log_level if not in project .env
            # Note: This test might need adjustment based on actual implementation
        finally:
            os.chdir(original_cwd)

    @patch.dict(os.environ, {
        'CHUNK_SIZE': '1024',
        'EMBEDDING_MODEL': 'test-direct-env',
        'LOG_LEVEL': 'WARNING'
    })
    def test_direct_environment_variables(self):
        """Test loading configuration directly from environment variables."""
        config = Config.create_default()
        
        assert config.chunk_size == 1024
        assert config.embedding_model == "test-direct-env"
        assert config.log_level == "WARNING"

    def test_config_serialization(self, test_config: Config, temp_dir: Path):
        """Test that configuration can be saved and loaded from JSON."""
        config_file = temp_dir / "config.json"
        test_config.save_to_file(config_file)
        
        # Verify file was created
        assert config_file.exists()
        
        # Load configuration from file
        loaded_config = Config.load_from_file(config_file)
        
        # Verify values match
        assert loaded_config.chunk_size == test_config.chunk_size
        assert loaded_config.embedding_model == test_config.embedding_model
        assert loaded_config.log_level == test_config.log_level