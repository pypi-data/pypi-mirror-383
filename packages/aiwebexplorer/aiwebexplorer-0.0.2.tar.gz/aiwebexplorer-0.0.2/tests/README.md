# WebExplorer Test Suite

This directory contains comprehensive tests for the AI Web Explorer package.

## Test Structure

### Core Test Files

- **`test_webexplorer.py`** - Main test suite for WebExplorer class
- **`test_interfaces.py`** - Tests for IAgent and IResponse interfaces
- **`conftest.py`** - Shared fixtures and pytest configuration

### Test Categories

#### Unit Tests
- Interface compliance testing
- Initialization and configuration
- Prompt parsing functionality
- Site detection logic
- Confidence extraction
- Caching behavior

#### Integration Tests
- End-to-end WebExplorer functionality
- Agent polymorphism
- Error handling
- Cleanup operations

#### Mock Tests
- Browser interaction mocking
- HTTP request mocking
- Agent response mocking

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-mock
```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_webexplorer.py

# Run specific test class
pytest tests/test_webexplorer.py::TestWebExplorerInterface

# Run specific test method
pytest tests/test_webexplorer.py::TestWebExplorerInterface::test_webexplorer_implements_iagent
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip web-dependent tests
pytest -m "not web"
```

### Coverage (Optional)

```bash
# Install coverage tools
pip install pytest-cov

# Run with coverage
pytest --cov=aiwebexplorer --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Fixtures

### Available Fixtures

- **`webexplorer`** - Basic WebExplorer instance
- **`webexplorer_with_custom_config`** - WebExplorer with custom settings
- **`mock_html_content`** - Sample HTML for testing
- **`mock_amazon_html`** - Amazon-style HTML
- **`mock_ebay_html`** - eBay-style HTML
- **`mock_agent_response`** - Mock agent response
- **`mock_browser`** - Mock browser for testing

### Using Fixtures

```python
def test_with_fixture(webexplorer, mock_html_content):
    # Use the fixtures in your test
    assert webexplorer.max_content_length == 5000
    assert "Test Product Store" in mock_html_content
```

## Test Patterns

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_functionality():
    explorer = WebExplorer()
    response = await explorer.arun("test prompt")
    assert response.content is not None
```

### Mocking

```python
@patch.object(WebExplorer, '_explore_fast')
async def test_with_mock(mock_explore):
    mock_explore.return_value = "mocked result"
    explorer = WebExplorer()
    response = await explorer.arun("test")
    assert response.content == "mocked result"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("url,expected_site", [
    ("https://amazon.com/product", "amazon"),
    ("https://ebay.com/item", "ebay"),
    ("https://unknown.com", None),
])
def test_site_detection(url, expected_site):
    explorer = WebExplorer()
    assert explorer._detect_site_type(url) == expected_site
```

## Test Data

### Mock HTML Content

Tests use realistic HTML content to simulate real web pages:

- Product pages with titles, prices, descriptions
- E-commerce site structures (Amazon, eBay)
- Various HTML elements and CSS selectors

### Mock Responses

- Agent responses with confidence indicators
- Error responses for failure scenarios
- Structured data responses

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
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-asyncio
    - name: Run tests
      run: pytest
```

## Best Practices

### Test Organization

1. **One test class per main class/functionality**
2. **Descriptive test method names**
3. **Arrange-Act-Assert pattern**
4. **Independent tests (no dependencies between tests)**

### Mocking Strategy

1. **Mock external dependencies** (HTTP requests, browser)
2. **Use fixtures for common test data**
3. **Mock at the right level** (not too high, not too low)
4. **Verify mock interactions when important**

### Async Testing

1. **Use `@pytest.mark.asyncio` for async tests**
2. **Mock async functions with `AsyncMock`**
3. **Use `asyncio.run()` for simple async operations**

### Error Testing

1. **Test both success and failure scenarios**
2. **Verify error messages and types**
3. **Test edge cases and boundary conditions**

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the package is installed in development mode
2. **Async test failures**: Check `@pytest.mark.asyncio` decorator
3. **Mock not working**: Verify mock is applied before the code under test runs
4. **Fixture not found**: Check fixture is defined in `conftest.py` or same file

### Debug Mode

```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest -v -s tests/test_webexplorer.py::TestWebExplorerInterface::test_webexplorer_implements_iagent
```

## Contributing

When adding new tests:

1. **Follow existing naming conventions**
2. **Add appropriate docstrings**
3. **Use existing fixtures when possible**
4. **Add new fixtures to `conftest.py` if reusable**
5. **Update this README if adding new test categories**
