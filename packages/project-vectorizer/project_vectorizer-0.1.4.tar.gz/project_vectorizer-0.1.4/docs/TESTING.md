# Testing Guide

This guide provides comprehensive information about testing the Project Vectorizer application.

## Overview

The Project Vectorizer has a robust test suite with **46 tests** covering all major functionality. All tests are designed to work with ChromaDB databases and require no external services.

## Quick Start

### Install Test Dependencies

```bash
# Install the project with development dependencies
pip install -e ".[dev]"

# Or install test dependencies manually
pip install pytest pytest-asyncio pytest-cov python-dotenv
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=project_vectorizer --cov-report=html
```

## Test Structure

### Test Files

| File                            | Purpose                                | Test Count |
| ------------------------------- | -------------------------------------- | ---------- |
| `test_environment_variables.py` | Configuration and environment handling | 11 tests   |
| `test_single_word_search.py`    | Single-word search functionality       | 7 tests    |
| `test_multi_level_chunking.py`  | Code chunking and parsing              | 9 tests    |
| `test_complete_workflow.py`     | End-to-end workflows                   | 5 tests    |
| `test_error_handling.py`        | Error handling and edge cases          | 14 tests   |

### Test Categories

#### 1. Environment Variables (11 tests)

Tests configuration loading, validation, and environment variable handling:

- ✅ Default configuration values
- ✅ Environment variable overrides
- ✅ Configuration priority system
- ✅ Invalid value validation (Pydantic)
- ✅ List-based environment variables
- ✅ OpenAI API key loading
- ✅ ChromaDB path configuration variations
- ✅ Project-specific .env loading
- ✅ Environment file precedence
- ✅ Direct environment variables
- ✅ Configuration serialization

#### 2. Single-Word Search (7 tests)

Tests enhanced search functionality for single-word queries:

- ✅ Exact match detection
- ✅ Programming keyword detection
- ✅ Word boundary matching
- ✅ Adaptive threshold handling
- ✅ Similarity boosting
- ✅ Multiple language support
- ✅ Result ranking priority

#### 3. Multi-Level Chunking (9 tests)

Tests code parsing and chunking capabilities:

- ✅ Function and class chunking
- ✅ Micro-chunk generation
- ✅ Word-level chunks
- ✅ Chunk size respect
- ✅ JavaScript chunking
- ✅ Chunk overlap handling
- ✅ Embedding generation
- ✅ Line number tracking
- ✅ Chunk content quality

#### 4. Complete Workflows (5 tests)

Tests end-to-end functionality:

- ✅ Init → Index → Search workflow
- ✅ Incremental indexing (fixed)
- ✅ Multi-language projects
- ✅ Large project handling
- ✅ Project statistics and status

#### 5. Error Handling (14 tests)

Tests error handling and edge cases:

- ✅ Invalid configuration values
- ✅ Missing project initialization
- ✅ Nonexistent project paths
- ✅ Corrupted file handling
- ✅ Empty file handling
- ✅ Large file handling
- ✅ Invalid search parameters
- ✅ Database connection errors
- ✅ Embedding generation failures
- ✅ Concurrent access handling
- ✅ File permission errors
- ✅ Malformed code files
- ✅ Memory pressure handling
- ✅ Config file corruption

## Running Tests

### Using pytest Directly

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_environment_variables.py

# Run specific test
pytest tests/test_environment_variables.py::TestEnvironmentVariables::test_default_config_values

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=project_vectorizer --cov-report=term-missing

# Run only fast tests (skip slow ones)
pytest tests/ -m "not slow"

# Run with maximum verbosity for debugging
pytest tests/ -vvv -s --tb=long
```

### Using the Custom Test Runner

```bash
# Run all tests
python tests/test_runner.py all

# Run quick subset for fast feedback
python tests/test_runner.py quick

# Run specific test suites
python tests/test_runner.py env          # Environment variable tests
python tests/test_runner.py search      # Single-word search tests
python tests/test_runner.py chunking    # Multi-level chunking tests
python tests/test_runner.py workflow    # Complete workflow tests
python tests/test_runner.py errors      # Error handling tests

# Run performance tests
python tests/test_runner.py perf
```

## Test Configuration

### pytest.ini Configuration

The project includes a `pytest.ini` file with optimized settings:

```ini
[tool:pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --tb=short
    --asyncio-mode=auto
    -ra
    --durations=10
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::UserWarning:sentence_transformers.*
    ignore::UserWarning:torch.*
    ignore::FutureWarning:transformers.*
markers =
    asyncio: marks tests as async
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    performance: marks tests as performance tests
asyncio_mode = auto
timeout = 300
```

### Test Fixtures

Tests use comprehensive fixtures defined in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `sample_python_file` - Comprehensive Python code sample
- `sample_js_file` - JavaScript code sample
- `env_file` - Test environment configuration
- `test_config` - Pre-configured Config object
- `vectorizer_engine` - Initialized vectorization engine
- `test_project` - Complete project setup

## Database Requirements

### ChromaDB-Only Approach

All tests use ChromaDB databases exclusively:

- ✅ **No external database services required**
- ✅ **Each test uses isolated database files**
- ✅ **Automatic cleanup after tests**

### Database Isolation

Each test creates its own temporary ChromaDB database:

```python
# Example from conftest.py
@pytest.fixture
async def test_project(temp_dir: Path, test_config: Config) -> ProjectManager:
    """Create a test project with sample files."""
    project_manager = ProjectManager(temp_dir, test_config)
    await project_manager.initialize("test-project")
    return project_manager
```

## Recent Fixes

### Major Issues Resolved

1. **Environment Variable Loading** - Fixed Config class to properly load .env files
2. **Incremental Indexing** - Fixed file discovery in `index_all()` method
3. **Pydantic Validation** - Added proper validation for configuration values
4. **Error Handling** - Improved error handling for corrupted config files

### Test Isolation Improvements

- ✅ **Environment cleanup** - Tests properly clear environment variables between runs
- ✅ **Temporary directories** - All tests use isolated temporary directories
- ✅ **Database isolation** - Each test uses its own ChromaDB database file

## Performance

### Test Execution Times

- **Environment Variables**: ~0.2 seconds
- **Single-Word Search**: ~32 seconds (includes model loading)
- **Multi-Level Chunking**: ~40 seconds (includes model loading)
- **Complete Workflows**: ~5 seconds
- **Error Handling**: ~0.3 seconds

**Total**: ~5.5 minutes for all 46 tests

### Optimization Tips

```bash
# Run only fast tests for quick feedback
pytest tests/ -m "not slow"

# Run specific test suites
python tests/test_runner.py quick

# Run tests in parallel (if pytest-xdist is installed)
pytest tests/ -n auto
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest tests/ --cov=project_vectorizer --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Troubleshooting

### Common Issues

1. **Import errors** - Ensure project is in Python path
2. **Async test failures** - Check `pytest-asyncio` is installed
3. **Slow tests** - Use `python tests/test_runner.py quick`
4. **Memory errors** - Reduce test dataset sizes
5. **Permission errors** - Ensure write access to temp directories

### Debug Mode

Run tests with maximum verbosity:

```bash
pytest tests/ -vvv -s --tb=long
```

Enable debug logging in tests:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Adding New Tests

### Guidelines

1. **Use appropriate fixtures** from `conftest.py`
2. **Mark async tests** with `@pytest.mark.asyncio`
3. **Add descriptive docstrings** explaining what is tested
4. **Test both success and failure cases**
5. **Use meaningful assertions** with helpful error messages
6. **Clean up resources** (handled by fixtures)

### Example Test

```python
@pytest.mark.asyncio
async def test_new_feature(self, temp_dir: Path):
    """Test description of what this verifies."""
    # Arrange
    test_file = temp_dir / "test.py"
    test_file.write_text("def new_feature(): pass")

    config = Config(chunk_size=128)
    project_manager = ProjectManager(temp_dir, config)
    await project_manager.initialize("test-new-feature")

    # Act
    await project_manager.index_all()
    results = await project_manager.search("new_feature", threshold=0.8)

    # Assert
    assert len(results) > 0, "Should find the new feature"
    assert results[0]['similarity'] >= 0.8, "Should have high similarity"
```

## Coverage Reporting

### Generate Coverage Reports

```bash
# Terminal coverage report
pytest tests/ --cov=project_vectorizer --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=project_vectorizer --cov-report=html

# XML coverage report (for CI)
pytest tests/ --cov=project_vectorizer --cov-report=xml
```

### Coverage Goals

- **Target**: >90% code coverage
- **Critical paths**: 100% coverage
- **Error handling**: 100% coverage
- **Configuration**: 100% coverage

## Conclusion

The Project Vectorizer test suite provides comprehensive coverage of all functionality with a focus on reliability, maintainability, and ease of use. All tests work with ChromaDB and require no external services, making them easy to run in any environment.
