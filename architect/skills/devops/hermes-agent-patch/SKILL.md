---
name: hermes-agent-patch
version: 1.0
description: Manages custom provider enhancement patch on top of upstream hermes-agent
trigger: When updating hermes-agent, reapplying custom patches, or debugging custom provider features
---

# Hermes Agent Custom Patch Management

Maintains a git-format patch for custom provider enhancements on top of the upstream hermes-agent repo.

## Patch Location
`~/.hermes/custom-provider-enhancements.patch`

## What the Patch Adds (purely additive, no upstream code removed)
1. **`provider_model_ids("custom:<name>")`** — Resolves named custom providers (e.g. `custom:chutes`) from config.yaml's `custom_providers` list, probes their `/models` endpoint, returns live model list. (22 lines in `hermes_cli/models.py`)
2. **Live `/models` probing in picker** — `list_authenticated_providers()` section 4 extracts `api_key` from custom_providers entries and probes live `/models` to discover models beyond config declarations. Respects `max_models`. (29 lines in `hermes_cli/model_switch.py`)
3. **Test file** — `tests/hermes_cli/test_custom_name_provider.py` (389 lines, 14 tests)
4. **Test fix** — Adds `fetch_api_models` mock to `test_list_groups_same_name_custom_providers_into_one_row` to prevent non-deterministic failures from live Ollama Cloud responses.

## How to Update Hermes Agent (after upstream changes)

```bash
cd ~/.hermes/hermes-agent

# 1. Remove our patch commit AND discard its changes from working tree
git reset --hard HEAD~1

# 2. Pull upstream (fast-forward)
git pull --ff-only

# 3. Re-apply our patch
git am < ~/.hermes/custom-provider-enhancements.patch

# 4. If the patch doesn't apply cleanly due to upstream conflicts:
#    git am --abort   # returns to clean pre-patch state
#    Then either:
#    a) Resolve manually: git am with --3way, resolve conflicts, git am --continue
#    b) Regenerate (see "Regenerating the Patch" below)
```

### Why this is better than stash & pop

If upstream touches the same lines, both `git am` and `git stash pop` will conflict. The real advantages are:

1. **Survivability**: The `.patch` file is a permanent artifact on disk. `git stash drop` or a corrupted repo loses stash entries forever. The patch file can always be re-applied to a fresh clone.
2. **Atomic rollback**: `git am --abort` returns to a guaranteed clean state. A failed `stash pop` can leave a messy half-applied working tree.
3. **Minimal surface area**: The patch is reviewed, tested (+14 new tests), and strictly additive. The old scattered unstaged changes had no test coverage and mixed intent with noise.
4. **Reproducibility**: The patch + skill can regenerate from scratch on any checkout. Stash is tied to one repo state.

## Regenerating the Patch (if upstream changes conflict)

```bash
git clone https://github.com/NousResearch/hermes-agent.git /tmp/hermes-agent
cd /tmp/hermes-agent
git config user.email "local@hermes" && git config user.name "local"

# Apply changes manually (see code blocks in SKILL.md), then:
git add -A && git commit -m "Custom provider enhancements..."
git format-patch -1 HEAD -o ~/.hermes/

# Verify on a second clone:
git clone --depth 1 https://github.com/NousResearch/hermes-agent.git /tmp/verify
cd /tmp/verify && git config user.email "l@h" && git config user.name "l"
git am < ~/.hermes/custom-provider-enhancements.patch
python3 -m venv venv && source venv/bin/activate && pip install -e '.[dev]'
python -m pytest tests/hermes_cli/test_custom_name_provider.py tests/hermes_cli/test_model_switch_custom_providers.py -v
```

## Pitfalls
- `load_config` is a deferred import from `hermes_cli.config` — must patch `hermes_cli.config.load_config` in tests, NOT `hermes_cli.models.load_config`
- The existing test `test_list_groups_same_name_custom_providers_into_one_row` uses `https://ollama.com/v1` which responds to `/models` — must mock `fetch_api_models` to return None for deterministic tests
- `max_models=0` means "no limit" in the hermes codebase — don't treat it as falsy
- Always work in /tmp for patch development — never modify the running installation directly
