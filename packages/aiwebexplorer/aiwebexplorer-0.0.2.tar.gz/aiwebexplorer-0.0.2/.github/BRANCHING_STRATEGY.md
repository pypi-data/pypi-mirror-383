# WebExplorer Branching Strategy & Versioning

## 🌿 Branch Structure

### Main Branches
- **`master`** - Production-ready code, latest stable release
- **`develop`** - Integration branch for features, pre-release testing

### Supporting Branches
- **`feature/*`** - New features (e.g., `feature/user-authentication`)
- **`hotfix/*`** - Critical fixes for production (e.g., `hotfix/security-patch`)
- **`release/*`** - Release preparation (e.g., `release/v1.2.0`)

## 🚀 Deployment Workflow

### 1. Feature Development
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# Work on feature, commit changes
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create PR to develop
# After review and merge, delete feature branch
```

### 2. Release Preparation
```bash
# Create release branch from develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# Update CHANGELOG.md
# Final testing
# Note: Version is managed automatically by setuptools_scm from git tags

# Merge to master
git checkout master
git merge release/v1.2.0
git tag v1.2.0
git push origin master --tags

# Merge back to develop
git checkout develop
git merge release/v1.2.0
git push origin develop
```

### 3. Hotfix Process
```bash
# Create hotfix from master
git checkout master
git checkout -b hotfix/critical-bug

# Fix the issue, commit
git commit -m "fix: resolve critical bug"
git push origin hotfix/critical-bug

# Merge to master and develop
git checkout master
git merge hotfix/critical-bug
git tag v1.2.1
git push origin master --tags

git checkout develop
git merge hotfix/critical-bug
git push origin develop
```

## 📦 Versioning Strategy

### Semantic Versioning (SemVer)
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Bumping Rules
- **Patch** (1.0.0 → 1.0.1): Bug fixes, hotfixes
- **Minor** (1.0.0 → 1.1.0): New features, enhancements
- **Major** (1.0.0 → 2.0.0): Breaking changes

### Automated Versioning
The CI/CD pipeline will:
1. Check version consistency between `pyproject.toml` and git tags
2. Automatically publish to PyPI when version tags are pushed
3. Create GitHub releases for each version

## 🔄 CI/CD Triggers

### Development Workflow
- **Push to `develop`**: Run tests, linting, formatting
- **PR to `develop`**: Run tests, linting, formatting

### Release Workflow
- **Push to `master`**: Run full test suite, create release if version tag exists
- **Version tag push** (e.g., `v1.2.0`): Build and publish to PyPI

### Manual Triggers
- **Workflow dispatch**: Manual version publishing
- **Release creation**: Automatic GitHub release creation

## 📋 Release Checklist

### Before Release
- [ ] All features merged to `develop`
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Git tag created (version managed by setuptools_scm)

### Release Process
- [ ] Create release branch from `develop`
- [ ] Final testing on release branch
- [ ] Merge to `master`
- [ ] Create and push version tag (e.g., `git tag v1.2.0 && git push origin v1.2.0`)
- [ ] Verify PyPI publication (automatic via GitHub Actions)
- [ ] Create GitHub release (automatic via GitHub Actions)

### Automated Release Process
For automated releases, commit with message: `chore: release v1.2.0`
This will trigger:
1. Version tag creation
2. PyPI publication
3. GitHub release creation

### Post-Release
- [ ] Merge release branch back to `develop`
- [ ] Delete release branch
- [ ] Update documentation
- [ ] Announce release

## 🏷️ Tagging Convention

### Version Tags
- **Format**: `v1.2.3`
- **Examples**: `v1.0.0`, `v1.2.3`, `v2.0.0-beta.1`

### Pre-release Tags
- **Alpha**: `v1.2.0-alpha.1`
- **Beta**: `v1.2.0-beta.1`
- **RC**: `v1.2.0-rc.1`

## 🔧 Configuration Files

### pyproject.toml
```toml
[project]
name = "aiwebexplorer"
dynamic = ["version"]  # Version managed by setuptools_scm

[tool.setuptools_scm]
write_to = "src/aiwebexplorer/_version.py"

# Note: _version.py is generated automatically and should not be committed
```

### CHANGELOG.md
```markdown
# Changelog

## [1.2.0] - 2024-01-15
### Added
- New feature X
- Enhanced feature Y

### Changed
- Improved performance
- Updated dependencies

### Fixed
- Bug fix A
- Bug fix B
```

## 🚨 Emergency Procedures

### Critical Hotfix
1. Create hotfix branch from `master`
2. Fix the issue
3. Test thoroughly
4. Merge to `master` and `develop`
5. Create patch release
6. Deploy immediately

### Rollback Procedure
1. Revert to previous stable tag
2. Create hotfix for rollback
3. Communicate with users
4. Plan proper fix
