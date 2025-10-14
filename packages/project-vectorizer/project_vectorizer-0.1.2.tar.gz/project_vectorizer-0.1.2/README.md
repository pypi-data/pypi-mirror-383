# Project Vectorizer

A powerful CLI tool that vectorizes codebases, stores them in a vector database, tracks changes, and serves them via MCP (Model Context Protocol) for AI agents like Claude, Codex, and others.

**Latest Version**: 0.1.2 | [Changelog](#changelog) | [GitHub](https://github.com/starkbaknet/project-vectorizer)

---

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Performance Optimization](#performance-optimization)
- [CLI Commands](#cli-commands)
- [Configuration](#configuration)
- [Search Features](#search-features)
- [MCP Server](#mcp-server)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [Contributing](#contributing)

---

## Features

### 🚀 Performance & Optimization

- **Auto-Optimized Config** - Auto-detect CPU cores and RAM for optimal settings (`--optimize`)
- **Max Resources Mode** - Use maximum system resources for fastest indexing (`--max-resources`)
- **Smart Incremental** - 60-70% faster indexing with intelligent change categorization
- **Git-Aware Indexing** - 80-90% faster by indexing only git-changed files
- **Parallel Processing** - Multi-threaded with auto-detected optimal worker count (up to 16 workers)
- **Memory Monitoring** - Real-time memory tracking with automatic garbage collection
- **Batch Optimization** - Memory-based batch size calculation for safe processing

### 🔍 Search & Indexing

- **Code Vectorization** - Parse and vectorize with sentence-transformers or OpenAI embeddings
- **Multi-Level Chunking** - Functions, classes, micro-chunks, and word-level chunks for precision
- **Enhanced Single-Word Search** - High-precision search for single keywords (0.8+ thresholds)
- **Semantic + Exact Search** - Combines semantic similarity with exact word matching
- **Adaptive Thresholds** - Automatically adjusts for optimal results
- **Multiple Languages** - 30+ languages (Python, JS, TS, Go, Rust, Java, C++, C, PHP, Ruby, Swift, Kotlin, and more)

### 🔄 Change Management

- **Git Integration** - Track changes via git commits with `index-git` command
- **Smart File Categorization** - Detects New, Modified, and Deleted files
- **Watch Mode** - Real-time monitoring with configurable debouncing (0.5-10s)
- **Incremental Updates** - Only re-index changed content
- **Hash-Based Detection** - SHA256 file hashing for accurate change detection

### 🌐 AI Integration

- **MCP Server** - Model Context Protocol for AI agents (Claude, Codex, etc.)
- **HTTP Fallback API** - RESTful endpoints when MCP unavailable
- **Semantic Search** - Natural language queries for code discovery
- **File Operations** - Get content, list files, project statistics

### 🎨 User Experience

- **Clean Progress Output** - Single unified progress bar with timing information
- **Suppressed Library Logs** - No cluttered batch progress bars from dependencies
- **Timing Information** - Elapsed time for all operations (seconds or minutes+seconds)
- **Verbose Mode** - Optional detailed logging for debugging
- **Professional UI** - Rich terminal output with colors, panels, and formatting
- **Real-time Updates** - Live file names and status tags during indexing

### 💾 Database & Storage

- **ChromaDB Backend** - High-performance vector database
- **Fast HNSW Indexing** - Optimized similarity search algorithm
- **Scalable** - Handles 500K+ chunks efficiently
- **Single Database** - No external dependencies required
- **Custom Paths** - Configurable database location

---

## Installation

### From PyPI (Recommended)

```bash
# Install from PyPI
pip install project-vectorizer

# Verify installation
pv --version
```

### From Source

```bash
# Clone repository
git clone https://github.com/starkbaknet/project-vectorizer.git
cd project-vectorizer

# Install
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Initialize Your Project

```bash
# 🚀 Recommended: Auto-optimize based on your system (16 workers, 400 batch on 8-core/16GB RAM)
pv init /path/to/project --optimize

# Or with custom settings
pv init /path/to/project \
  --name "My Project" \
  --embedding-model "all-MiniLM-L6-v2" \
  --chunk-size 256 \
  --optimize
```

**Output:**

```
✓ Project initialized successfully!

Name: My Project
Path: /path/to/project
Model: all-MiniLM-L6-v2
Provider: sentence-transformers
Chunk Size: 256 tokens

Optimized Settings:
  • Workers: 16
  • Batch Size: 400
  • Embedding Batch: 200
  • Memory Monitoring: Enabled
  • GC Interval: 100 files
```

### 2. Index Your Codebase

```bash
# 🚀 Recommended: First-time indexing with max resources (2-4x faster)
pv index /path/to/project --max-resources

# 🚀 Recommended: Smart incremental for updates (60-70% faster)
pv index /path/to/project --smart

# 🚀 Recommended: Git-aware for recent changes (80-90% faster)
pv index-git /path/to/project --since HEAD~5

# Standard full indexing
pv index /path/to/project

# Force re-index everything
pv index /path/to/project --force

# Combine for maximum performance
pv index /path/to/project --smart --max-resources
```

**Output:**

```
Using maximum system resources (optimized settings)...
  • Workers: 16
  • Batch Size: 400
  • Embedding Batch: 200

  Indexing examples/demo.py ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

╭────────────────── Indexing Complete ──────────────────╮
│ ✓ Indexing complete!                                  │
│                                                       │
│ Files indexed: 48/49                                  │
│ Total chunks: 9222                                    │
│ Model: all-MiniLM-L6-v2                               │
│ Time taken: 2m 16s                                    │
│                                                       │
│ You can now search with: pv search . "your query"     │
╰───────────────────────────────────────────────────────╯
```

### 3. Search Your Code

```bash
# Natural language search
pv search /path/to/project "authentication logic"

# Single-word searches work great (high precision)
pv search /path/to/project "async" --threshold 0.8
pv search /path/to/project "test" --threshold 0.9

# Multi-word queries (semantic search)
pv search /path/to/project "user login validation" --threshold 0.5

# Find specific constructs
pv search /path/to/project "class" --limit 10
```

**Output:**

```
Search Results for: authentication logic

Found 5 result(s) with threshold >= 0.5

╭─────────────────────── Result 1 ───────────────────────╮
│ src/auth/login.py                                      │
│ Lines 45-67 | Similarity: 0.892                        │
│                                                        │
│ def authenticate_user(username: str, password: str):   │
│     """                                                │
│     Authenticate user credentials against database     │
│     Returns user object if valid, None otherwise       │
│     """                                                │
│     ...                                                │
╰────────────────────────────────────────────────────────╯
```

### 4. Start MCP Server

```bash
# Start server (default: localhost:8000)
pv serve /path/to/project

# Custom host/port
pv serve /path/to/project --host 0.0.0.0 --port 8080
```

### 5. Monitor Changes in Real-Time

```bash
# Watch for file changes (default 2s debounce)
pv sync /path/to/project --watch

# Fast feedback (0.5s)
pv sync /path/to/project --watch --debounce 0.5

# Slower systems (5s)
pv sync /path/to/project --watch --debounce 5.0
```

---

## Performance Optimization

### Understanding the Optimization Flags

#### `--optimize` (Permanent)

Use when **initializing** a new project. Detects your system and saves optimal settings.

```bash
pv init /path/to/project --optimize
```

**What it does:**

- Detects CPU cores → sets `max_workers` (e.g., 8 cores = 16 workers)
- Calculates RAM → sets safe `batch_size` (e.g., 16GB = 400 batch)
- Sets memory thresholds based on total RAM
- **Saves to config** - All future operations use these settings

**When to use:**

- ✅ New projects
- ✅ Want permanent optimization
- ✅ Same machine for all operations
- ✅ "Set and forget" approach

#### `--max-resources` (Temporary)

Use when **indexing** to temporarily boost performance without changing config.

```bash
pv index /path/to/project --max-resources
pv index-git /path/to/project --since HEAD~1 --max-resources
```

**What it does:**

- Detects system resources (same as --optimize)
- **Temporarily overrides** config for this operation only
- Original config unchanged

**When to use:**

- ✅ Existing project without optimization
- ✅ One-time heavy indexing
- ✅ CI/CD with dedicated resources
- ✅ Don't want to modify config

### Performance Benchmarks

**System**: 8-core CPU, 16GB RAM, SSD

| Mode               | Files     | Chunks | Time   | Settings              |
| ------------------ | --------- | ------ | ------ | --------------------- |
| Standard           | 48        | 9222   | 4m 32s | 4 workers, 100 batch  |
| --max-resources    | 48        | 9222   | 2m 16s | 16 workers, 400 batch |
| Smart incremental  | 5 changed | 412    | 24s    | 16 workers, 400 batch |
| Git-aware (HEAD~1) | 3 changed | 287    | 15s    | 16 workers, 400 batch |

**Key Findings:**

- `--max-resources`: **2x faster** for full indexing
- Smart incremental: **60-70% faster** than full reindex
- Git-aware: **80-90% faster** for recent changes
- Chunk size (128 vs 512): **No performance difference** (same ~2m 16s)

### System Resource Detection

**CPU Detection:**

```
Detected: 8 cores
Optimal workers: min(8 * 2, 16) = 16 workers
```

**Memory Detection:**

```
Total RAM: 16GB
Available RAM: 8GB
Safe batch size: 8GB * 0.5 * 100 = 400
Embedding batch: 400 * 0.5 = 200
GC interval: 100 files
```

**Memory Thresholds:**

```
32GB+ RAM → threshold: 50000
16-32GB   → threshold: 20000
8-16GB    → threshold: 10000
<8GB      → threshold: 5000
```

### Best Practices

1. **Initialize with optimization**

   ```bash
   pv init ~/my-project --optimize
   ```

2. **Use max resources for heavy operations**

   ```bash
   pv index ~/my-project --force --max-resources
   ```

3. **Use smart mode for daily updates**

   ```bash
   pv index ~/my-project --smart
   ```

4. **Use git-aware after pulling changes**

   ```bash
   pv index-git ~/my-project --since HEAD~1
   ```

5. **Monitor memory with verbose mode**
   ```bash
   pv index ~/my-project --max-resources --verbose
   ```

---

## CLI Commands

### Global Options

```bash
pv [OPTIONS] COMMAND [ARGS]

Options:
  -v, --verbose    Enable verbose output
  --version        Show version
  --help           Show help
```

### `pv init` - Initialize Project

Initialize a new project for vectorization.

```bash
pv init [OPTIONS] PROJECT_PATH

Options:
  -n, --name TEXT              Project name (default: directory name)
  -m, --embedding-model TEXT   Model name (default: all-MiniLM-L6-v2)
  -p, --embedding-provider     Provider: sentence-transformers | openai
  -c, --chunk-size INT         Chunk size in tokens (default: 256)
  -o, --chunk-overlap INT      Overlap in tokens (default: 32)
  --optimize                   Auto-optimize based on system resources ⭐
```

**Examples:**

```bash
# Basic initialization
pv init /path/to/project

# With optimization (recommended)
pv init /path/to/project --optimize

# With OpenAI embeddings
export OPENAI_API_KEY="sk-..."
pv init /path/to/project \
  --embedding-provider openai \
  --embedding-model text-embedding-ada-002 \
  --optimize
```

### `pv index` - Index Codebase

Index the codebase for searching.

```bash
pv index [OPTIONS] PROJECT_PATH

Options:
  -i, --incremental      Only index changed files
  -s, --smart            Smart incremental (categorized: new/modified/deleted) ⭐
  -f, --force            Force re-index all files
  --max-resources        Use maximum system resources ⭐
```

**Examples:**

```bash
# Full indexing with max resources
pv index /path/to/project --max-resources

# Smart incremental (fastest for updates)
pv index /path/to/project --smart

# Combine for maximum performance
pv index /path/to/project --smart --max-resources

# Force complete reindex
pv index /path/to/project --force
```

### `pv index-git` - Git-Aware Indexing

Index only files changed in git commits.

```bash
pv index-git [OPTIONS] PROJECT_PATH

Options:
  -s, --since TEXT       Git reference (default: HEAD~1)
  --max-resources        Use maximum system resources ⭐
```

**Examples:**

```bash
# Last commit
pv index-git /path/to/project --since HEAD~1

# Last 5 commits
pv index-git /path/to/project --since HEAD~5

# Since main branch
pv index-git /path/to/project --since main

# Since specific commit
pv index-git /path/to/project --since abc123def

# With max resources
pv index-git /path/to/project --since HEAD~10 --max-resources
```

**Use Cases:**

- After `git pull` - index only new changes
- Before code review - index PR changes
- CI/CD pipelines - index commit range
- After branch switch - index differences

### `pv search` - Search Code

Search through vectorized codebase.

```bash
pv search [OPTIONS] PROJECT_PATH QUERY

Options:
  -l, --limit INT        Number of results (default: 10)
  -t, --threshold FLOAT  Similarity threshold 0.0-1.0 (default: 0.3)
```

**Examples:**

```bash
# Natural language search
pv search /path/to/project "error handling in database connections"

# Single-word search (high threshold)
pv search /path/to/project "async" --threshold 0.9

# Find all tests
pv search /path/to/project "test" --limit 20 --threshold 0.8

# Broad semantic search (low threshold)
pv search /path/to/project "api authentication" --threshold 0.3
```

**Threshold Guide:**

- **0.8-0.95**: Single words, exact matches
- **0.5-0.7**: Multi-word phrases, semantic
- **0.3-0.5**: Complex queries, broad search
- **0.1-0.3**: Very broad, exploratory

### `pv sync` - Sync Changes / Watch Mode

Sync changes or watch for file modifications.

```bash
pv sync [OPTIONS] PROJECT_PATH

Options:
  -w, --watch           Watch for file changes
  -d, --debounce FLOAT  Debounce delay in seconds (default: 2.0)
```

**Examples:**

```bash
# One-time sync (smart incremental)
pv sync /path/to/project

# Watch mode with default debounce (2s)
pv sync /path/to/project --watch

# Fast feedback (0.5s)
pv sync /path/to/project --watch --debounce 0.5

# Slower systems (5s)
pv sync /path/to/project --watch --debounce 5.0
```

**Debounce Explained:**

- Waits X seconds after last file change before indexing
- Batches multiple rapid changes together
- Prevents redundant indexing when saving files repeatedly
- Reduces CPU usage during active development

**Recommended Values:**

- **0.5-1.0s**: Fast machines, need instant feedback
- **2.0s**: Balanced (default)
- **5.0-10.0s**: Slower machines, large codebases

### `pv serve` - Start MCP Server

Start MCP server for AI agent integration.

```bash
pv serve [OPTIONS] PROJECT_PATH

Options:
  -p, --port INT   Port number (default: 8000)
  -h, --host TEXT  Host address (default: localhost)
```

**Examples:**

```bash
# Start server
pv serve /path/to/project

# Custom port
pv serve /path/to/project --port 8080

# Expose to network
pv serve /path/to/project --host 0.0.0.0 --port 8000
```

### `pv status` - Show Project Status

Show project status and statistics.

```bash
pv status PROJECT_PATH
```

**Output:**

```
╭────────────── Project Status ──────────────╮
│ Name              my-project               │
│ Path              /path/to/project         │
│ Embedding Model   all-MiniLM-L6-v2         │
│                                            │
│ Total Files       49                       │
│ Indexed Files     48                       │
│ Total Chunks      9222                     │
│                                            │
│ Git Branch        main                     │
│ Last Updated      2025-10-13 12:15:42      │
│ Created           2025-10-10 09:30:15      │
╰────────────────────────────────────────────╯
```

---

## Configuration

### Config File Location

Configuration is stored at `<project>/.vectorizer/config.json`

### Full Configuration Reference

```json
{
  "chromadb_path": null,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_provider": "sentence-transformers",
  "openai_api_key": null,
  "chunk_size": 128,
  "chunk_overlap": 32,
  "max_file_size_mb": 10,
  "included_extensions": [
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".scala",
    ".clj",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".bat",
    ".cmd",
    ".md",
    ".txt",
    ".rst",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".graphql",
    ".proto"
  ],
  "excluded_patterns": [
    "node_modules/**",
    ".git/**",
    "__pycache__/**",
    "*.pyc",
    ".pytest_cache/**",
    "venv/**",
    "env/**",
    ".env/**",
    "build/**",
    "dist/**",
    "*.egg-info/**",
    ".DS_Store",
    "*.min.js",
    "*.min.css"
  ],
  "mcp_host": "localhost",
  "mcp_port": 8000,
  "log_level": "INFO",
  "log_file": null,
  "max_workers": 4,
  "batch_size": 100,
  "embedding_batch_size": 100,
  "parallel_file_processing": true,
  "memory_monitoring_enabled": true,
  "memory_efficient_search_threshold": 10000,
  "gc_interval": 100
}
```

### Key Settings Explained

**Embedding Settings:**

- `embedding_model`: Model for embeddings (all-MiniLM-L6-v2, text-embedding-ada-002, etc.)
- `embedding_provider`: "sentence-transformers" (local) or "openai" (API)
- `chunk_size`: Tokens per chunk (128 for precision, 512 for context)
- `chunk_overlap`: Overlap between chunks (16-32 recommended)

**Performance Settings:**

- `max_workers`: Parallel workers (auto-detected with --optimize)
- `batch_size`: Files per batch (auto-calculated with --optimize)
- `embedding_batch_size`: Embeddings per batch
- `parallel_file_processing`: Enable parallel processing (recommended: true)

**Memory Settings:**

- `memory_monitoring_enabled`: Monitor RAM usage (recommended: true)
- `memory_efficient_search_threshold`: Switch to streaming for large results
- `gc_interval`: Garbage collection frequency (files between GC)

**File Filtering:**

- `included_extensions`: File types to index
- `excluded_patterns`: Glob patterns to ignore
- `max_file_size_mb`: Skip files larger than this

**Server Settings:**

- `mcp_host`: MCP server host
- `mcp_port`: MCP server port
- `log_level`: INFO, DEBUG, WARNING, ERROR
- `chromadb_path`: Custom ChromaDB location (optional)

### Environment Variables

Create `.env` file or export:

```bash
# OpenAI API Key (required for OpenAI embeddings)
export OPENAI_API_KEY="sk-..."

# Override config values
export EMBEDDING_PROVIDER="sentence-transformers"
export EMBEDDING_MODEL="all-MiniLM-L6-v2"
export CHUNK_SIZE="256"
export DEFAULT_SEARCH_THRESHOLD="0.3"

# Database
export CHROMADB_PATH="/custom/path/to/chromadb"

# Logging
export LOG_LEVEL="INFO"
export LOG_FILE="/var/log/vectorizer.log"
```

For complete list, see [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)

### Editing Configuration

```bash
# View current config
cat /path/to/project/.vectorizer/config.json

# Edit manually
nano /path/to/project/.vectorizer/config.json

# Or regenerate with optimization
pv init /path/to/project --optimize
```

---

## Search Features

### Single-Word Search

Optimized for high-precision single-keyword searches.

```bash
# Programming keywords
pv search /path/to/project "async" --threshold 0.9
pv search /path/to/project "test" --threshold 0.8
pv search /path/to/project "class" --threshold 0.9
pv search /path/to/project "import" --threshold 0.85

# Works great for finding specific constructs
pv search /path/to/project "def" --threshold 0.9  # Python functions
pv search /path/to/project "function" --threshold 0.9  # JS functions
pv search /path/to/project "catch" --threshold 0.8  # Error handling
```

**Features:**

- **Exact Word Matching**: Prioritizes exact word boundaries
- **Keyword Detection**: Special handling for programming keywords
- **Relevance Boosting**: Huge boost for exact matches
- **High Thresholds**: Reliable results even at 0.8-0.9+

### Multi-Word Search

Semantic search for phrases and concepts.

```bash
# Natural language
pv search /path/to/project "user authentication logic" --threshold 0.5

# Code patterns
pv search /path/to/project "error handling in database" --threshold 0.4

# Features
pv search /path/to/project "rate limiting middleware" --threshold 0.6
```

### Search Result Ranking

Results ranked by:

1. **Exact word matches** (highest priority)
2. **Content type** (micro/word chunks get boost)
3. **Partial matches** within larger words
4. **Semantic similarity** from embeddings

### Recommended Thresholds by Query Type

| Query Type     | Threshold | Example                           |
| -------------- | --------- | --------------------------------- |
| Single keyword | 0.7-0.95  | "async", "test", "class"          |
| Two words      | 0.5-0.8   | "error handling", "api routes"    |
| Short phrase   | 0.4-0.7   | "user login validation"           |
| Complex query  | 0.3-0.5   | "authentication with jwt tokens"  |
| Exploratory    | 0.1-0.3   | "machine learning model training" |

---

## MCP Server

### Starting the Server

```bash
# Default (localhost:8000)
pv serve /path/to/project

# Custom settings
pv serve /path/to/project --host 0.0.0.0 --port 8080
```

### Available MCP Tools

When running, AI agents can use these tools:

1. **search_code** - Search vectorized codebase

   ```json
   {
     "query": "authentication logic",
     "limit": 10,
     "threshold": 0.5
   }
   ```

2. **get_file_content** - Retrieve full file

   ```json
   {
     "file_path": "src/auth/login.py"
   }
   ```

3. **list_files** - List all files

   ```json
   {
     "file_type": "py" // optional filter
   }
   ```

4. **get_project_stats** - Get statistics
   ```json
   {}
   ```

### HTTP Fallback API

If MCP unavailable, HTTP endpoints provided:

```bash
# Search
curl "http://localhost:8000/search?q=authentication&limit=5&threshold=0.5"

# Get file
curl "http://localhost:8000/file/src/auth/login.py"

# List files
curl "http://localhost:8000/files?type=py"

# Statistics
curl "http://localhost:8000/stats"

# Health check
curl "http://localhost:8000/health"
```

### Use Cases

1. **AI Code Review**: Let Claude analyze your codebase semantically
2. **Intelligent Navigation**: Ask AI to find relevant code
3. **Documentation**: Generate docs from actual code
4. **Onboarding**: Help new devs understand codebase
5. **Refactoring**: Find similar patterns across project

---

## Advanced Usage

### Python API

#### Basic Usage

```python
import asyncio
from pathlib import Path
from project_vectorizer.core.config import Config
from project_vectorizer.core.project import ProjectManager

async def main():
    # Initialize project
    config = Config.create_optimized(
        embedding_model="all-MiniLM-L6-v2",
        chunk_size=256
    )

    project_path = Path("/path/to/project")
    manager = ProjectManager(project_path, config)

    # Initialize
    await manager.initialize("My Project")

    # Index
    await manager.load()
    await manager.index_all()

    # Search
    results = await manager.search("authentication", limit=10, threshold=0.5)
    for result in results:
        print(f"{result['file_path']}: {result['similarity']:.3f}")

asyncio.run(main())
```

#### Progress Tracking

```python
from rich.progress import Progress, BarColumn, TaskProgressColumn

async def index_with_progress(project_path):
    config = Config.load_from_project(project_path)
    manager = ProjectManager(project_path, config)
    await manager.load()

    with Progress() as progress:
        task = progress.add_task("Indexing...", total=100)

        def update_progress(current, total, description):
            progress.update(task, completed=current, total=total, description=description)

        manager.set_progress_callback(update_progress)
        await manager.index_all()
```

#### Custom Resource Limits

```python
import psutil

async def adaptive_index(project_path):
    """Index with resources based on current load."""
    cpu_percent = psutil.cpu_percent(interval=1)

    if cpu_percent < 50:  # System idle
        config = Config.create_optimized()
    else:  # System busy
        config = Config(max_workers=4, batch_size=100)

    manager = ProjectManager(project_path, config)
    await manager.load()
    await manager.index_all()
```

### Chunk Size Optimization

The engine enforces a maximum of 128 tokens per chunk (see engine.py:35) for precision, but you can configure larger sizes for more context:

```bash
# Precision (default, forced max 128)
pv init /path/to/project --chunk-size 128

# More context (still capped at 128 by engine)
pv init /path/to/project --chunk-size 512
```

**Performance Note**: Chunk size has virtually NO impact on indexing speed (~2m 16s for both 128 and 512 tokens). Choose based on search quality needs:

- **128**: Better precision, exact matches
- **512**: More context, better understanding

### CI/CD Integration

```yaml
# .github/workflows/vectorize.yml
name: Vectorize Codebase

on:
  push:
    branches: [main]

jobs:
  vectorize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install vectorizer
        run: pip install project-vectorizer

      - name: Initialize and index
        run: |
          pv init . --optimize --name "${{ github.repository }}"
          pv index . --max-resources

      - name: Test search
        run: pv search . "test" --limit 5
```

### Custom File Filters

```json
{
  "included_extensions": [".py", ".js", ".custom"],
  "excluded_patterns": ["tests/**", "*.generated.js", "vendor/**", "*.min.*"]
}
```

### Watch Mode During Development

```bash
# Terminal 1: Watch mode
pv sync /path/to/project --watch --debounce 1.0

# Terminal 2: Make code changes
# Auto-indexes when you save

# Terminal 3: Search as you code
pv search /path/to/project "your new function" --threshold 0.5
```

---

## Troubleshooting

### Common Issues

#### 1. Slow Indexing

**Problem**: Indexing taking too long

**Solutions:**

```bash
# Use max resources
pv index /path/to/project --max-resources

# Use smart incremental for updates
pv index /path/to/project --smart

# Use git-aware for recent changes
pv index-git /path/to/project --since HEAD~1

# Check if optimization is working
pv index /path/to/project --max-resources --verbose
# Look for: "Workers: 16, Batch Size: 400"
```

#### 2. High Memory Usage

**Problem**: Process using too much RAM or getting killed

**Solutions:**

```bash
# Reduce batch size in config
{
  "batch_size": 50,
  "max_workers": 4
}

# Enable memory monitoring
{
  "memory_monitoring_enabled": true,
  "gc_interval": 50
}

# Use smaller chunks
pv init /path/to/project --chunk-size 128
```

#### 3. Poor Search Results

**Problem**: Search not finding relevant code

**Solutions:**

```bash
# Lower threshold for phrases
pv search /path/to/project "your query" --threshold 0.3

# Higher threshold for keywords
pv search /path/to/project "async" --threshold 0.9

# Use smaller chunk size for precision
# Edit config: "chunk_size": 128

# Ensure index is up to date
pv index /path/to/project --smart
```

#### 4. No Results for Single Words

**Problem**: Single-word searches return nothing

**Solutions:**

```bash
# Try lower threshold
pv search /path/to/project "yourword" --threshold 0.5

# Check if word exists
pv search /path/to/project "yourword" --threshold 0.1 --limit 1

# Reindex with smaller chunks
# Edit config: "chunk_size": 128
pv index /path/to/project --force
```

#### 5. Missing Recent Changes

**Problem**: Just-edited code not showing in search

**Solutions:**

```bash
# Run smart incremental
pv index /path/to/project --smart

# Or git-aware
pv index-git /path/to/project --since HEAD~1

# Check status
pv status /path/to/project
```

#### 6. psutil Not Found

**Problem**: Optimization not working

**Solution:**

```bash
# Install psutil
pip install psutil

# Verify
python -c "import psutil; print(f'CPUs: {psutil.cpu_count()}, RAM: {psutil.virtual_memory().available / 1024**3:.1f}GB')"

# Try again
pv init /path/to/project --optimize
```

### Debug Mode

```bash
# Enable verbose logging
pv --verbose index /path/to/project

# Check project status
pv status /path/to/project

# View config
cat /path/to/project/.vectorizer/config.json

# Check ChromaDB
ls -lh /path/to/project/.vectorizer/chromadb/
```

### Performance Debugging

```bash
# Time operations
time pv index /path/to/project
time pv index /path/to/project --max-resources

# Monitor resources during indexing
# Terminal 1:
pv index /path/to/project --max-resources

# Terminal 2:
htop  # or top
# Should see high CPU across all cores

# Check memory warnings
pv index /path/to/project --max-resources --verbose
# Look for memory warnings
```

---

## Changelog

### [0.1.2] - 2025-10-13

#### Added

- **Optimized Config Generation** - `Config.create_optimized()` auto-detects CPU/RAM
- **Max Resources Flag** - `--max-resources` for temporary performance boost
- **psutil Integration** - Automatic system resource detection
- **Unified Progress Tracking** - Clean single-line progress bar
- **Library Progress Suppression** - No more cluttered batch progress bars
- **Timing Information** - All operations show elapsed time
- **Clean Terminal Output** - Professional UI with timing

#### Performance

- **2x faster** full indexing with --max-resources
- **60-70% faster** smart incremental updates
- **80-90% faster** git-aware indexing

#### Documentation

- Comprehensive documentation overhaul
- Consolidated all guides into main README
- Added CHANGELOG.md with version history

### [0.1.1] - 2025-10-12

- Enhanced single-word search with high precision
- Multi-level chunking (micro + word-level)
- Adaptive search thresholds
- Programming keyword detection
- Improved word matching and relevance boosting

### [0.1.0] - 2025-10-10

- Initial release
- Code vectorization
- Smart incremental indexing
- Git-aware indexing
- MCP server
- Watch mode
- ChromaDB backend
- 30+ language support

---

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/starkbaknet/project-vectorizer.git
cd project-vectorizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=project_vectorizer

# Specific test
pytest tests/test_config.py

# Verbose
pytest -v
```

See [docs/TESTING.md](docs/TESTING.md) for details.

### Publishing

See [docs/PUBLISHING.md](docs/PUBLISHING.md) for PyPI publishing guide.

### Contributing Guidelines

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Ensure tests pass: `pytest`
5. Format code: `black . && isort .`
6. Commit: `git commit -m 'Add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Additional Resources

- **GitHub**: https://github.com/starkbaknet/project-vectorizer
- **PyPI**: https://pypi.org/project/project-vectorizer/
- **Issues**: https://github.com/starkbaknet/project-vectorizer/issues

---

**Made with ❤️ by StarkBakNet**

_Vectorize your codebase. Empower your AI agents. Build better software._
