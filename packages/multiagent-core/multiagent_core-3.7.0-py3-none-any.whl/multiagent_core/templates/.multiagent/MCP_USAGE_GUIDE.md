# MCP Server Management Guide

## 🎯 Overview

This project includes a unified MCP (Model Context Protocol) server management system that works with **both Claude Code and VS Code Copilot** from a single source of truth.

### Token Optimization

**Problem**: Auto-loading all MCP servers consumes ~96,000 tokens per conversation
**Solution**: Load servers on-demand per project
**Savings**: ~86,000-96,000 tokens = **43-48% more context available**

### Security First

⚠️ **NEVER hardcode API keys in MCP configuration files**

❌ **Wrong** (hardcoded):
```json
{
  "env": {
    "POSTMAN_API_KEY": "PMAK-abc123..."
  }
}
```

✅ **Correct** (environment variable):
```json
{
  "env": {
    "POSTMAN_API_KEY": "${POSTMAN_API_KEY}"
  }
}
```

## 🏗️ System Architecture

### Single Source of Truth

```
~/.claude/mcp-servers-registry.json
          ↓
    /mcp:add github
          ↓
    ┌─────────────────┬─────────────────────┐
    ↓                 ↓                     ↓
.mcp.json      .vscode/mcp.json      ~/.mcp-keys/
(Claude Code)   (VS Code Copilot)    (API Keys)
```

### File Structure

```
~/.claude/
├── mcp-servers-registry.json    # Master list of all available servers
├── commands/mcp/                # MCP management commands
│   ├── add.md                   # Add servers from registry
│   ├── remove.md                # Remove servers
│   ├── clear.md                 # Clear all servers
│   ├── status.md                # Show current configuration
│   ├── list.md                  # Browse available servers
│   ├── check.md                 # Check configured API keys
│   ├── setup.md                 # Interactive key configuration
│   └── inventory.md             # Track usage across projects
└── settings.json                # Permissions for MCP commands

~/.mcp-keys/                     # Organized API key storage
├── standard.env                 # GitHub, Postman
├── remote-servers.env           # Remote MCP server URLs
├── local-dev.env                # Local development keys
└── databases.env                # Supabase, etc.

project-root/
├── .mcp.json                    # Claude Code configuration
└── .vscode/
    └── mcp.json                 # VS Code Copilot configuration
```

## 🚀 Quick Start

### Initial Setup

1. **Run multiagent init** (creates registry and empty `.mcp.json`):
```bash
cd your-project
multiagent init
```

2. **Configure API keys**:
```bash
/mcp:setup
```

This interactive wizard will:
- Prompt for all your API keys
- Save them securely in `~/.mcp-keys/`
- Auto-load them via `~/.bashrc`

3. **Add servers to your project**:
```bash
/mcp:add github
/mcp:add memory
/mcp:add postman
```

This command writes to **both** `.mcp.json` and `.vscode/mcp.json` simultaneously.

### Daily Workflow

**Start work session:**
```bash
cd your-project
git pull  # Get latest changes
/mcp:status  # See current MCP configuration
```

**Add server when needed:**
```bash
/mcp:add playwright  # For testing
/mcp:add airtable    # For data access
```

**Remove servers to save context:**
```bash
/mcp:remove playwright  # Done testing
/mcp:clear              # Remove all for maximum context
```

**Restart to apply changes:**
- Claude Code: Restart conversation
- VS Code Copilot: `Cmd/Ctrl + Shift + P` → "Reload Window"

## 🤖 Multi-Agent Support

This MCP system is optimized for **Claude Code + VS Code Copilot** with on-demand loading:

| Agent | Config Location | Context Optimization | MCP Commands Work? |
|-------|----------------|---------------------|-------------------|
| **Claude Code** | `.mcp.json` | ✅ Yes (43-48% savings) | ✅ Yes |
| **VS Code Copilot** | `.vscode/mcp.json` | ✅ Yes (shares with Claude) | ✅ Yes |
| **Codex** | `~/.codex/config.toml` | ❌ No (larger context window) | ❌ Manual edit |
| **Gemini CLI** | `~/.gemini/settings.json` | ❌ No (larger context window) | ❌ Manual edit |
| **Qwen** | Python API | ❌ No (larger context window) | ❌ Python config |

### Why Claude Code + Copilot Only?

**Claude Code and VS Code Copilot benefit from on-demand loading** because:
- ✅ Smaller context windows (need to save tokens)
- ✅ Share the same project workspace
- ✅ Both use JSON configuration files

**Codex, Gemini, and Qwen are different** because:
- ✅ Larger context windows (don't need token optimization)
- ✅ Keep MCP servers loaded globally (always available)
- ✅ Different config formats (TOML, Python, etc.)

**Recommendation:** Use global configs for Codex/Gemini, and on-demand loading for Claude Code/Copilot.

## 📋 Available Commands

### `/mcp:list`
Browse all available MCP servers in the registry, organized by category.

**Example:**
```bash
/mcp:list

📚 Available MCP Servers

Development Tools:
  📍 github (local/remote)
     GitHub API integration
  • memory (local)
     Persistent conversation memory
  • playwright (local)
     Browser automation and testing
```

### `/mcp:add <server-name> [local|remote]`
Add a server from the registry to your project (both Claude Code and VS Code Copilot).

**Examples:**
```bash
/mcp:add github                  # Standard server
/mcp:add signalhire local        # Use local variant
/mcp:add signalhire remote       # Use remote variant
/mcp:add signalhire              # Prompt to choose variant
```

**What it does:**
1. Reads server config from `~/.claude/mcp-servers-registry.json`
2. Replaces `${VARIABLE}` placeholders with environment values
3. Writes to `.mcp.json` (for Claude Code)
4. Writes to `.vscode/mcp.json` (for VS Code Copilot)
5. Warns if required API keys are missing

### `/mcp:remove <server-name>`
Remove a server from both Claude Code and VS Code Copilot configurations.

**Example:**
```bash
/mcp:remove postman

✅ Removed 'postman' from project MCP configuration
   📍 Removed from: .mcp.json + .vscode/mcp.json
```

### `/mcp:clear`
Remove all servers to maximize context window (useful for coding-heavy tasks).

**Example:**
```bash
/mcp:clear

✅ MCP servers cleared from both configurations
   📍 Cleared: .mcp.json + .vscode/mcp.json
```

### `/mcp:status`
Show current MCP configuration for both Claude Code and VS Code Copilot.

**Example:**
```bash
/mcp:status

📊 MCP Status Overview

Claude Code (.mcp.json): 3 server(s)
  - github: http
  - memory: stdio
  - postman: stdio

VS Code Copilot (.vscode/mcp.json): 3 server(s)
  - github: http
  - memory: stdio
  - postman: stdio
```

### `/mcp:check`
Verify which API keys are currently configured.

**Example:**
```bash
/mcp:check

🔑 MCP API Key Status

✅ GITHUB_TOKEN (configured)
✅ POSTMAN_API_KEY (configured)
❌ AIRTABLE_API_KEY (missing)
```

### `/mcp:setup`
Interactive wizard to configure all API keys.

**Example:**
```bash
/mcp:setup

🔧 MCP API Key Setup
━━━━━━━━━━━━━━━━━━━━

Standard Services
  GitHub Token: ghp_...
  Postman API Key: PMAK-...

Remote MCP Servers (complete URLs):
  Format: http://your-server-ip:port/mcp
  SignalHire Remote URL: http://142.93.123.456:8080/mcp
  ...
```

### `/mcp:inventory`
Generate a global inventory showing which projects use which servers/keys.

**Example:**
```bash
/mcp:inventory

Generated: ~/.api-keys-inventory.md

# MCP API Keys Inventory

## Projects Using MCP Servers

### multiagent-core
- github (http)
- memory (stdio)
- postman (stdio)

### StaffHive
- signalhire (remote)
- airtable (remote)
```

## 🔐 API Key Management

### Organized Keys Directory

API keys are stored in `~/.mcp-keys/` with categorized `.env` files:

```bash
~/.mcp-keys/
├── standard.env           # Common services
│   GITHUB_TOKEN=ghp_...
│   POSTMAN_API_KEY=PMAK-...
│
├── remote-servers.env     # Remote MCP server URLs
│   SIGNALHIRE_REMOTE_URL=http://142.93.123.456:8080/mcp
│   AIRTABLE_REMOTE_URL=http://167.99.45.78:8082/mcp
│
├── local-dev.env          # Local development
│   SIGNALHIRE_API_KEY=abc123
│   AIRTABLE_API_KEY=xyz789
│
└── databases.env          # Database credentials
    SUPABASE_URL=https://...
    SUPABASE_ANON_KEY=...
```

### Auto-Loading Keys

Keys are automatically loaded in your shell via `~/.bashrc`:

```bash
# MCP Keys - Load from organized directory
if [ -d ~/.mcp-keys ]; then
  for env_file in ~/.mcp-keys/*.env; do
    [ -f "$env_file" ] && source "$env_file"
  done
fi
```

**To reload keys without restarting terminal:**
```bash
source ~/.bashrc
```

## 🎨 Server Variants (Local vs Remote)

Some MCP servers support multiple variants:

### Local Variant (stdio)
- Runs on your machine via `npx`
- Lower latency
- No network required
- Uses local API keys

**Example:**
```json
{
  "type": "stdio",
  "command": "npx",
  "args": ["signalhire-mcp-server"],
  "env": {
    "SIGNALHIRE_API_KEY": "${SIGNALHIRE_API_KEY}"
  }
}
```

### Remote Variant (http)
- Runs on remote droplet/server
- Shared across team
- Centralized API key management
- Network dependent

**Example:**
```json
{
  "type": "http",
  "url": "${SIGNALHIRE_REMOTE_URL}",
  "headers": {
    "Authorization": "Bearer ${MCP_AUTH_TOKEN}"
  }
}
```

### Choosing a Variant

```bash
# Let command prompt you
/mcp:add signalhire

Server 'signalhire' supports multiple variants:
  - local: Run locally via npx
  - remote: Connect to remote server
Choose variant [local/remote]: remote

# Or specify explicitly
/mcp:add signalhire local
/mcp:add signalhire remote
```

## 🧪 Common Workflows

### Workflow 1: New Project Setup (Claude Code + Copilot)

**Scenario:** Starting a new project with Claude Code and VS Code Copilot.

```bash
cd new-project
multiagent init

# Empty .mcp.json created - maximum context available!
/mcp:status

# Add servers on-demand as needed
/mcp:add github      # For Git operations
/mcp:add memory      # For persistent memory

# Both Claude Code and VS Code Copilot now have these servers
```

**Benefits:**
- ✅ Empty by default = maximum context window
- ✅ Add servers only when you need them
- ✅ Automatic sync between Claude Code + Copilot

### Workflow 2: Multi-Agent Development

**Scenario:** Using Claude Code, Copilot, Codex, and Gemini together on same project.

```bash
# For Claude Code + Copilot (on-demand loading)
/mcp:add github memory

# For Codex and Gemini (already have global MCP servers)
# Nothing to do - they use ~/.codex/config.toml and ~/.gemini/settings.json
# These are configured once globally and always available

# Result:
# - Claude Code: github, memory (loaded on-demand, saves context)
# - VS Code Copilot: github, memory (shares with Claude)
# - Codex: All servers from ~/.codex/config.toml (always loaded)
# - Gemini: All servers from ~/.gemini/settings.json (always loaded)
```

### Workflow 3: Maximum Context for Coding

```bash
# Clear all MCP servers
/mcp:clear

# Code with full context window
# ...

# Re-add servers when needed
/mcp:add github memory
```

### Workflow 2: Testing with Playwright

```bash
# Add playwright for testing
/mcp:add playwright

# Run tests
# ...

# Remove after testing
/mcp:remove playwright
```

### Workflow 3: Multi-Project Setup

```bash
# Project A - Only needs GitHub
cd ~/Projects/project-a
/mcp:add github

# Project B - Needs Airtable integration
cd ~/Projects/project-b
/mcp:add github airtable

# Check usage across projects
/mcp:inventory
```

### Workflow 4: New Server Development

```bash
# Add your custom server to registry
vim ~/.claude/mcp-servers-registry.json

# Add server definition
{
  "servers": {
    "myserver": {
      "description": "My custom MCP server",
      "category": "Custom",
      "variants": {
        "local": {
          "type": "stdio",
          "command": "node",
          "args": ["./mcp-servers/myserver/index.js"]
        }
      }
    }
  }
}

# Use in project
/mcp:add myserver local
```

## 🔍 Troubleshooting

### "Missing required API keys"

**Problem:** Added server but getting warnings about missing keys

**Solution:**
```bash
# Check what's missing
/mcp:check

# Configure missing keys
/mcp:setup

# Reload shell to pick up new keys
source ~/.bashrc

# Try adding server again
/mcp:add servername
```

### "Server already configured"

**Problem:** Trying to add a server that's already in the project

**Solution:**
```bash
# Check current status
/mcp:status

# If you need to update the config, remove first
/mcp:remove servername
/mcp:add servername
```

### Keys not loading in VS Code

**Problem:** VS Code Copilot can't access environment variables

**Solution:**
1. Reload VS Code window: `Cmd/Ctrl + Shift + P` → "Reload Window"
2. Make sure keys are in `~/.mcp-keys/` and `~/.bashrc` sources them
3. Check if VS Code terminal inherits shell environment

### Changes not taking effect

**Problem:** Added/removed servers but nothing changed

**Solution:**
- **Claude Code:** Start a new conversation
- **VS Code Copilot:** Reload window (`Cmd/Ctrl + Shift + P` → "Reload Window")

## 📊 Best Practices

### 1. Minimize Global Auto-Load
Keep `~/.claude/settings.json` minimal. Only auto-load MCP servers you use in EVERY project.

### 2. Load Per-Project
Use `/mcp:add` to configure servers per-project based on actual needs.

### 3. Clear When Not Needed
Use `/mcp:clear` during coding-heavy sessions to maximize context window.

### 4. Track Usage
Run `/mcp:inventory` periodically to see which projects use which servers/keys.

### 5. Never Commit API Keys
- Always use `${VARIABLE}` placeholders in `.mcp.json` and `.vscode/mcp.json`
- Add `.mcp-keys/` to `.gitignore` (though it's in your home directory, not project)
- Commit `.env.example` to show required keys (without actual values)
- Commit `.api-keys-inventory.example.md` as a template

### 6. Organized Key Categories
Keep keys organized by purpose:
- `standard.env` - Common services everyone uses
- `remote-servers.env` - Server URLs (non-sensitive but important)
- `local-dev.env` - Development API keys
- `databases.env` - Database credentials

## 🆘 Support

**View available commands:**
```bash
ls ~/.claude/commands/mcp/
```

**Read command documentation:**
```bash
cat ~/.claude/commands/mcp/add.md
```

**Check registry contents:**
```bash
cat ~/.claude/mcp-servers-registry.json | jq '.servers | keys'
```

**Verify keys are loaded:**
```bash
env | grep -E "(GITHUB_TOKEN|POSTMAN_API_KEY|SIGNALHIRE)"
```

## 🔗 Related Documentation

- [MCP Official Docs](https://modelcontextprotocol.io)
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [VS Code Copilot Integration](https://code.visualstudio.com/docs/copilot)
