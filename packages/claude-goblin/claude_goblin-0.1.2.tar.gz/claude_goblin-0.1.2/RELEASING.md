# Release Process

## Publishing to PyPI

### Prerequisites
1. Make sure you have `build` and `twine` installed:
   ```bash
   pip install build twine
   ```

2. Have PyPI credentials ready (API token recommended)

### Release Steps

1. **Update version number** in `pyproject.toml`:
   ```toml
   version = "0.1.1"
   ```

2. **Update CHANGELOG.md** with release notes:
   - List all changes under the new version
   - Follow format: Added, Changed, Deprecated, Removed, Fixed, Security

3. **Commit version bump**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.1"
   git tag v0.1.1
   git push origin master --tags
   ```

4. **Build distribution packages**:
   ```bash
   python -m build
   ```
   This creates `dist/claude-goblin-0.1.1.tar.gz` and `dist/claude_goblin-0.1.1-py3-none-any.whl`

5. **Upload to TestPyPI** (optional, for testing):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

   Test install:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ claude-goblin
   ```

6. **Upload to PyPI** (production):
   ```bash
   python -m twine upload dist/*
   ```

7. **Create GitHub Release** (optional):
   - Go to GitHub releases page
   - Create new release from tag `v0.1.1`
   - Copy release notes from CHANGELOG.md
   - Attach distribution files if desired

### Release Notes on PyPI

PyPI will automatically use:
1. **Short description**: From `description` field in `pyproject.toml`
2. **Long description**: From `README.md` (specified in `readme` field)
3. **Changelog**: PyPI doesn't have a dedicated changelog section, but you can:
   - Add a "Release History" section to README.md
   - Link to CHANGELOG.md on GitHub
   - Include recent changes in GitHub release notes

### Post-Release

1. **Verify installation**:
   ```bash
   pip install claude-goblin --upgrade
   claude-goblin --help
   ```

2. **Announce release** (optional):
   - Update documentation
   - Post on social media
   - Notify users

## Version Numbering

Follow Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (e.g., 0.1.0 → 0.2.0)
- **PATCH**: Bug fixes, backward compatible (e.g., 0.1.0 → 0.1.1)

## Current Release: 0.1.1

### Changes in 0.1.1:
- **CRITICAL BUG FIX**: Fixed data loss in full storage mode
- Migrated to typer CLI framework
- Improved command syntax and help messages
