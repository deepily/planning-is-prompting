# History Management Workflow

**Purpose**: Prevent history.md from exceeding 25,000 token limits through adaptive archival strategy that monitors token count, forecasts growth, and automatically archives when needed.

**When to use**:
- Integrated into session-end rituals (automatic health check)
- Manual invocation via `/history-management` slash command
- Proactive monitoring when approaching token limits

**Key capabilities**:
- Real-time health monitoring with velocity forecasting
- Adaptive boundary detection for natural split points
- Dual-channel notifications (CLI + notify-claude-async)
- Four operational modes (check, archive, analyze, dry-run)
- Integration with session-end workflows

---

## Design Principles

### 1. Trigger-Based Detection (Not Calendar-Based)
- Monitor token count continuously, not just at month boundaries
- Alert before hitting 25k limit (thresholds: 20k warning, 22k critical)
- Forecast based on 7-day velocity trends

### 2. Context-Aware Splitting
- Respect natural breakpoints (milestones, week boundaries, day boundaries)
- Don't split mid-session or mid-feature
- Preserve logical cohesion in archives

### 3. Intelligent Naming
- Complete month: `YYYY-MM-history.md` (if archived as single unit)
- Partial month: `YYYY-MM-DD-to-DD-history.md` (during active month splits)
- **No consolidation**: Multiple archives per month = visual indicator of high-intensity period

### 4. Metadata Preservation
- Archive files explain WHY they were created
- Link back to main history and adjacent archives
- Provide navigation context and achievement summaries

### 5. Adaptive Granularity
- Target: Keep 8-12k tokens in main history.md
- Analyze token density per day to determine retention period
- Typical: 7-14 days of recent history
- Minimum: 5 days for context

---

## Token Thresholds & Alerts

### Severity Levels

**🚨 CRITICAL** (≥22k tokens OR breach <3 days)
- Immediate action required
- notify-claude-async priority: `urgent`
- Blocks session-end until addressed
- Recommendation: Archive immediately

**⚠️ WARNING** (≥20k tokens OR breach <7 days)
- Archive recommended soon
- notify-claude-async priority: `high`
- User decision: Archive now / Archive next session / Continue
- Recommendation: Archive within 1-2 sessions

**ℹ️ MONITOR** (breach <14 days)
- Watch closely
- notify-claude-async priority: `medium`
- No immediate action required
- Recommendation: Plan archival within next week

**✅ HEALTHY** (breach >14 days)
- No action needed
- No notification sent
- Continue normal operation

### Velocity Calculation

**Primary**: 7-day rolling average
```
velocity_7d = (current_tokens - tokens_7_days_ago) / 7
```

**Secondary**: 30-day trend (for context)
```
velocity_30d = (current_tokens - tokens_30_days_ago) / 30
```

**Forecast**:
```
days_until_20k = (20000 - current_tokens) / velocity_7d
days_until_25k = (25000 - current_tokens) / velocity_7d
```

---

## Operational Modes

### Mode 1: Check (Default)

**Purpose**: Health check with dual notification

**Process**:
1. Count tokens (word count × 1.33 approximation)
2. Calculate 7-day and 30-day velocity
3. Forecast breach dates
4. Determine severity level
5. Display report in CLI
6. Send notify-claude-async if severity ≥ MONITOR

**Output Format**:
```
📊 History Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Size: X,XXX tokens
Velocity: XXX tok/day (7d) | XXX tok/day (30d)
Forecast: Will reach 20k in XX days
Status: [ICON] [SEVERITY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[If WARNING/CRITICAL: Recommended action]
```

**Notification Example** (if WARNING):
```bash
notify-claude-async "[PROJECT] ⚠️ History.md at 21k tokens - archive recommended" \
  --type=alert --priority=high
```

---

### Mode 2: Archive

**Purpose**: Execute adaptive archival split

**Process**:

**Step 1: Analyze Content**
- Read current history.md
- Identify session boundaries
- Map token density by date
- Calculate adaptive retention period

**Step 2: Find Split Point**
Priority order for boundary detection:
1. **Most recent major milestone** (✅ COMPLETE, 🎯 ACHIEVEMENT markers)
2. **Most recent week boundary** (Sunday date)
3. **Most recent day boundary** with <3 sessions
4. **Token-based split** keeping last 8-12k tokens

Validation:
- Split must leave 5-14 days in main file
- If <5 days would remain: Keep 10 days instead
- Ensure logical cohesion (don't split mid-feature)

**Step 3: Preview & Confirm**
Show user:
```
📋 Proposed Archive Split
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archive: 2025-09-03-to-23-history.md
Period: Sept 3-23, 2025 (21 days)
Sessions: 38 sessions
Size: ~22,000 tokens

Retention: Sept 24-30 (7 days, ~4,600 tokens)

Split Reason: Token limit (current 26,886 tokens)
Natural Boundary: Sept 23 - Agent Migration Complete

[Preview first/last 3 lines of archive]
[Preview first/last 3 lines of retention]

Continue with archive? [y/n]
```

**Step 4: Execute Archive**
1. Create archive file with metadata
2. Write archived content
3. Trim main history.md
4. Update cross-reference links
5. Verify token reduction
6. Notify completion

**Step 5: Verification**
- Count tokens in new history.md
- Verify archive file created
- Check cross-reference links work
- Confirm token reduction meets target

---

### Mode 3: Analyze

**Purpose**: Deep trend analysis and optimization recommendations

**Process**:
1. **Session Frequency Distribution**
   - Sessions per day/week/month
   - Identify busy vs. calm periods
   - Highlight outliers

2. **Token Density Heatmap**
   - Tokens per session over time
   - Average session size by period
   - Variance analysis

3. **Heavy Session Identification**
   - Sessions >500 tokens
   - Sessions >1000 tokens
   - Candidates for session detail extraction

4. **Archive Structure Assessment**
   - Current archive count
   - Archive size distribution
   - Visual intensity indicators

5. **Velocity Trend Analysis**
   - 7-day moving average trend
   - 30-day moving average trend
   - Acceleration/deceleration detection

6. **Optimization Recommendations**
   - Suggest session detail extraction for heavy sessions
   - Recommend periodic archives for stable periods
   - Identify documentation optimization opportunities

**Output**: Markdown report with charts, tables, and actionable recommendations

---

### Mode 4: Dry-Run

**Purpose**: Simulation mode for safe testing

**Process**:
1. Run full archive analysis (as in Mode 2)
2. Show proposed split point
3. Display archive filename and metadata
4. Preview token reduction
5. Show before/after structure
6. **DO NOT execute any changes**

**Output**:
```
🧪 Dry-Run Simulation (No Changes Made)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current State:
  File: history.md
  Size: 26,886 tokens
  Sessions: 45 (Sept 3-30)

Proposed Archive:
  File: history/2025-09-03-to-23-history.md
  Period: Sept 3-23 (21 days)
  Sessions: 38
  Size: ~22,000 tokens

After Archive:
  File: history.md (trimmed)
  Period: Sept 24-30 (7 days)
  Sessions: 7
  Size: ~4,600 tokens

Token Reduction: 26,886 → 4,600 (83% reduction)

This is a simulation. Run with mode=archive to execute.
```

---

## Archive File Template

```markdown
# {Project} History - {Date Range}

> **Archive Period**: {Start Date} - {End Date}
> **Archived**: {Archive Date}
> **Reason**: {Auto-generated reason}
> **Original Size**: {X} tokens → Reduced to {Y} tokens
> **Parent Document**: [../history.md](../history.md)

This archive contains detailed session entries from {period description}, a period of {intensity level} development activity including {key themes}.

---

## {Month} {Year} Sessions ({Start}-{End})

### 🎯 Key Achievements This Period

{Auto-generated list of major milestones from session content}

---

{Archived session content}

---

## Navigation

### Archive Links
- **[Return to Main History](../history.md)** - Current active sessions
{Dynamic links to previous/next archives if they exist}

### Quick Context
This archive covers a {high/medium/low}-intensity period with:
- {X} sessions across {Y} days
- Average {Z} tokens/day
- Major milestones: {List}
```

---

## Adaptive Boundary Detection Algorithm

```
function find_optimal_split_point(history_content, current_tokens):
    target_retention = calculate_adaptive_retention(current_tokens)

    # Priority 1: Find most recent major milestone
    milestones = scan_for_markers(["✅ COMPLETE", "🎯 ACHIEVEMENT", "PHASE X COMPLETE"])
    if milestones:
        candidate = most_recent_milestone
        if validate_retention(candidate, target_retention):
            return candidate

    # Priority 2: Find most recent week boundary (Sunday)
    week_boundaries = scan_for_week_boundaries()
    if week_boundaries:
        candidate = most_recent_sunday
        if validate_retention(candidate, target_retention):
            return candidate

    # Priority 3: Find most recent day with <3 sessions
    light_days = scan_for_light_days(max_sessions=3)
    if light_days:
        candidate = most_recent_light_day
        if validate_retention(candidate, target_retention):
            return candidate

    # Priority 4: Token-based split
    return calculate_token_split(current_tokens, target_retention)

function calculate_adaptive_retention(current_tokens):
    if current_tokens >= 25000:
        return 8000  # Aggressive: keep 8k
    elif current_tokens >= 22000:
        return 10000  # Moderate: keep 10k
    else:
        return 12000  # Conservative: keep 12k

function validate_retention(split_point, target_retention):
    remaining_tokens = count_tokens_after_split(split_point)
    remaining_days = count_days_after_split(split_point)

    # Token validation
    if remaining_tokens < 3000 or remaining_tokens > 15000:
        return false

    # Time validation
    if remaining_days < 5 or remaining_days > 21:
        return false

    return true
```

---

## Integration with Session-End Workflow

### Step 0.5: History Health Check

**When**: After creating TODO list, before updating history.md

**Process**:
```
1. Invoke /history-management mode=check
2. Display health report
3. If severity >= WARNING:
   a. Pause session-end workflow
   b. Present options:
      [1] Archive now (recommended) - will take ~3-5 minutes
      [2] Archive next session - adds to TODO
      [3] Continue anyway - I'll handle manually

   c. If [1] selected:
      - Invoke /history-management mode=archive
      - Wait for completion
      - Resume session-end workflow

   d. If [2] selected:
      - Add "[PROJECT] Archive history.md" to TODO list
      - Resume session-end workflow

   e. If [3] selected:
      - Log decision
      - Resume session-end workflow

4. If severity < WARNING:
   - Continue session-end workflow normally
```

**Rationale**: Check health BEFORE adding new content that might push over limit.

---

## Project-Specific Customization

When implementing this workflow in a specific project, provide:

1. **Project Prefix**: e.g., `[LUPIN]`, `[WEBSOCKET]`, `[AUTH]`
2. **File Paths**:
   - History file: `/path/to/project/history.md`
   - Archive directory: `/path/to/project/history/`
3. **Session-End Command**: `/project-session-end` or equivalent
4. **Notification Target**: Email or communication channel
5. **Token Threshold Overrides** (optional): Custom thresholds if needed

---

## Usage Examples

### Manual Health Check
```bash
# In any project with history-management slash command
/history-management

# Explicit check mode
/history-management mode=check
```

### Create Archive
```bash
# Interactive mode with confirmation
/history-management mode=archive

# Force archive (testing)
/history-management mode=archive force-split=true
```

### Analyze Trends
```bash
# Generate comprehensive analysis report
/history-management mode=analyze
```

### Safe Testing
```bash
# See what would happen without making changes
/history-management mode=dry-run
```

### Session-End Integration
```bash
# Automatically invoked during session-end
/project-session-end
# → Runs history health check as Step 0.5
# → Prompts for archival if needed
# → Continues with normal steps
```

---

## Maintenance Commands

### Check Token Count
```bash
# Recommended: Pre-approved script with health indicators
~/.claude/scripts/get-token-count.sh history.md
# Output: Words, tokens, percentage, and health status (HEALTHY/WARNING/CRITICAL)

# Alternative: Quick manual estimate
wc -w history.md | awk '{print $1 * 1.33}'

# Full health check with velocity forecasting
/history-management mode=check
```

**Script Details**:
- Pre-approved for automatic execution (no permission prompts)
- Shows word count, estimated tokens, and percentage of 25k limit
- Color-coded health indicators (✅/⚠️/🚨)
- Fast, lightweight alternative to full health check

### Manual Archive Creation
```bash
# Extract lines for archive period
head -n 498 history.md > /tmp/history_header.md
tail -n +1554 history.md >> /tmp/history_temp.md
cp /tmp/history_temp.md history.md

# Create archive
# (Content between line 499-1553 goes to archive file)
```

### Verify Archive Structure
```bash
# List all archives
ls -lh history/*.md

# Count archives per month
ls history/ | grep "2025-09" | wc -l
# Multiple files = high-intensity month
```

---

## Troubleshooting

### Issue: Token count estimation inaccurate
**Solution**: Word count × 1.33 is approximation. Use actual token counter if available, or be conservative with thresholds.

### Issue: Split creates too-small retention
**Solution**: Algorithm validates minimum 5 days retention. Adjust `calculate_adaptive_retention()` if needed.

### Issue: Natural boundaries not found
**Solution**: Falls back to token-based split. Consider adding more milestone markers to sessions.

### Issue: Archive links broken
**Solution**: Verify relative paths in archive template. Use `../history.md` for parent, adjust for nested archives.

### Issue: Velocity forecast unreliable
**Solution**: Requires at least 7 days of history for 7-day velocity. Supplement with 30-day trend for context.

---

## Version History

**v1.0** (2025.09.30) - Initial canonical workflow
- Four operational modes
- Adaptive boundary detection
- Dual-channel notifications
- Session-end integration
- Dry-run testing mode

---

## References

- **Planning-is-Prompting Repository**: Central workflow library
- **Global CLAUDE.md**: HISTORY DOCUMENT MANAGEMENT section
- **Project Slash Commands**: Project-specific wrappers referencing this workflow
