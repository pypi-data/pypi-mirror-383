# Project Documentation

This directory will be populated when you run:

```bash
/docs:init
```

The `/docs:init` command reads universal templates from `~/.claude/docs/templates/`
and creates project-specific documentation:

- `README.md` - Project overview
- `ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - Contribution guide
- `CHANGELOG.md` - Version history
- `TROUBLESHOOTING.md` - Common issues and solutions

**Universal Documentation:**
All patterns, workflows, and guides are in `~/.claude/docs/` and accessible via `/docs` command.

**Project-Specific Documentation:**
This `docs/` directory is for documentation specific to your project only.
