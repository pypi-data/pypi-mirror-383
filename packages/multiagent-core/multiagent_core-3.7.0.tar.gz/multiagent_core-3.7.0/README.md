# MultiAgent Core

**Production-ready multi-agent development framework with intelligent automation**

[![PyPI version](https://badge.fury.io/py/multiagent-core.svg)](https://pypi.org/project/multiagent-core/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Quick Start

```bash
# Install from PyPI
pip install multiagent-core

# Initialize a new project
multiagent init my-project
cd my-project

# Check installation
multiagent status
```

## What is MultiAgent Core?

A comprehensive framework that transforms any project into a coordinated multi-agent development environment. Provides:

- 🤖 **Agent Coordination** - Claude, Copilot, Qwen, Gemini, Codex working in parallel via git worktrees
- 🔌 **MCP Integration** - Model Context Protocol servers with on-demand loading (43-48% more context)
- 📋 **Automated Workflows** - Slash commands for testing, deployment, PR reviews, and documentation
- 🔧 **Smart Project Detection** - Auto-detects tech stack and generates optimal configurations
- 🔒 **Security First** - Built-in secret scanning, compliance checks, and safe deletion protocols
- 📊 **Comprehensive Testing** - Unified testing strategy with intelligent project detection

## Core Commands

```bash
multiagent init          # Initialize framework in project
multiagent status        # Show component installation status
multiagent detect        # Detect project tech stack
multiagent doctor        # Health check and diagnostics
multiagent env-init      # Generate smart environment config
multiagent upgrade       # Update all components
```

## Slash Commands

Powerful automation via Claude Code slash commands:

### 🧪 Testing
- `/testing:test` - Unified testing with intelligent routing
- `/testing:test-generate` - Generate test structure from tasks
- `/testing:test-prod` - Production readiness validation

### 🚀 Deployment
- `/deployment:deploy-prepare` - Orchestrate deployment prep
- `/deployment:deploy-validate` - Validate deployment config
- `/deployment:deploy-run` - Execute local deployment
- `/deployment:deploy` - Deploy to cloud platforms
- `/deployment:prod-ready` - Comprehensive production scan

### 🔄 Iteration
- `/iterate:tasks` - Apply task layering for parallel work
- `/iterate:sync` - Sync entire spec ecosystem
- `/iterate:adjust` - Live development adjustments

### 👁️ Supervision
- `/supervisor:start` - Pre-work agent verification
- `/supervisor:mid` - Progress monitoring
- `/supervisor:end` - Pre-PR completion checks

### 📝 Documentation & Planning
- `/docs:init`, `/docs:update`, `/docs:validate`
- `/planning:plan`, `/planning:tasks`, `/planning:plan-generate`

### 🐙 GitHub Integration
- `/github:create-issue` - Create issues with templates
- `/github:pr-review` - Analyze PR feedback
- `/github:discussions` - Manage discussions

### 🔌 MCP Server Management
- `/mcp:setup` - Interactive wizard for API key configuration
- `/mcp:list` - Show all available MCP servers
- `/mcp:add <server>` - Add server to current project
- `/mcp:remove <server>` - Remove server from project
- `/mcp:status` - Show project's MCP configuration
- `/mcp:clear` - Remove all servers (maximize context)

## MCP Integration

**Model Context Protocol (MCP) servers extend Claude Code with custom tools and integrations.**

MultiAgent Core uses a **two-tier MCP system** to maximize context window:

1. **Global Registry** (`~/.claude/mcp-servers-registry.json`) - Available servers catalog
2. **Per-Project Config** (`.mcp.json`, `.vscode/mcp.json`) - Load only what's needed

### Quick Start

```bash
# One-time setup: Add API keys to shell config
/mcp:config edit

# View available servers
/mcp:list

# Add servers to your project
/mcp:add github memory

# Check project status
/mcp:status
```

### Available MCP Servers

**Standard Servers:**
- `github` - GitHub API integration
- `postman` - API testing & collections
- `memory` - Persistent conversation memory
- `playwright` - Browser automation
- `filesystem` - File/directory operations
- `supabase` - Supabase backend operations

**Custom Servers (with local/remote variants):**
- `signalhire` - Talent search API
- `airtable` - Database operations
- `twilio` - SMS/voice communications
- `calendly` - Appointment scheduling

### Context Window Optimization

**Problem:** Auto-loading all MCP servers = ~96,000 tokens wasted
**Solution:** Load servers on-demand = 43-48% more context available

```bash
# ❌ Bad: Global auto-load (wastes tokens everywhere)
~/.claude/settings.json with all servers

# ✅ Good: Per-project as needed
cd project-a && /mcp:add github memory
cd project-b && /mcp:add postman
cd project-c                              # No servers = max context
```

### API Key Management

API keys are stored in `~/.bashrc` (single source of truth) and **hardcoded** into project configs:

```bash
# View configured keys
/mcp:check

# Add/update keys
/mcp:config edit
# Or manually: nano ~/.bashrc
# Add: export POSTMAN_API_KEY="your-key"
source ~/.bashrc
```

**Security:**
- Keys stored in `~/.bashrc` (not committed to git)
- Project configs (`.mcp.json`, `.vscode/mcp.json`) are gitignored
- `/mcp:add` reads from environment and hardcodes values (no `${VAR}` placeholders)

### Adding Custom Servers to Registry

**Use the `/mcp:registry` command to add custom servers:**

```bash
# Add a new server to the registry
/mcp:registry add your-server local npx

# Follow prompts for:
# - Package name: @your-org/your-mcp-server
# - Environment variables: YOUR_API_KEY
# - Description: Your server description
```

**Then add API keys and use your server:**

```bash
# Add API key
/mcp:config edit
# Add: export YOUR_API_KEY="your-key"
source ~/.bashrc

# Add to project
/mcp:add your-server
```

**Or manually edit `~/.claude/mcp-servers-registry.json`** (see complete guide for format)

**📚 Documentation:**
- **Quick Start:** [docs/MCP_QUICK_START.md](docs/MCP_QUICK_START.md)
- **Complete Guide:** `~/.claude/MCP_COMPLETE_GUIDE.md` (run `/docs mcp` to load)

## Project Structure

After `multiagent init`:

```
your-project/
├── .multiagent/          # Core automation system
│   ├── core/            # Agent workflows & templates
│   ├── deployment/      # Deployment automation
│   ├── testing/         # Test generation & execution
│   ├── security/        # Security scanning & compliance
│   └── supervisor/      # Agent monitoring
├── .claude/              # Claude Code configuration
│   ├── agents/          # Specialized agent definitions
│   ├── commands/        # Slash command definitions
│   └── hooks/           # Git hooks & automation
├── .github/workflows/    # CI/CD automation
└── specs/               # Feature specifications & tasks
```

## Architecture

```
multiagent_core/
├── cli.py              # Main CLI with 15+ commands
├── detector.py         # Tech stack detection
├── analyzer.py         # Environment analysis
├── env_generator.py    # Smart .env generation
├── auto_updater.py     # Auto-update system
├── config.py           # Configuration management
└── templates/          # Deployment templates
```

## Development Workflow

**For Contributors:**

1. **Install in editable mode:**
   ```bash
   pip install -e . --force
   ```

2. **Edit source templates** in root directories (`.multiagent/`, `.claude/`)
   - Build system auto-syncs to `multiagent_core/templates/`

3. **Test changes:**
   ```bash
   cd /tmp && multiagent init test-project
   ```

4. **Build & test distribution:**
   ```bash
   python -m build
   pip install dist/multiagent_core-*.whl --force
   ```

## Automation Systems

Each subsystem is self-contained with its own README:

| System | Path | Purpose |
|--------|------|---------|
| **Core** | `.multiagent/core/` | Agent workflows, templates, coordination |
| **Deployment** | `.multiagent/deployment/` | Multi-platform deployment automation |
| **Testing** | `.multiagent/testing/` | Intelligent test generation & execution |
| **Security** | `.multiagent/security/` | Secret scanning, compliance, auditing |
| **Supervisor** | `.multiagent/supervisor/` | Agent monitoring & compliance |
| **PR Review** | `.multiagent/github/pr-review/` | Automated PR analysis & feedback |
| **Iterate** | `.multiagent/iterate/` | Spec synchronization & task layering |

## Release & Versioning

- **Semantic Versioning** via conventional commits
- **Automated Releases** on push to main
- **PyPI Publishing** via GitHub Actions
- **Version Management** - `.github/workflows/version-management.yml`

Commit format:
```
feat: Add new command
fix: Resolve deployment issue
docs: Update README
chore: Bump dependencies
```

## Testing

```bash
# Run full test suite
python -m pytest

# GitHub Actions tests:
# - Ubuntu, Windows, macOS
# - Python 3.8-3.12
# - pip, pipx, source installs
```

## Documentation

- **User Guide**: [`.multiagent/README.md`](.multiagent/README.md) (deployed to projects)
- **Developer Docs**: [`docs/`](docs/) (contributor guide)
- **System Docs**: Each subsystem has its own README

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with conventional commits
4. Test with `python -m pytest`
5. Submit PR with detailed description

## License

MIT License - see LICENSE file

---

**Install now:** `pip install multiagent-core`

**Documentation:** [.multiagent/README.md](.multiagent/README.md)
# Auto-sync test
