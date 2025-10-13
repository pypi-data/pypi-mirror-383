# Publishing to PyPI

This guide explains how to publish the project-vectorizer package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:

   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **GitHub Repository Secrets**: Add the following secrets to your GitHub repository:
   - Go to repository Settings → Secrets and variables → Actions
   - No API tokens needed if using Trusted Publishers (recommended, see below)

## Publishing Methods

### Method 1: Automatic Publishing via GitHub Releases (Recommended)

This is the easiest method using GitHub Actions:

1. **Update Version Number**:

   ```bash
   # Edit pyproject.toml and update the version
   vim pyproject.toml
   # Change: version = "0.1.1" to version = "0.1.2"
   ```

2. **Commit and Push Changes**:

   ```bash
   git add pyproject.toml
   git commit -m "Bump version to 0.1.1"
   git push
   ```

3. **Create a GitHub Release**:

   ```bash
   # Create and push a tag
   git tag v0.1.1
   git push origin v0.1.1

   # Or create a release via GitHub UI:
   # - Go to repository → Releases → Create a new release
   # - Choose tag: v0.1.1
   # - Release title: v0.1.1
   # - Add release notes
   # - Click "Publish release"
   ```

4. **Automated Publishing**:
   - The GitHub Action will automatically:
     - Build the package
     - Run tests
     - Publish to PyPI
     - Upload signed artifacts to the GitHub release

### Method 2: Manual Publish via GitHub Actions

You can manually trigger a publish to TestPyPI or PyPI:

1. **Go to GitHub Actions**:

   - Navigate to your repository → Actions tab
   - Select "Publish to PyPI" workflow

2. **Run Workflow**:
   - Click "Run workflow"
   - Choose environment:
     - `testpypi` - For testing
     - `pypi` - For production
   - Click "Run workflow"

### Method 3: Local Publishing (Advanced)

For local testing and publishing:

1. **Install Build Tools**:

   ```bash
   pip install build twine
   ```

2. **Build the Package**:

   ```bash
   # Clean previous builds
   rm -rf dist/ build/ *.egg-info/

   # Build the package
   python -m build
   ```

3. **Test the Build**:

   ```bash
   # Check the package
   twine check dist/*

   # Test install locally
   pip install dist/project_vectorizer-0.1.0-py3-none-any.whl
   ```

4. **Upload to TestPyPI** (Testing):

   ```bash
   twine upload --repository testpypi dist/*

   # Test installation from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ project-vectorizer
   ```

5. **Upload to PyPI** (Production):
   ```bash
   twine upload dist/*
   ```

## Setting Up Trusted Publishers (Recommended)

Trusted Publishers is the most secure way to publish without API tokens:

### For PyPI:

1. Go to [PyPI](https://pypi.org/)
2. Navigate to your project (create it first if needed)
3. Go to "Publishing" → "Add a new publisher"
4. Fill in:
   - **PyPI Project Name**: `project-vectorizer`
   - **Owner**: `starkbaknet`
   - **Repository name**: `project-vectorizer`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`

### For TestPyPI:

1. Go to [TestPyPI](https://test.pypi.org/)
2. Follow the same steps as above
3. Use environment name: `testpypi`

## Version Management

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (e.g., 0.1.0 → 0.2.0)
- **PATCH**: Bug fixes (e.g., 0.1.0 → 0.1.1)

### Version Update Checklist:

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG in `README.md`
- [ ] Commit changes
- [ ] Create git tag
- [ ] Push tag to trigger release
- [ ] Verify release on PyPI

## Pre-Release Checklist

Before publishing a new version:

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black . && isort .`
- [ ] Version number updated in `pyproject.toml`
- [ ] README.md is up to date
- [ ] CHANGELOG section updated
- [ ] Git tag created with correct version

## Testing the Package

After publishing to TestPyPI:

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    project-vectorizer

# Test the installation
pv --version
pv --help

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

## Troubleshooting

### Common Issues:

1. **Version already exists**:

   - You cannot re-upload the same version
   - Increment the version number in `pyproject.toml`

2. **Authentication failed**:

   - Verify your API token or Trusted Publisher setup
   - Check GitHub Actions secrets

3. **Package not found**:

   - Wait a few minutes after publishing
   - Check PyPI for the package page

4. **Import errors after install**:

   - Verify MANIFEST.in includes all necessary files
   - Check that `__init__.py` files exist in all packages

5. **Dependencies not installing**:
   - Verify dependency versions in `pyproject.toml`
   - Test with TestPyPI first

## Package URLs

After publishing:

- **PyPI**: https://pypi.org/project/project-vectorizer/
- **TestPyPI**: https://test.pypi.org/project/project-vectorizer/

## Support

For issues with publishing:

- Check [PyPI Help](https://pypi.org/help/)
- Review [Python Packaging Guide](https://packaging.python.org/)
- Open an issue in the repository
