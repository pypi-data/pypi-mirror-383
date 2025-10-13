# Environment Variables

This document describes all available environment variables for Project Vectorizer.

## Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your preferred settings
3. The application will automatically load these variables

## Variable Categories

### Embedding Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Required for OpenAI embeddings. Get from [OpenAI Platform](https://platform.openai.com/api-keys) |
| `EMBEDDING_PROVIDER` | `sentence-transformers` | Provider: `sentence-transformers` or `openai` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Model to use for embeddings |

#### Recommended Models

**Sentence Transformers (Free, Local):**
- `all-MiniLM-L6-v2` - Fast, good quality (384 dimensions)
- `all-mpnet-base-v2` - Higher quality, slower (768 dimensions)
- `all-distilroberta-v1` - Good balance (768 dimensions)

**OpenAI (Paid API):**
- `text-embedding-3-small` - Latest, efficient
- `text-embedding-3-large` - Highest quality
- `text-embedding-ada-002` - Legacy but reliable

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMADB_PATH` | `{project}/.vectorizer/chromadb` | Path to ChromaDB storage directory |

#### Database Examples

```bash
# Default (stored in project directory)
# CHROMADB_PATH=

# Custom path
CHROMADB_PATH=/custom/path/to/chromadb
```

### Chunking Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `256` | Token size for chunks (128-256 recommended for single-word search) |
| `CHUNK_OVERLAP` | `32` | Overlap between chunks in tokens |
| `MAX_FILE_SIZE_MB` | `10` | Maximum file size to process |

#### Chunk Size Guidelines

- **128-256 tokens**: Best for single-word and precise searches ✅
- **256-512 tokens**: Good balance for most use cases
- **512-1024 tokens**: Better for context understanding
- **1024+ tokens**: Comprehensive semantic search

### Search Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_SEARCH_THRESHOLD` | `0.3` | Default similarity threshold (0.0-1.0) |
| `DEFAULT_SEARCH_LIMIT` | `10` | Default number of results |
| `ENABLE_SINGLE_WORD_OPTIMIZATION` | `true` | Enable enhanced single-word search |

#### Threshold Guidelines

- **Single words**: 0.7-0.9 (works excellently)
- **Multi-word phrases**: 0.3-0.7
- **Complex queries**: 0.1-0.5

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `localhost` | MCP server host |
| `MCP_PORT` | `8000` | MCP server port |
| `ENABLE_HTTP_FALLBACK` | `true` | Enable HTTP API fallback |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8080` | Allowed CORS origins |

### File Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `INCLUDED_EXTENSIONS` | `.py,.js,.ts,...` | File extensions to include |
| `EXCLUDED_PATTERNS` | `node_modules/**,...` | Patterns to exclude |

### Performance

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_BATCH_SIZE` | `10` | Concurrent embedding generations |
| `ENABLE_PARALLEL_PROCESSING` | `true` | Enable parallel file processing |
| `MAX_WORKERS` | `4` | Maximum worker threads |

### Development

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `VERBOSE_LOGGING` | `false` | Enable verbose logging |
| `DEVELOPMENT_MODE` | `false` | Enable development mode |
| `ENABLE_PROFILING` | `false` | Enable performance profiling |

## Usage Examples

### Basic Setup with Sentence Transformers
```bash
EMBEDDING_PROVIDER=sentence-transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=256
DEFAULT_SEARCH_THRESHOLD=0.3
```

### OpenAI Setup
```bash
OPENAI_API_KEY=sk-your-key-here
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=256
DEFAULT_SEARCH_THRESHOLD=0.5
```

### High-Performance Setup
```bash
EMBEDDING_BATCH_SIZE=20
MAX_WORKERS=8
ENABLE_PARALLEL_PROCESSING=true
```

### Development Setup
```bash
LOG_LEVEL=DEBUG
VERBOSE_LOGGING=true
DEVELOPMENT_MODE=true
ENABLE_PROFILING=true
```

## Validation

The application validates environment variables on startup and will show warnings for:
- Invalid values
- Missing required variables (when using certain providers)
- Conflicting configurations

## Override Priority

Configuration values are applied in this order (highest priority first):
1. Command-line arguments
2. Environment variables
3. Project configuration file
4. Default values