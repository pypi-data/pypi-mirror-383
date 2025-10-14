# Documentation Management System

## Purpose

Universal documentation system that works across ANY project type. Creates minimal, maintainable docs that stay updated automatically.

## Core Principle

**UPDATE, DON'T CREATE** - Keep 2-3 core docs current instead of spawning dozens of stale files.

## Standard Structure (Any Project)

```
docs/
├── README.md              # Project overview (ALWAYS update this)
├── architecture/
│   └── overview.md        # High-level design (ALWAYS update this)
└── DESIGN_SYSTEM.md       # Frontend/full-stack only (conditional)
```

## How It Works

### 1. First-Time Setup (`/docs:init`)

**Reads the spec as source of truth:**
```
.speckit/001-*/
├── spec.md           # Project specification
├── requirements.md   # Feature requirements
└── tasks.md          # Implementation tasks
```

**Creates docs from spec:**
1. Finds `.speckit/001-*/spec.md`
2. Extracts: project type, tech stack, features, architecture
3. Generates `docs/README.md` (filled from spec)
4. Generates `docs/architecture/overview.md` (filled from spec)
5. **If frontend/full-stack detected** → Copies `DESIGN_SYSTEM.md`

**Example:**
```bash
# In new project with spec
/docs:init

# Creates:
docs/
├── README.md              # Generated from spec.md
├── architecture/
│   └── overview.md        # Generated from spec architecture
└── DESIGN_SYSTEM.md       # Only if spec mentions React/Vue/etc.
```

### 2. Ongoing Maintenance (Automatic)

**Post-commit hook detects changes:**
```bash
# You commit code
git commit -m "feat: add new config option"

# Hook runs detect-doc-drift.sh
[POST-COMMIT] Checking doc drift...
⚠️  Config code changed → docs/architecture/04-configuration.md needs update

# Auto-calls command (future)
[AUTO-UPDATE] Running: /docs:update-section 04-configuration.md
✅ Updated docs/architecture/04-configuration.md
```

### 3. Manual Updates

```bash
# Update core docs (README + overview)
/docs:update-core

# Update specific section
/docs:update-section 04-configuration.md

# Validate everything
/docs:validate
```

## Commands

### Core Commands (Use These 90% of Time)

- **`/docs:init`** - First-time setup (reads spec, creates minimal structure)
- **`/docs:update-core`** - Update README + architecture/overview.md *(not built yet)*
- **`/docs:update-section <file>`** - Update specific doc *(not built yet)*

### Specialized Commands (Use Sparingly)

- **`/docs:create <type>`** - Create NEW doc (requires justification)
- **`/docs:validate [--strict]`** - Check for drift and inconsistencies
- **`/docs:consolidate`** - Merge redundant/stale docs *(not built yet)*

## Auto-Detection System

### How It Works

1. **Post-commit hook** runs after every commit
2. **`detect-doc-drift.sh`** scans changed files
3. Matches code areas to documentation files
4. **Auto-calls slash command** to update docs *(future)*

### Detection Rules

| Code Change | Triggers | Updates |
|-------------|----------|---------|
| `cli.py` config code | `/docs:update-section 04-configuration.md` | Configuration docs |
| `auto_updater.py` | `/docs:update-section 03-build-system.md` | Build system docs |
| Template structure changes | `/docs:update-core` | README + overview |
| New subsystem added | Prompts: "Update or create?" | Decision tree |
| Bug fix | Nothing | No docs needed |

### Current State

✅ **Working:**
- Post-commit hook installed
- `detect-doc-drift.sh` detects architecture drift
- `detect-docs-sprawl.sh` detects documentation sprawl (mechanical)
- `/docs:validate --check-sprawl` analyzes sprawl with AI
- Warns which docs need updating

⏳ **Not Yet Built:**
- Auto-calling update commands
- Auto-fixing sprawl issues
- Commands actually updating docs

### Sprawl Detection System

**Two-Phase Approach: Mechanical + AI**

**Phase 1: Mechanical Detection** (`detect-docs-sprawl.sh`):
- Scans commit for .md file changes
- Finds duplicate filenames across locations
- Detects README files in templates (wrong location)
- Flags docs in wrong subsystems
- Exports issues as JSON for AI analysis

**Phase 2: AI Intelligence** (`/docs:validate --check-sprawl` with subagent):
- Analyzes if detected issues are actual problems
- Determines correct location for each doc
- Distinguishes duplicates from similar names
- Provides specific fix commands
- Can auto-fix safe issues

**Example Flow:**
```bash
# 1. Commit adds doc file
git commit -m "docs: Add README to profile template"

# 2. Hook runs mechanical detection
[SPRAWL] ⚠️  README.md in templates detected
[SPRAWL] 🤖 Calling docs-validate agent...

# 3. Run AI analysis
/docs:validate --check-sprawl

# 4. AI analyzes and suggests fix
🔴 CRITICAL: templates/.multiagent/profile/README.md
   → Should be: ~/.multiagent/profile/README.md
   → Fix: mv templates/.multiagent/profile/README.md ~/.multiagent/profile/
```

## Components

### 1. Slash Commands (`~/.claude/commands/docs/`)

**Implemented:**
- ✅ `init.md` - Spec-aware initialization

**Not Yet Implemented:**
- ⏳ `update-core.md` - Update README + overview
- ⏳ `update-section.md` - Update specific file
- ⏳ `consolidate.md` - Merge redundant docs

### 2. Scripts (`scripts/`)

**Two-Script System: Framework vs Projects**

- **`detect-doc-drift.sh`** - Generic drift detection for user projects
  - **Project-type aware**: Adapts checks based on project type
  - Has `{{PROJECT_TYPE}}` placeholder (replaced during `/core:project-setup`)
  - **landing-page**: Checks src/, config/ only
  - **web-app**: Checks src/, backend/, database/
  - **ai-app**: Checks src/, backend/, database/, AI/ML code
  - Maps changed code → relevant docs
  - Prints warnings about what needs updating
  - Called by post-commit hook in user projects
  - Configured automatically during project setup

- **`detect-framework-drift.sh`** - Framework-specific drift detection
  - Only for multiagent-core repository development
  - Checks framework templates, CLI code, subsystem READMEs
  - Called by post-commit hook in framework repo only
  - Not deployed to user projects

- **`detect-docs-sprawl.sh`** - Scans for documentation sprawl (PLANNED)
  - Finds duplicate docs across locations
  - Detects README files in wrong places (templates vs actual)
  - Flags misplaced documentation
  - Calls `/docs:validate --check-sprawl` for AI analysis
  - Not yet implemented

### 3. Templates (`templates/`)

- **`DESIGN_SYSTEM.md`** - Frontend design system template
  - Only copied if spec shows frontend indicators
  - Used by frontend-developer agent
  - Maintains design consistency

### 4. Git Hook Integration

**Post-commit hook** (deployed to projects):
```bash
# Check for documentation drift (calls global script)
if [ -f "$HOME/.multiagent/documentation/scripts/detect-doc-drift.sh" ]; then
    bash "$HOME/.multiagent/documentation/scripts/detect-doc-drift.sh"
fi
```

## Spec-Aware Architecture

**Primary Source: `.speckit/001-*/spec.md`**

### Why Read the Spec?

The spec contains:
- **Project type** - Frontend, backend, full-stack, CLI
- **Tech stack** - React, FastAPI, PostgreSQL, etc.
- **Architecture decisions** - Why technologies were chosen
- **Key features** - What the project does
- **Requirements** - User stories, acceptance criteria

### What Gets Extracted

1. **For `docs/README.md`:**
   - Project name → Spec title
   - Overview → Spec summary
   - Tech stack → Spec dependencies
   - Features → Spec requirements
   - Getting started → Spec setup instructions

2. **For `docs/architecture/overview.md`:**
   - High-level design → Spec architecture section
   - Components → Spec system components
   - Technology decisions → Spec tech choices
   - Data flow → Spec architecture diagrams
   - Deployment → Spec deployment section

3. **For `docs/DESIGN_SYSTEM.md`** (conditional):
   - Created only if spec mentions:
     - React, Vue, Angular, Svelte, Next.js
     - UI/UX requirements
     - Component library
     - Design system needs

### Fallback Detection

If no spec exists (`.speckit/` not found):
- Fall back to code structure detection
- Check `package.json`, `pyproject.toml`
- Scan directories (`components/`, `routes/`)
- Less accurate, but still functional

## Design Principles

1. **Spec is Source of Truth** - Read spec first, generate docs from it
2. **Minimal by Default** - Start with 2 docs, expand only if needed
3. **Update Over Create** - Always prefer updating existing docs
4. **Auto-Detect Changes** - Hook catches drift, auto-fixes
5. **Preserve Customizations** - Never overwrite user content
6. **Project-Aware** - Create appropriate docs for project type

## File Layout

```
.multiagent/documentation/
├── README.md                    # This file - how the system works
├── scripts/
│   └── detect-doc-drift.sh      # Auto-detection script
└── templates/
    └── DESIGN_SYSTEM.md         # Frontend design system template
```

**What Was Removed (Legacy):**
- ❌ `create-structure.sh` - Not used by new system
- ❌ `AGENT_DEVELOPMENT_PROCESS.md` - Framework doc, not project doc
- ❌ `PLACEHOLDER_REFERENCE.md` - Old template system
- ❌ `ARCHITECTURE.md` template - Generated inline instead
- ❌ `CHANGELOG.md` template - Use git tags instead
- ❌ `CONTRIBUTING.md` template - Not needed for all projects
- ❌ `TROUBLESHOOTING.md` template - Add to README instead

## Workflow Examples

### New Frontend Project

```bash
# 1. Create spec
specify init 001-dashboard

# 2. Fill spec with React/Next.js requirements
vim .speckit/001-dashboard/spec.md

# 3. Initialize docs (reads spec)
/docs:init

# Creates:
docs/
├── README.md              # From spec summary
├── architecture/
│   └── overview.md        # From spec architecture
└── DESIGN_SYSTEM.md       # Because spec mentions React
```

### Update Docs After Code Change

```bash
# Make code changes
vim src/config.py

# Commit
git commit -m "feat: add new config option"

# Hook detects drift
[DOC-DRIFT] Config code changed but docs not updated
[DOC-DRIFT] Run: /docs:update-section 04-configuration.md

# Update manually (auto-update not built yet)
/docs:update-section 04-configuration.md
```

## Configuration (`~/.multiagent.json`)

```json
{
  "settings": {
    "documentation": {
      "autoUpdate": true,
      "validateOnBuild": true,
      "minimalMode": true,
      "specAware": true,
      "autoConsolidate": false
    }
  }
}
```

## Anti-Patterns (What NOT to Do)

❌ Creating 50+ markdown files that never get updated
❌ Duplicating information across multiple docs
❌ Writing docs without reading the spec first
❌ Creating new docs instead of updating existing ones
❌ Documentation without code examples
❌ Ignoring the spec and guessing project structure

## Best Practices (What TO Do)

✅ Read the spec before generating docs
✅ Update README + overview for most changes
✅ Only create new docs when spec justifies it
✅ Use spec data to keep docs accurate
✅ Include code examples in docs
✅ Let auto-detection catch drift

## Roadmap

### Phase 1: Foundation ✅
- [x] Spec-aware `/docs:init`
- [x] Auto-detection script
- [x] Post-commit hook integration
- [x] Clean minimal structure

### Phase 2: Auto-Update ⏳
- [ ] Build `/docs:update-core` command
- [ ] Build `/docs:update-section <file>` command
- [ ] Wire detection → auto-call commands
- [ ] Test on multiagent-core

### Phase 3: Intelligence 🔮
- [ ] Detect when to create vs update
- [ ] Consolidate redundant docs automatically
- [ ] Suggest doc improvements based on code
- [ ] Validate docs against spec

## Troubleshooting

### Docs are out of sync
```bash
/docs:update-core
/docs:validate
```

### Too many docs created
```bash
/docs:consolidate
```

### Auto-detection not working
```bash
# Check hook is installed
ls -la .git/hooks/post-commit

# Test detection manually
bash ~/.multiagent/documentation/scripts/detect-doc-drift.sh
```

### Docs don't match spec
```bash
# Re-run init to regenerate from spec
rm -rf docs/
/docs:init
```

## Related Systems

- **`/docs`** - Load framework/user docs for review
- **`/docs:add`** - Add user docs to `~/.claude/docs/`
- **`/docs:sync`** - Sync framework docs with commands
- **Git Hooks** - Auto-detection and validation
- **SpecKit** - Source of truth for project requirements

---

**Remember: The spec is the blueprint, docs are the map. Keep them in sync.**
