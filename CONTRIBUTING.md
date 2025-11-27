# Contributing to Unity3D-MCP

Thank you for your interest in contributing to Unity3D-MCP! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.8+
- Unity Editor 2019.4 LTS or later
- Git

### Setup Steps

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/unity3d-mcp.git
   cd unity3d-mcp
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Style

We use **ruff** for linting and formatting:

```bash
# Check code
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check . --fix
```

### Testing

Run tests before submitting PRs:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=unity3d_mcp --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Type Checking

Add type hints to all functions:

```python
async def create_project(name: str, template: str = "3D") -> dict[str, Any]:
    '''Create Unity project with specified template.'''
    pass
```

## Making Changes

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`

### Commit Messages

Follow conventional commits:

```
feat: Add VRM optimization tool
fix: Fix Unity path detection on macOS
docs: Update VRChat integration guide
test: Add tests for avatar upload
```

### Pull Request Process

1. Create feature branch
2. Make changes with tests
3. Run linter and tests locally
4. Push to your fork
5. Create PR with clear description
6. Wait for CI/CD checks
7. Address review feedback
8. Merge when approved

## Areas for Contribution

### High Priority
- Additional Unity operations
- More VRM optimization options
- Enhanced VRChat SDK automation
- Performance profiling tools
- Cross-platform testing

### Medium Priority
- Documentation improvements
- Example projects
- Tutorial content
- Error handling enhancements

### Low Priority
- Code refactoring
- Performance optimizations
- Additional test coverage

## Unity-Specific Guidelines

### Mocking Unity API

Since Unity can't run in CI/CD, mock all Unity operations:

```python
@pytest.mark.asyncio
async def test_unity_operation():
    with patch('subprocess.run') as mock_unity:
        mock_unity.return_value = Mock(returncode=0)
        # Test your operation
```

### VRM Testing

Use sample VRM files or mock VRM data structures:

```python
mock_vrm_data = {
    'name': 'TestAvatar',
    'triangles': 10000,
    'materials': 8
}
```

### VRChat Testing

Mock VRChat SDK operations (don't require actual SDK):

```python
with patch('vrchat_sdk.upload') as mock_upload:
    mock_upload.return_value = {'success': True}
    # Test upload logic
```

## Code Review Checklist

Before submitting PR, verify:

- ✅ Code follows ruff style guidelines
- ✅ All tests pass
- ✅ New features have tests
- ✅ Documentation updated
- ✅ Type hints added
- ✅ No hardcoded paths or credentials
- ✅ Error handling implemented
- ✅ Logging added for important operations

## Questions or Issues?

- **Bugs:** Open GitHub issue with reproduction steps
- **Features:** Open GitHub discussion first
- **Questions:** Check documentation, then ask in discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for helping improve Unity3D-MCP!** 🎮✨


