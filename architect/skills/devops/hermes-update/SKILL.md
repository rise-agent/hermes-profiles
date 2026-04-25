---
name: hermes-update
version: 1.0
description: Update Hermes Agent to latest upstream, reapply the custom provider enhancement patch, and run the patch tests. Preserves the custom Chutes model display fix.
trigger: When user asks to update Hermes, pull latest changes, reapply patches, or verify patch tests after an update
---

# Hermes Agent Update

Updates the local Hermes Agent installation to the latest upstream commit and re-applies the custom provider enhancement patch (`custom:<name>` support + live `/models` probing).

## Prerequisites
- Hermes installed at `~/.hermes/hermes-agent/` (git repo)
- Custom patch at `~/.hermes/custom-provider-enhancements.patch`
- Python venv at `~/.hermes/hermes-agent/venv/`

## Quick Reference

```bash
# 1. Navigate to repo
cd ~/.hermes/hermes-agent

# 2. Check status before updating
hermes update --dry-run 2>/dev/null || echo "dry-run not supported"
git log --oneline -1
git status --short

# 3. Stash any unrelated local changes (should be none if patch is last commit)
git stash push -m "pre-update-stash-$(date +%Y%m%d-%H%M%S)"

# 4. Remove our patch commit AND discard its changes from working tree
git reset --hard HEAD~1

# 5. Pull upstream (fast-forward)
git pull --ff-only

# 6. Re-apply our patch (22 lines in models.py + 29 lines in model_switch.py + 14 tests)
git am < ~/.hermes/custom-provider-enhancements.patch

# 7. Install any new dependencies
source venv/bin/activate
pip install -e '.[dev]'

# 8. Run the patch tests (14 tests in 2 files)
python -m pytest tests/hermes_cli/test_custom_name_provider.py tests/hermes_cli/test_model_switch_custom_providers.py -v
```

## Full Update Workflow (with verification)

```bash
cd ~/.hermes/hermes-agent

# Pre-check: is our patch the last commit?
PATCH_FILES="hermes_cli/models.py hermes_cli/model_switch.py tests/hermes_cli/test_custom_name_provider.py tests/hermes_cli/test_model_switch_custom_providers.py"
git log --oneline -1 -- $PATCH_FILES

# Step 1: Remove patch commit
git reset --hard HEAD~1

# Step 2: Pull upstream
git pull --ff-only

# Step 3: Re-apply patch
git am < ~/.hermes/custom-provider-enhancements.patch

# Step 4: Install deps and test
source venv/bin/activate
pip install -e '.[dev]'
python -m pytest tests/hermes_cli/test_custom_name_provider.py tests/hermes_cli/test_model_switch_custom_providers.py -v
```

## Failure Recovery

### Patch doesn't apply cleanly (upstream conflicts)

```bash
cd ~/.hermes/hermes-agent

# Abort to clean state
git am --abort

# Option A: Manual 3-way resolution
git am --3way < ~/.hermes/custom-provider-enhancements.patch
# ...resolve conflicts in editor...
git add -A && git am --continue

# Option B: Regenerate patch from scratch
# (see skill: hermes-agent-patch)
```

### Tests fail after update

```bash
# Run patch tests with more detail
python -m pytest tests/hermes_cli/test_custom_name_provider.py tests/hermes_cli/test_model_switch_custom_providers.py -vv --tb=long

# Check if existing test needs updated mock (upstream may have changed test infra)
python -m pytest tests/hermes_cli/test_model_switch_custom_providers.py -v
```

### Fast-forward pull fails (diverged branches)

```bash
git pull --rebase  # or reset to upstream: git reset --hard origin/main
# Then re-apply patch
```

## Verify Custom Provider Still Works

```bash
# Check if custom:chutes resolves models
hermes model --provider custom:chutes 2>/dev/null || echo "Check manually"

# Or via Python
source venv/bin/activate
python -c "
from hermes_cli.models import provider_model_ids
print(provider_model_ids('custom:chutes'))
"
```

## Restart Gateways After Update

After updating, restart all gateway services so they run the new code:

```bash
for svc in $(systemctl --user list-units --type=service --state=running | grep -o 'hermes-gateway-[^.]*\.service'); do
    echo "Restarting $svc..."
    systemctl --user restart "$svc"
done
```

Or use the `hermes-restart-gateways` skill.

## What the Patch Adds (14 tests)
1. `TestCustomNameProviderModelIds` (9 tests) — `provider_model_ids()` for `custom:<name>` resolution
2. `TestCustomProviderLiveProbing` (5 tests) — Live `/models` probing in model picker
3. Mock fix for existing `test_list_groups_same_name_custom_providers_into_one_row`

## Pitfalls
- Always run tests after patching — the 14 tests catch regressions quickly
- `git am --abort` is your friend; never leave a half-applied patch
- If upstream touched `hermes_cli/models.py` or `hermes_cli/model_switch.py`, expect conflicts
- `load_config` is a deferred import — mock `hermes_cli.config.load_config` in tests, not `hermes_cli.models.load_config`
- The existing test uses `https://ollama.com/v1` for `/models` probing — must mock `fetch_api_models` for determinism
