"""Configuration management for project vectorizer."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv


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
    
    @field_validator('chunk_size', 'chunk_overlap', 'max_file_size_mb', 'mcp_port', 'max_workers', 'batch_size')
    @classmethod
    def validate_positive_integers(cls, v):
        """Validate that integer fields are positive."""
        if v <= 0:
            raise ValueError(f"Value must be positive, got {v}")
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
            batch_size=cls._get_env_value("EMBEDDING_BATCH_SIZE", "100", int)
        )
    
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
            batch_size=cls._get_env_value("EMBEDDING_BATCH_SIZE", "100", int)
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
