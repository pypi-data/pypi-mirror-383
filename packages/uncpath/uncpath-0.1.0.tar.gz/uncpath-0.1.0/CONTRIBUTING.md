# Contributing to uncpath-py

## Development Setup

1. Install [uv](https://github.com/astral-sh/uv):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/JiashuaiXu/uncpath-py.git
cd uncpath-py
```

3. Install dependencies:
```bash
uv sync
```

## Running Tests

```bash
uv run -m pytest -q
```

For verbose output:
```bash
uv run -m pytest -v
```

## Building the Package

```bash
uv build
```

This will create distribution files in the `dist/` directory.

## Release Process

The release process is fully automated through GitHub Actions:

1. **Update version**: Edit the `version` field in `pyproject.toml`

2. **Create and push a tag**:
```bash
git tag v0.1.0
git push origin v0.1.0
```

3. **Automated workflow**: The GitHub Actions workflow will automatically:
   - Run tests
   - Build the package
   - Publish to PyPI (requires `PYPI_TOKEN` secret)
   - Create a GitHub Release with build artifacts

## Adding PYPI_TOKEN

To enable automatic publishing to PyPI:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope for this project
3. Add it as a secret in GitHub:
   - Go to repository Settings → Secrets and variables → Actions
   - Create a new secret named `PYPI_TOKEN`
   - Paste your PyPI token

## Code Style

- Follow PEP 8 guidelines
- Write tests for new functionality
- Update documentation as needed
