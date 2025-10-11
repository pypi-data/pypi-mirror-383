# Documentation System Alignment

**Purpose**: Ensure the documentation management system aligns with the overall documentation hierarchy.

---

## Documentation System Overview

The `.multiagent/documentation/` system generates **user project documentation** (not framework docs).

### What This System Does

**Generates docs for USER PROJECTS** when they run `/docs:init`:

```bash
# User in their project runs:
/docs:init

# Creates in THEIR project:
docs/
├── README.md           # Project overview (filled from specs)
├── ARCHITECTURE.md     # System architecture
├── CONTRIBUTING.md     # How to contribute
├── TROUBLESHOOTING.md  # Common issues
└── CHANGELOG.md        # Version history
```

### What This System Does NOT Do

❌ Does NOT generate framework contributor docs (those live in `multiagent-core/docs/`)
❌ Does NOT touch `specs/` directories (those are Specify's domain)
❌ Does NOT maintain multiagent-core's own documentation

---

## System Components

### 1. Templates (`templates/`)

**Purpose**: Templates for USER PROJECT documentation

**Available Templates**:
- `README.template.md` - Project overview with placeholders
- `ARCHITECTURE.md` - System architecture documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `TROUBLESHOOTING.md` - Common issues and solutions
- `CHANGELOG.md` - Version history
- `DESIGN_SYSTEM.md` - UI/UX design system (for frontend projects)

**Placeholders**:
```
{{PROJECT_NAME}}
{{PROJECT_DESCRIPTION}}
{{FRONTEND_FRAMEWORK}}
{{BACKEND_FRAMEWORK}}
{{DATABASE_TYPE}}
{{GETTING_STARTED}}
{{INSTALLATION}}
{{USAGE}}
```

### 2. Bootstrap Script (`scripts/create-structure.sh`)

**Purpose**: Initialize documentation structure in user projects

**What it does**:
1. Creates `docs/` directory if missing
2. Copies `README.template.md` → `docs/README.md`
3. Seeds memory JSON files for tracking state
4. Does NOT fill placeholders (agents do that)

**When it runs**:
- During `multiagent init` in new projects
- When user runs `/docs:init` for first time

### 3. Agents

**docs-init** (`.claude/agents/docs-init.md`):
- Reads specs to understand project
- Fills placeholders in templates
- Creates additional docs based on project type
- Registers all docs in `doc-registry.json`

**docs-update** (`.claude/agents/docs-update.md`):
- Detects code changes
- Updates existing docs (non-destructive)
- Preserves user-authored content
- Logs changes to `update-history.json`

**docs-validate** (`.claude/agents/docs-validate.md`):
- Checks for unfilled placeholders
- Validates cross-document consistency
- Reports issues in `consistency-check.json`

**docs-sync** (`.claude/agents/docs-sync.md`):
- **Contributor-only** (NOT deployed to users)
- Syncs framework docs with slash commands
- Only for multiagent-core development

### 4. Memory Files (`memory/`)

**Purpose**: Track documentation state across agent invocations

**Files**:
- `template-status.json` - Which placeholders are filled
- `doc-registry.json` - What docs have been created
- `consistency-check.json` - Validation results
- `update-history.json` - Append-only change log

---

## How It Fits in Documentation Hierarchy

### User Project Flow

```
1. User creates project with multiagent init
   └─> .multiagent/documentation/ gets deployed

2. User runs /docs:init
   └─> docs-init agent:
       - Reads specs/001-*/spec.md
       - Fills templates with project-specific info
       - Creates docs/ with real content

3. User develops features
   └─> Code changes happen

4. User runs /docs:update
   └─> docs-update agent:
       - Detects new API endpoints
       - Updates ARCHITECTURE.md
       - Preserves user edits

5. User runs /docs:validate
   └─> docs-validate agent:
       - Checks for {{UNFILLED_PLACEHOLDERS}}
       - Reports inconsistencies
```

### Framework Development Flow (multiagent-core)

```
1. Contributor works on multiagent-core
   └─> Edits framework docs in multiagent-core/docs/

2. Contributor runs /docs:sync (contributor-only)
   └─> docs-sync agent:
       - Scans .claude/commands/
       - Updates .multiagent/README.md
       - Ensures docs match code

3. Changes get packaged
   └─> scripts/sync-templates.sh
       - Copies .multiagent/ → multiagent_core/templates/
       - Includes updated documentation system

4. Users get updates
   └─> pip install -U multiagent-core
       - Fresh .multiagent/documentation/ system
       - With latest templates and agents
```

---

## Alignment Checklist

### ✅ Correctly Separated

- ✅ User project docs (this system) vs framework docs (multiagent-core/docs/)
- ✅ Templates have clear placeholders for agents to fill
- ✅ Memory files track state properly
- ✅ Agents preserve user content (non-destructive updates)
- ✅ docs-sync is contributor-only (not deployed)

### ✅ Templates Are Appropriate

- ✅ README.template.md - User project overview
- ✅ ARCHITECTURE.md - User project architecture
- ✅ CONTRIBUTING.md - How to contribute to USER'S project
- ✅ TROUBLESHOOTING.md - Common issues in USER'S project
- ✅ CHANGELOG.md - USER'S project version history

### ✅ Agents Have Clear Roles

- ✅ docs-init: Create and fill initial docs
- ✅ docs-update: Maintain docs as code changes
- ✅ docs-validate: Check consistency
- ✅ docs-sync: Framework maintenance (not deployed)

### ⚠️  Potential Confusion Points

**Q**: Does this system manage multiagent-core's own docs?
**A**: NO. This system is FOR user projects. multiagent-core's docs are in `/docs/` and managed separately.

**Q**: Does this system touch specs/?
**A**: NO. This system READS specs to fill placeholders, but doesn't create or maintain specs.

**Q**: Where do feature specifications go?
**A**: `specs/` (generated by Specify), NOT in this documentation system.

---

## Design Principles

1. **Push intelligence to agents** - Templates are minimal, agents add context
2. **Non-destructive updates** - Never delete user content
3. **State tracking** - Memory files record what's been done
4. **Clear separation** - Framework docs ≠ user project docs
5. **Minimal templates** - Easy to understand and maintain

---

## Summary

**This system**: Generates and maintains documentation for **user projects**
**NOT this system**: Framework contributor docs (those are in `multiagent-core/docs/`)

**Templates**: Generic, placeholder-based
**Agents**: Read specs, fill placeholders, maintain docs
**Memory**: Track what's been created and updated

**Key insight**: This is a USER-FACING system that gets deployed to their projects. It helps THEM document THEIR code, not our framework.

---

**Last Updated**: 2025-10-08
**Status**: ✅ Properly aligned with documentation hierarchy
