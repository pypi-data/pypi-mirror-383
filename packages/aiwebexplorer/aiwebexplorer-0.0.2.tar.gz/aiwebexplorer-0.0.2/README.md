# AIWebExplorer

An agent for agents to explore the web

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd AIWebExplorer

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## Development

```bash
# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Run type checking
uv run ruff check --select I
```

## Environment Variables

Copy `.env.example` to `.env` and adjust the values:

```env
ENV=DEV
LOG_LEVEL=INFO
```

## New Features

To develop a new feature:

1. **Create a feature branch from `develop`:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Work on your feature and commit changes:**
   ```bash
   git add .
   git commit -m "feat: add your new feature"
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request to `develop` branch**
4. **After review and merge, delete the feature branch**

## New Versions

### Option 1: Automated Release (Recommended)

For automated releases, simply commit with the release message:

```bash
git commit -m "chore: release v1.2.0"
git push origin master
```

This will automatically:
- Create the version tag
- Publish to PyPI
- Create a GitHub release

### Option 2: Manual Release

1. **Create a release branch from `develop`:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.2.0
   ```

2. **Update CHANGELOG.md with your changes**

3. **Merge to master and create version tag:**
   ```bash
   git checkout master
   git merge release/v1.2.0
   git tag v1.2.0
   git push origin master --tags
   ```

4. **Merge back to develop:**
   ```bash
   git checkout develop
   git merge release/v1.2.0
   git push origin develop
   ```

The CI/CD pipeline will automatically:
- Run tests and linting
- Build and publish to PyPI when version tags are pushed
- Create GitHub releases

**Version numbering:**
- **Patch** (1.0.0 → 1.0.1): Bug fixes
- **Minor** (1.0.0 → 1.1.0): New features
- **Major** (1.0.0 → 2.0.0): Breaking changes

## License

[Add your license here]
