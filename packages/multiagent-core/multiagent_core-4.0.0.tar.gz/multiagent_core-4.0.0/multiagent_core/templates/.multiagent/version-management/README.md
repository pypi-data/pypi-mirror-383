# Version Management Subsystem

Automated semantic versioning and release management for Python and TypeScript projects.

## Structure

- `docs/OVERVIEW.md` - Complete version management documentation
- `templates/python/github-workflows/` - Python semantic-release workflows
- `templates/typescript/github-workflows/` - TypeScript semantic-release workflows
- `scripts/` - Version management scripts
- `memory/` - Release history and metadata
- `logs/` - Release logs

## How It Works

1. **Pre-push hook** reminds at 10+ commits
2. **Conventional commits** determine version bump (feat/fix/BREAKING)
3. **GitHub Actions** auto-publishes on push to main
4. **Semantic-release** handles versioning, changelog, GitHub release, PyPI/npm publish

See `docs/OVERVIEW.md` for complete documentation.
