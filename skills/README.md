# Claude Code Skills Directory

**Purpose**: This directory contains Agent Skills for Claude Code - modular, token-efficient capabilities that extend Claude's functionality with specialized expertise and workflows.

**Announced**: October 16, 2025 by Anthropic

**Official Documentation**: https://docs.claude.com/en/docs/claude-code/skills

---

## Table of Contents

- [What Are Agent Skills?](#what-are-agent-skills)
- [Token Efficiency](#token-efficiency)
- [How Skills Work](#how-skills-work)
- [File Structure](#file-structure)
- [Skill Storage Locations](#skill-storage-locations)
- [Creating a Skill](#creating-a-skill)
- [Best Practices](#best-practices)
- [Using Skills in This Repository](#using-skills-in-this-repository)
- [Testing and Debugging](#testing-and-debugging)
- [References](#references)

---

## What Are Agent Skills?

**Agent Skills** package expertise into discoverable capabilities within Claude Code. Each Skill consists of a `SKILL.md` file containing instructions that Claude reads when relevant, plus optional supporting files like scripts and templates.

### Key Characteristics

- **Model-Invoked**: Claude autonomously decides when to use Skills based on your request and the Skill's description (unlike slash commands, which are user-invoked)
- **Portable**: Build once, use across Claude apps, Claude Code, and the API
- **Composable**: Skills stack together - Claude automatically identifies which skills are needed and coordinates their use
- **Powerful**: Skills can include executable code for tasks where traditional programming is more reliable than token generation

### Skills vs Slash Commands

| Feature | Skills | Slash Commands |
|---------|--------|----------------|
| **Invocation** | Automatic (model-invoked) | Manual (user-invoked) |
| **Discovery** | Claude reads description | User types `/command` |
| **Token Usage** | 30-50 tokens until loaded | Full prompt loaded immediately |
| **Coordination** | Multi-skill composition | Single command execution |
| **Best For** | Specialized expertise, workflows | Structured processes, workflows |

---

## Token Efficiency

**The Innovation**: Agent Skills use a "progressive disclosure" architecture that makes them remarkably token-efficient.

### How It Works

1. **Initial Footprint**: Each Skill consumes only **30-50 tokens** until Claude determines it's relevant
2. **Lazy Loading**: Full Skill content (instructions, examples, supporting files) loads only when needed
3. **Context Management**: Claude manages the context window efficiently by reading additional files only when necessary

### Benefits

- **Scalability**: Add dozens of Skills without overwhelming the context window
- **Performance**: Claude remains fast while accessing specialized expertise
- **Cost Efficiency**: API users save tokens by loading only what's needed
- **Multi-Skill Coordination**: Multiple Skills can be active simultaneously without context explosion

### Example

```
Initial State:
- 10 Skills available
- Total token usage: 300-500 tokens (just descriptions)

Task: "Create a PowerPoint presentation about Q4 results"
- Claude identifies "PowerPoint Creation" Skill as relevant
- Loads full Skill content: +2,000 tokens
- Other 9 Skills remain dormant: still only 30-50 tokens each
- Total: ~2,500 tokens vs. ~20,000 if all Skills were fully loaded
```

---

## How Skills Work

### Discovery Process

Claude automatically discovers Skills from three sources:

1. **Personal Skills**: `~/.claude/skills/` (individual user workflows)
2. **Project Skills**: `.claude/skills/` (team-shared, checked into git)
3. **Plugin Skills**: Bundled with installed Claude Code plugins

### Activation Flow

```
User Request
    ↓
Claude analyzes task
    ↓
Compares against Skill descriptions (30-50 tokens each)
    ↓
Selects relevant Skill(s)
    ↓
Loads full SKILL.md content
    ↓
Reads supporting files if needed (progressive disclosure)
    ↓
Executes task using Skill instructions
```

### Progressive Disclosure

Claude employs a multi-tier loading strategy:

1. **Tier 1**: Skill name + description (always loaded, 30-50 tokens)
2. **Tier 2**: Main SKILL.md content (loaded when Skill is activated)
3. **Tier 3**: Supporting files (loaded only when referenced/needed)

This keeps the context window lean while maintaining access to deep expertise.

---

## File Structure

### Minimal Skill (Required Only)

```
skill-name/
└── SKILL.md          # Required: YAML frontmatter + instructions
```

### Comprehensive Skill (With Supporting Files)

```
skill-name/
├── SKILL.md          # Required: Core instructions and metadata
├── reference.md      # Optional: Detailed documentation
├── examples.md       # Optional: Concrete usage examples
├── scripts/
│   ├── helper.py     # Optional: Executable utilities
│   └── validator.sh  # Optional: Validation scripts
└── templates/
    ├── output.txt    # Optional: Output templates
    └── config.yaml   # Optional: Configuration templates
```

### SKILL.md Anatomy

```markdown
---
name: Skill Name (64 chars max)
description: What this Skill does and when to use it (1024 chars max)
allowed-tools: Read, Grep, Glob  # Optional: restrict tools
---

# Skill Name

## Instructions
Step-by-step guidance for Claude.

## Examples
Concrete usage examples.

## Supporting Resources
- See `reference.md` for detailed documentation
- See `examples.md` for more examples
- Use `scripts/helper.py` for data processing
```

---

## Skill Storage Locations

### 1. Personal Skills: `~/.claude/skills/`

**Use Case**: Individual workflows and preferences

**Characteristics**:
- Private to your user account
- Not shared with team
- Follows you across all projects

**Example**:
```bash
~/.claude/skills/
├── personal-code-style/
│   └── SKILL.md
└── my-git-workflow/
    └── SKILL.md
```

### 2. Project Skills: `.claude/skills/` (This Directory)

**Use Case**: Team-shared capabilities specific to this project

**Characteristics**:
- Checked into git (shared with team)
- Project-specific workflows
- Version-controlled alongside code

**Example**:
```bash
planning-is-prompting/.claude/skills/
├── workflow-installation/
│   └── SKILL.md
└── documentation-generation/
    └── SKILL.md
```

### 3. Plugin Skills: From Installed Plugins

**Use Case**: Community-created or vendor-provided Skills

**Characteristics**:
- Installed via Claude Code plugin system
- Managed through plugin updates
- Discoverable in plugin marketplace

**Installation**:
```bash
# Skills bundled with plugins auto-load when plugin is installed
# No manual configuration needed
```

---

## Creating a Skill

### Step 1: Choose a Location

- **Team Collaboration**: Create in `.claude/skills/` (this directory)
- **Personal Use**: Create in `~/.claude/skills/`
- **Broad Distribution**: Package as plugin

### Step 2: Create Directory and SKILL.md

```bash
# Example: Create a workflow validation Skill
mkdir -p .claude/skills/workflow-validator
cd .claude/skills/workflow-validator
```

Create `SKILL.md`:

```yaml
---
name: Validating Workflow Documents
description: Validates planning-is-prompting workflow documents for structure, cross-references, and completeness. Use when checking workflow files or before commits.
allowed-tools: Read, Grep, Glob
---

# Validating Workflow Documents

## Purpose
Ensure workflow documents follow project standards and have valid cross-references.

## Instructions

### Validation Steps
1. Check YAML frontmatter in all workflow/*.md files
2. Validate cross-references (e.g., "See planning-is-prompting → workflow/...")
3. Verify file structure matches README.md documentation
4. Check for broken internal links

### Validation Checklist
- [ ] All workflow files have proper headers
- [ ] Cross-references use canonical format
- [ ] Examples are up-to-date
- [ ] Version history is present (if applicable)

## Output Format
Provide validation results in tabular format:

| File | Status | Issues |
|------|--------|--------|
| workflow/session-end.md | ✅ PASS | None |
| workflow/p-is-p-01-planning.md | ⚠️ WARN | 2 broken links |

## Examples

### Good Cross-Reference
"See planning-is-prompting → workflow/history-management.md"

### Bad Cross-Reference
"See history-management.md" (not portable)
"See /path/to/history-management.md" (hardcoded path)
```

### Step 3: Add Supporting Files (Optional)

```bash
# Add validation script
mkdir scripts
cat > scripts/check-links.sh << 'EOF'
#!/bin/bash
# Validate all internal links in workflow/*.md files
find workflow/ -name "*.md" -exec grep -H "→ workflow/" {} \;
EOF
chmod +x scripts/check-links.sh
```

### Step 4: Test the Skill

1. Restart Claude Code (Skills load at startup)
2. Ask: "What Skills are available?"
3. Trigger the Skill: "Validate the workflow documents"
4. Verify Claude uses your Skill (check for description matching)

---

## Best Practices

### 1. Write Clear, Specific Descriptions

**Good**:
```yaml
description: Analyzes Excel spreadsheets, creates pivot tables, and generates charts. Use when working with .xlsx files or when user mentions spreadsheet analysis.
```

**Bad**:
```yaml
description: For files.
```

The description is critical for discovery - it helps Claude select the right Skill from many options.

### 2. Keep Skills Focused

**One Skill = One Capability**

Instead of:
- ❌ "Document Processing" (too broad)

Create separate Skills:
- ✅ "Processing Excel Spreadsheets"
- ✅ "Generating PowerPoint Presentations"
- ✅ "Analyzing PDF Reports"

### 3. Use Progressive Disclosure

Keep `SKILL.md` under **500 lines**. Structure additional content in separate files:

**Pattern 1: High-level guide with references**
```markdown
# Core instructions here (< 500 lines)

For detailed examples, see `examples.md`
For API reference, see `reference.md`
```

**Pattern 2: Domain-specific organization**
```
skill-name/
├── SKILL.md              # Overview + common workflows
├── advanced-features.md  # Deep dive content
└── troubleshooting.md    # Error handling
```

**Pattern 3: Conditional details**
```markdown
# Basic workflow (always needed)

## Advanced Options
For power users, see `advanced.md` for:
- Custom configuration
- Integration patterns
- Performance tuning
```

### 4. Match Specificity to Requirements

- **High Freedom** (text-based guidance): Flexible decisions
- **Medium Freedom** (pseudocode): Preferred patterns
- **Low Freedom** (exact scripts): Fragile operations requiring consistency

### 5. Include Concrete Examples

**Good**:
```markdown
## Example: Basic Usage
User: "Check workflow documents"
Claude: *Uses this Skill to validate all files in workflow/*

## Example: Specific File
User: "Validate p-is-p-01-planning.md"
Claude: *Uses this Skill to check single file*
```

### 6. Test Across Models

What works for Claude Opus may need more detail for Haiku. Test your Skill with:
- Claude Sonnet (balanced)
- Claude Opus (most capable)
- Claude Haiku (most efficient)

### 7. Use Tool Restrictions for Safety

```yaml
allowed-tools: Read, Grep, Glob  # Read-only Skill
```

When `allowed-tools` is specified, Claude can only use those tools without requesting permission. This is useful for:
- Read-only Skills that shouldn't modify files
- Skills with limited scope
- Security-sensitive workflows

### 8. Avoid Anti-Patterns

❌ **Don't**:
- Use Windows-style paths (`C:\path\to\file`)
- Create deeply nested file references (keep 1 level deep)
- Include time-sensitive information
- Provide excessive options without defaults
- Use vague or generic naming

✅ **Do**:
- Use forward slashes universally (`/path/to/file`)
- Keep file references shallow
- Use "deprecated patterns" sections for old methods
- Provide sensible defaults with escape hatches
- Use specific, descriptive names

---

## Using Skills in This Repository

### Adding a New Skill to This Project

1. **Create Skill directory**:
   ```bash
   mkdir -p .claude/skills/your-skill-name
   ```

2. **Create SKILL.md**:
   ```bash
   cd .claude/skills/your-skill-name
   # Create SKILL.md with YAML frontmatter and instructions
   ```

3. **Add supporting files** (optional):
   ```bash
   mkdir scripts templates
   # Add helper scripts, templates, etc.
   ```

4. **Test locally**:
   - Restart Claude Code
   - Verify Skill appears: "What Skills are available?"
   - Test activation with relevant task

5. **Commit to repository**:
   ```bash
   git add .claude/skills/your-skill-name
   git commit -m "Add [your-skill-name] Skill for [purpose]"
   git push
   ```

### Team Collaboration Workflow

**When You Add a Skill**:
1. Create Skill in `.claude/skills/`
2. Test thoroughly with various tasks
3. Document usage in Skill description
4. Commit and push to repository

**When Teammate Pulls Changes**:
1. Pull latest changes from git
2. Restart Claude Code (Skills reload at startup)
3. Skills are automatically available
4. No manual installation needed

### Version Control Best Practices

**Do Track**:
- ✅ `.claude/skills/*/SKILL.md`
- ✅ `.claude/skills/*/scripts/`
- ✅ `.claude/skills/*/templates/`
- ✅ `.claude/skills/*/reference.md`

**Don't Track** (already in root `.gitignore`):
- ❌ `.claude/settings.local.json` (user-specific)
- ❌ `.claude/cache/` (temporary)

**Pattern in Root `.gitignore`**:
```gitignore
# Exclude all .claude/ by default
.claude/*

# But include slash commands and skills
!.claude/commands/
!.claude/skills/
```

---

## Testing and Debugging

### Verify Skill Installation

Ask Claude directly:
```
"What Skills are available?"
```

Claude will display all discoverable Skills from all three sources (personal, project, plugin).

### Trigger Your Skill

Use a request matching your description:
```
# If description says: "Use when validating workflow documents"
"Validate the workflow documents"

# If description says: "Use when creating PowerPoint presentations"
"Create a PowerPoint about Q4 results"
```

### Debugging: Skill Not Activating

If Claude doesn't use your Skill, verify:

1. **Description Specificity**: Vague descriptions impede discovery
   ```yaml
   # Too vague
   description: For files.

   # Better
   description: Validates planning-is-prompting workflow documents for structure and cross-references. Use when checking workflow files.
   ```

2. **File Path Correctness**:
   - Project: `.claude/skills/skill-name/SKILL.md` (note leading dot)
   - Personal: `~/.claude/skills/skill-name/SKILL.md`

3. **YAML Syntax Validity**:
   ```yaml
   ---
   name: Skill Name
   description: Description here
   ---
   ```
   (No tabs, proper spacing, closing `---`)

4. **Restart Claude Code**: Skills load at startup, not dynamically

### Debug Mode

Run Claude Code with debug flag for error visibility:
```bash
claude-code --debug
```

Look for Skill loading errors in output.

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Skill not listed | Wrong file path | Check `.claude/skills/name/SKILL.md` |
| Skill listed but not used | Vague description | Add specific triggers to description |
| YAML parse error | Invalid syntax | Validate YAML frontmatter |
| Supporting file not found | Wrong path in SKILL.md | Use forward slashes, relative paths |

---

## References

### Official Anthropic Documentation

- **Skills Overview**: https://www.anthropic.com/news/skills
- **Claude Code Skills Guide**: https://docs.claude.com/en/docs/claude-code/skills
- **Best Practices**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices
- **API Skills Guide**: https://docs.claude.com/en/api/skills-guide
- **Quickstart Tutorial**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/quickstart

### Engineering Deep Dives

- **Agent Skills Architecture**: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Claude Code Best Practices**: https://www.anthropic.com/engineering/claude-code-best-practices

### Community Resources

- **Awesome Claude Skills**: https://github.com/travisvn/awesome-claude-skills
- **Skills Marketplace**: https://github.com/anthropics/skills (official)

### Related Planning-is-Prompting Documentation

- **INSTALLATION-GUIDE.md**: Installing workflows in new projects
- **workflow/session-end.md**: Session wrap-up workflow
- **workflow/history-management.md**: History archival strategies
- **.claude/commands/**: Slash commands (user-invoked, contrast with Skills)

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2025.10.21 | 1.0 | Initial README creation with comprehensive Skills documentation |

---

## Contributing

When adding Skills to this repository:

1. **Ensure relevance**: Skills should support planning-is-prompting workflows
2. **Test thoroughly**: Verify activation with multiple tasks
3. **Document clearly**: Description should explain when to use
4. **Follow structure**: Use progressive disclosure for complex Skills
5. **Update this README**: Add your Skill to the table below if applicable

### Skills in This Repository

| Skill Name | Directory | Purpose |
|------------|-----------|---------|
| *(None yet)* | - | Add your Skills here! |

---

**Last Updated**: 2025.10.21
**Maintained By**: Planning-is-Prompting Project
