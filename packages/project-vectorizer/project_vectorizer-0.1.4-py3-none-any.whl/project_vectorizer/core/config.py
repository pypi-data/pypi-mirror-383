"""Configuration management for project vectorizer."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Try to import psutil for memory/CPU detection
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class Config(BaseModel):
    # Database configuration (ChromaDB only)
    chromadb_path: Optional[str] = Field(default=None)  # Path to ChromaDB storage

    # Embedding configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    embedding_provider: str = Field(default="sentence-transformers")
    openai_api_key: Optional[str] = Field(default=None)

    # Chunking configuration
    chunk_size: int = Field(default=256)
    chunk_overlap: int = Field(default=32)
    max_file_size_mb: int = Field(default=10)

    # File filtering
    included_extensions: List[str] = Field(default=[
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c",
        ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".kt", ".scala", ".clj",
        ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
        ".md", ".txt", ".rst", ".asciidoc", ".org",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
        ".xml", ".html", ".htm", ".css", ".scss", ".sass", ".less",
        ".sql", ".graphql", ".proto", ".dockerfile", ".makefile",
        ".gitignore", ".env", ".editorconfig"
    ])

    excluded_patterns: List[str] = Field(default=[
        "node_modules/**",
        ".git/**",
        ".svn/**",
        ".hg/**",
        "__pycache__/**",
        "*.pyc",
        ".pytest_cache/**",
        ".coverage",
        "htmlcov/**",
        ".tox/**",
        ".nox/**",
        "venv/**",
        "env/**",
        ".env/**",
        ".venv/**",
        ".vectorizer/**",
        "build/**",
        "dist/**",
        "*.egg-info/**",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "*.tmp",
        "*.temp",
        ".idea/**",
        ".vscode/**",
        "*.min.js",
        "*.min.css"
    ])

    # Server configuration
    mcp_host: str = Field(default="localhost")
    mcp_port: int = Field(default=8000)

    # Logging configuration
    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default=None)

    # Performance configuration
    max_workers: int = Field(default=4)
    batch_size: int = Field(default=100)
    embedding_batch_size: int = Field(default=100)  # NEW: Separate batch size for embeddings
    parallel_file_processing: bool = Field(default=True)  # NEW: Enable/disable parallel processing

    # Memory management configuration
    memory_monitoring_enabled: bool = Field(default=True)  # NEW: Enable memory monitoring
    memory_efficient_search_threshold: int = Field(default=10000)  # NEW: Switch to efficient search above this
    gc_interval: int = Field(default=100)  # NEW: Garbage collection interval (files)
    
    @field_validator('chunk_size', 'chunk_overlap', 'max_file_size_mb', 'mcp_port', 'embedding_batch_size', 'memory_efficient_search_threshold', 'gc_interval')
    @classmethod
    def validate_positive_integers(cls, v):
        """Validate that integer fields are positive."""
        if v <= 0:
            raise ValueError(f"Value must be positive, got {v}")
        return v

    @field_validator('max_workers')
    @classmethod
    def optimize_max_workers(cls, v: int) -> int:
        """
        Auto-detect optimal worker count based on CPU cores.

        If using default value (4), auto-detect based on system CPU count.
        Formula: min(cpu_count * 2, 16) - Use 2x CPU cores, max 16 workers

        Returns:
            Optimized worker count
        """
        # If not using default, respect user's choice
        if v != 4:
            return v

        # Try to auto-detect CPU count
        if PSUTIL_AVAILABLE:
            try:
                cpu_count = psutil.cpu_count(logical=True) or 4
                # Use 2x CPU cores for I/O bound tasks, cap at 16
                optimal = min(cpu_count * 2, 16)
                if optimal != v:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Auto-detected optimal max_workers: {optimal} (based on {cpu_count} CPU cores)")
                return optimal
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not auto-detect CPU count: {e}, using default")

        # Fallback to default
        return v

    @field_validator('batch_size')
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """
        Validate batch size against available memory.

        Rule of thumb: 1GB RAM per 100 chunks
        Warns if batch_size may exceed available RAM

        Returns:
            Validated batch_size
        """
        if v <= 0:
            raise ValueError(f"batch_size must be positive, got {v}")

        if PSUTIL_AVAILABLE:
            try:
                # Get available RAM in GB
                available_ram_gb = psutil.virtual_memory().available / (1024**3)

                # Calculate safe maximum (1GB per 100 chunks)
                max_safe_batch = int(available_ram_gb * 100)

                if v > max_safe_batch:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"batch_size {v} may exceed available RAM ({available_ram_gb:.1f}GB). "
                        f"Recommended max: {max_safe_batch}"
                    )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Could not validate batch size against memory: {e}")

        return v
    
    @classmethod
    def _get_env_value(cls, key: str, default: str = None, type_func: callable = str) -> any:
        """Get environment variable value with proper type conversion."""
        value = os.getenv(key, default)
        if value is None:
            return None
        try:
            return type_func(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for {key}: {value}") from e
    
    @classmethod
    def _get_env_list(cls, key: str, default: List[str] = None) -> List[str]:
        """Get environment variable as a list."""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(",") if item.strip()]
        return default or []
    
    @classmethod
    def create_default(cls) -> "Config":
        """Create default configuration with environment variable support."""
        # Try to load .env file from current directory
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

        # Create config with environment variable overrides
        return cls(
            chromadb_path=cls._get_env_value("CHROMADB_PATH"),
            embedding_model=cls._get_env_value("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            embedding_provider=cls._get_env_value("EMBEDDING_PROVIDER", "sentence-transformers"),
            openai_api_key=cls._get_env_value("OPENAI_API_KEY"),
            chunk_size=cls._get_env_value("CHUNK_SIZE", "256", int),
            chunk_overlap=cls._get_env_value("CHUNK_OVERLAP", "32", int),
            max_file_size_mb=cls._get_env_value("MAX_FILE_SIZE_MB", "10", int),
            included_extensions=cls._get_env_list("INCLUDED_EXTENSIONS", [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c",
                ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".kt", ".scala", ".clj",
                ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
                ".md", ".txt", ".rst", ".asciidoc", ".org",
                ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
                ".xml", ".html", ".htm", ".css", ".scss", ".sass", ".less",
                ".sql", ".graphql", ".proto", ".dockerfile", ".makefile",
                ".gitignore", ".env", ".editorconfig"
            ]),
            excluded_patterns=cls._get_env_list("EXCLUDED_PATTERNS", [
                "node_modules/**", ".git/**", ".svn/**", ".hg/**", "__pycache__/**",
                "*.pyc", ".pytest_cache/**", ".coverage", "htmlcov/**", ".tox/**",
                ".nox/**", "venv/**", "env/**", ".env/**", ".venv/**", ".vectorizer/**",
                "build/**", "dist/**", "*.egg-info/**", ".DS_Store", "Thumbs.db",
                "*.log", "*.tmp", "*.temp", ".idea/**", ".vscode/**", "*.min.js", "*.min.css"
            ]),
            mcp_host=cls._get_env_value("MCP_HOST", "localhost"),
            mcp_port=cls._get_env_value("MCP_PORT", "8000", int),
            log_level=cls._get_env_value("LOG_LEVEL", "INFO"),
            log_file=cls._get_env_value("LOG_FILE"),
            max_workers=cls._get_env_value("MAX_WORKERS", "4", int),
            batch_size=cls._get_env_value("BATCH_SIZE", "100", int),
            embedding_batch_size=cls._get_env_value("EMBEDDING_BATCH_SIZE", "100", int),
            parallel_file_processing=cls._get_env_value("PARALLEL_FILE_PROCESSING", "true", lambda x: x.lower() == "true"),
            memory_monitoring_enabled=cls._get_env_value("MEMORY_MONITORING_ENABLED", "true", lambda x: x.lower() == "true"),
            memory_efficient_search_threshold=cls._get_env_value("MEMORY_EFFICIENT_SEARCH_THRESHOLD", "10000", int),
            gc_interval=cls._get_env_value("GC_INTERVAL", "100", int)
        )
    
    @classmethod
    def create_optimized(cls, **overrides) -> "Config":
        """
        Create an optimized configuration based on system resources.

        This method intelligently detects:
        - CPU cores for optimal max_workers
        - Available RAM for safe batch_size
        - Memory thresholds for efficient processing

        Args:
            **overrides: Any config parameters to override the optimized defaults

        Returns:
            Config instance with optimized settings

        Example:
            # Create with full optimization
            config = Config.create_optimized()

            # Create with custom embedding model but optimized workers/memory
            config = Config.create_optimized(
                embedding_model="text-embedding-ada-002",
                embedding_provider="openai"
            )
        """
        import logging
        logger = logging.getLogger(__name__)

        # Start with default config
        optimized_params = {}

        if PSUTIL_AVAILABLE:
            try:
                # Detect optimal max_workers based on CPU
                cpu_count = psutil.cpu_count(logical=True) or 4
                optimal_workers = min(cpu_count * 2, 16)
                optimized_params['max_workers'] = optimal_workers
                logger.info(f"Detected {cpu_count} CPU cores, setting max_workers={optimal_workers}")

                # Detect available RAM and optimize batch sizes
                memory = psutil.virtual_memory()
                available_ram_gb = memory.available / (1024**3)
                total_ram_gb = memory.total / (1024**3)

                # Calculate safe batch sizes (1GB RAM per 100 chunks)
                # Use 50% of available RAM for batch processing to leave room for other operations
                safe_batch_multiplier = int(available_ram_gb * 0.5)
                optimal_batch_size = max(50, min(safe_batch_multiplier * 100, 500))
                optimal_embedding_batch = max(50, min(safe_batch_multiplier * 50, 250))

                optimized_params['batch_size'] = optimal_batch_size
                optimized_params['embedding_batch_size'] = optimal_embedding_batch
                logger.info(
                    f"Detected {total_ram_gb:.1f}GB total RAM ({available_ram_gb:.1f}GB available), "
                    f"setting batch_size={optimal_batch_size}, embedding_batch_size={optimal_embedding_batch}"
                )

                # Adjust memory-efficient search threshold based on RAM
                # More RAM = higher threshold before switching to memory-efficient mode
                if total_ram_gb >= 32:
                    threshold = 50000  # High-end systems can handle larger collections
                elif total_ram_gb >= 16:
                    threshold = 20000  # Mid-range systems
                elif total_ram_gb >= 8:
                    threshold = 10000  # Standard systems
                else:
                    threshold = 5000   # Low-memory systems

                optimized_params['memory_efficient_search_threshold'] = threshold
                logger.info(f"Setting memory_efficient_search_threshold={threshold} based on {total_ram_gb:.1f}GB RAM")

                # Adjust GC interval based on available memory
                # Less memory = more frequent GC
                if available_ram_gb < 4:
                    gc_interval = 25   # Very aggressive GC for low memory
                elif available_ram_gb < 8:
                    gc_interval = 50   # Aggressive GC
                elif available_ram_gb < 16:
                    gc_interval = 100  # Standard GC
                else:
                    gc_interval = 200  # Relaxed GC for high memory systems

                optimized_params['gc_interval'] = gc_interval
                logger.info(f"Setting gc_interval={gc_interval} based on {available_ram_gb:.1f}GB available RAM")

                # Always enable memory monitoring on systems with <16GB RAM
                if total_ram_gb < 16:
                    optimized_params['memory_monitoring_enabled'] = True
                    logger.info("Enabling memory monitoring for system with <16GB RAM")

            except Exception as e:
                logger.warning(f"Could not detect system resources for optimization: {e}")
                logger.info("Falling back to conservative defaults")
        else:
            logger.warning("psutil not available - using conservative defaults")
            logger.info("Install psutil for automatic resource optimization: pip install psutil")

        # Apply any user overrides
        optimized_params.update(overrides)

        # Create config with optimized parameters
        return cls(**optimized_params)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "Config":
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)

            return cls(**data)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid configuration file format: {e}") from e
    
    @classmethod
    def load_from_project(cls, project_path: Path) -> "Config":
        """Load configuration from project directory with environment variable support."""
        # Load .env files (priority: project .env > global .env)
        project_env = project_path / ".env"
        global_env = Path(".env")

        # Load environment variables from .env files
        if project_env.exists():
            load_dotenv(project_env)
        elif global_env.exists():
            load_dotenv(global_env)

        # Check for config file first
        config_file = project_path / ".vectorizer" / "config.json"
        if config_file.exists():
            try:
                return cls.load_from_file(config_file)
            except ValueError:
                # Config file is corrupted, fall back to defaults
                pass

        # Create config with environment variable overrides
        return cls(
            chromadb_path=cls._get_env_value("CHROMADB_PATH"),
            embedding_model=cls._get_env_value("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            embedding_provider=cls._get_env_value("EMBEDDING_PROVIDER", "sentence-transformers"),
            openai_api_key=cls._get_env_value("OPENAI_API_KEY"),
            chunk_size=cls._get_env_value("CHUNK_SIZE", "256", int),
            chunk_overlap=cls._get_env_value("CHUNK_OVERLAP", "32", int),
            max_file_size_mb=cls._get_env_value("MAX_FILE_SIZE_MB", "10", int),
            included_extensions=cls._get_env_list("INCLUDED_EXTENSIONS", [
                ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".cpp", ".c",
                ".h", ".hpp", ".cs", ".php", ".rb", ".swift", ".kt", ".scala", ".clj",
                ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
                ".md", ".txt", ".rst", ".asciidoc", ".org",
                ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
                ".xml", ".html", ".htm", ".css", ".scss", ".sass", ".less",
                ".sql", ".graphql", ".proto", ".dockerfile", ".makefile",
                ".gitignore", ".env", ".editorconfig"
            ]),
            excluded_patterns=cls._get_env_list("EXCLUDED_PATTERNS", [
                "node_modules/**", ".git/**", ".svn/**", ".hg/**", "__pycache__/**",
                "*.pyc", ".pytest_cache/**", ".coverage", "htmlcov/**", ".tox/**",
                ".nox/**", "venv/**", "env/**", ".env/**", ".venv/**", ".vectorizer/**",
                "build/**", "dist/**", "*.egg-info/**", ".DS_Store", "Thumbs.db",
                "*.log", "*.tmp", "*.temp", ".idea/**", ".vscode/**", "*.min.js", "*.min.css"
            ]),
            mcp_host=cls._get_env_value("MCP_HOST", "localhost"),
            mcp_port=cls._get_env_value("MCP_PORT", "8000", int),
            log_level=cls._get_env_value("LOG_LEVEL", "INFO"),
            log_file=cls._get_env_value("LOG_FILE"),
            max_workers=cls._get_env_value("MAX_WORKERS", "4", int),
            batch_size=cls._get_env_value("BATCH_SIZE", "100", int),
            embedding_batch_size=cls._get_env_value("EMBEDDING_BATCH_SIZE", "100", int),
            parallel_file_processing=cls._get_env_value("PARALLEL_FILE_PROCESSING", "true", lambda x: x.lower() == "true"),
            memory_monitoring_enabled=cls._get_env_value("MEMORY_MONITORING_ENABLED", "true", lambda x: x.lower() == "true"),
            memory_efficient_search_threshold=cls._get_env_value("MEMORY_EFFICIENT_SEARCH_THRESHOLD", "10000", int),
            gc_interval=cls._get_env_value("GC_INTERVAL", "100", int)
        )
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.model_dump(), f, indent=2)
    
    def save_to_project(self, project_path: Path) -> None:
        """Save configuration to project directory."""
        config_dir = project_path / ".vectorizer"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.json"
        self.save_to_file(config_file)
    
    def get_chromadb_path(self, project_path: Path) -> str:
        """Get the resolved ChromaDB path for the project."""
        if self.chromadb_path:
            return self.chromadb_path

        # Default to project/.vectorizer/chromadb
        if isinstance(project_path, str):
            project_path = Path(project_path)
        return str(project_path / ".vectorizer" / "chromadb")
    
    def should_include_file(self, file_path: Path) -> bool:
        if file_path.suffix not in self.included_extensions:
            return False
        
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                return False
        except (OSError, IOError):
            return False
        
        file_str = str(file_path)
        for pattern in self.excluded_patterns:
            if self._match_pattern(file_str, pattern):
                return False
        
        return True
    
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        import fnmatch
        
        if pattern.endswith("/**"):
            dir_pattern = pattern[:-3]
            return dir_pattern in file_path
        
        return fnmatch.fnmatch(file_path, pattern)
