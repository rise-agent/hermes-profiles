---
name: multi-agent-communication-pattern
description: Design pattern for coordinating multi-agent (Hermes profile) workflows with minimal conversation overhead and zero wasted effort.
tags:
  - architecture
  - communication
  - multi-agent
  - discord
  - hermes
  - assistant
version: "1.0"
---

# Multi-Agent Communication Pattern: Zero-Overhead Coordination

## Context
Multi-profile Hermes team (Architect, Engineer, Research, Assistant, User) working on resource investing projects via Discord. Constraint: one active project at a time. Constraint: Assistant cannot manage Discord channels. Goal: minimize wasted effort, eliminate conversation overhead.

## Pattern

### Structure
- **Single project channel** (e.g., `#proj-copper-screen`) - all work discussion, no side channels
- **General channel** (`#general`) - user announcements, off-topic, non-project questions
- **No separate architecture channel** - reviews happen in-project with tagging

### Communication Protocol (Passive Listening > Active Checking)

#### Agent Activity (Fire-and-Forget Updates)
All agents communicate via **state posts** to project channel, never "check in" conversations:

```
@work-research: Data collected from Alpha Vantage. Key metrics: grade, depth, ownership. [Link to artifacts]

@work-engineer: MVP ready. Commit abc123. Screens 50 stocks in <2s. Blocked: API key handling.

@review-architect: Concerned about O(n²) complexity in scoring function. See lines 45-67 in main.py. 
  Recommendation: Use numpy vectorization. No action required if perf acceptable for 50 stocks.
```

#### Assistant (Passive Aggregator)
- **Monitors** project channel for `@work-_*` and `@review-architect` tags in message history
- **Never proactively pings** other agents
- **Only speaks** when:
  1. Responding to User query ("How's the project?")
  2. Identifying genuine blocker that needs user intervention
  3. Compiling status snapshot for user review
- **Status aggregation pattern**: Assistant reads tag history, compiles concise summary

#### User Interaction
- **Asynchronous-first**: All agents respond when active, no required sync meetings
- **Escalation**: Agent needs something → `@user` ping in project channel (not via Assistant)
- **Decision logging**: User finalizes decisions, posts summary to `#decisions-log` channel

### Tags (Searchable, Standardized)
- `@work-research` - Research agent activity
- `@work-engineer` - Engineer agent activity  
- `@review-architect` - Architect concerns/vetoes
- `@blocked` - Requires user decision
- `@decision` - User decision post (for logging)

### Barrier: Channel Management Limitations
**Problem**: Assistant cannot create/delete Discord channels.  
**Solution**: Manual channel creation by User for each project. Use consistent naming: `proj-<name>`, `general`.

## Pitfalls
1. **Over-communication**: Agents asking "How's it going?" wastes tokens and creates noise. Solution: Read history.

2. **All-hands channels**: Having all agents in one chat creates conflicting context windows and verbose cross-talk. Solution: Single project channel with disciplined tagging + passive monitoring.

3. **State synchronization**: If agents disconnect/reconnect, work may be duplicated. Solution: Assistant maintains lightweight state snapshot (markdown file in repo) updated via tag reads.

4. **Reverse communication**: Agent→User pings for decisions may get lost. Solution: User must monitor project channel or Assistant must explicitly call out user-blocked items.

## Quick Reference

### Workflow: New Project
1. **User** creates `#proj-<name>` manually
2. **Assistant** posts project brief template
3. **Research** works autonomously → posts `@work-research` summary with artifacts
4. **Engineer** works autonomously → posts `@work-engineer` summary with commits
5. **Architect** reviews autonomously → posts `@review-architect` concerns
6. **Assistant** monitors for `@blocked`
7. **User** reviews, makes decisions, posts to `#decisions-log`

### Workflow: Ask Assistant for Status
**User**: "What's blocking the copper screener?"  
**Assistant**: Reads `@blocked` tags in `#proj-copper-screen` since last user interaction → Compiles summary from last 10 messages tagged with any work status.

### Workflow: Architect Veto
**Architect** sees bad code → Posts `@review-architect` concern in project channel → Engineer reads and adjusts → No direct conversation required.

## State Snapshot Format (for Assistant reference)
```markdown
# Project: Copper Screener
Last updated: 2026-04-20

## Work Items
- [ ] Research: @work-research posted 3h ago, awaiting data validation
- [x] Engineer: @work-engineer posted 2h ago, MVP done
- [ ] Architect: @review-architect posted 1h ago, complexity concern raised

## Blockers
- User decision needed on API key handling (see @blocked tag)

## Next Actions
- Engineer to address architect's concern OR User to decide acceptable
- Research to validate additional data sources
```

## Implementation Checklist
- [ ] Confirm all agents understand tag convention
- [ ] User creates #proj-<name> and #architecture channels manually
- [ ] Assistant loads project channel history on query
- [ ] Engineer posts commit hashes with each `@work-engineer` update
- [ ] Architect separately saves key decisions to `#decisions-log` via user trigger