---
name: hermes-custom-provider-fix
description: Fix for custom providers (custom:chutes etc.) not appearing in Hermes model dropdown. Covers the two codepaths that must both handle custom:* providers.
version: 1.0
---

# Hermes Custom Provider Model Discovery Fix

## Problem
Custom Chutes models (or any `custom_providers` entry) don't appear in the Hermes TUI model dropdown.

## Root Cause
Two separate codepaths exist for model discovery, and both must handle `custom:*` providers:

1. **`hermes_cli/models.py` → `provider_model_ids()`** — Canonical model list per provider. Already has `custom:*` handler (lines ~1334-1353) that extracts provider name, looks up `base_url`/`api_key` from `custom_providers` config, calls `fetch_api_models()`.

2. **`hermes_cli/model_switch.py` → `list_authenticated_providers()`** — Builds the TUI picker rows. Section 4 (custom providers) was **only** showing models from the `model` field in config entries, never querying the `/v1/models` endpoint. This is the actual bug.

## Fix Applied (model_switch.py section 4)
For each `custom_providers` entry group:
1. Extract `api_key` from the entry during grouping
2. Call `fetch_api_models(api_key, base_url, timeout=6.0)` for each group
3. Merge live API models with any config-declared `model` fields (deduped)
4. Respect `max_models` cap while keeping `total_models` accurate
5. Graceful fallback: if API call fails, show only config-declared models

## Architecture Insight
`provider_model_ids()` and `list_authenticated_providers()` are **separate codepaths**. Fixes to one don't automatically propagate to the other. When adding provider type support, check BOTH functions.

## Config Format
```yaml
custom_providers:
  - name: chutes
    base_url: https://llm.chutes.ai/v1
    api_key: chutes_xxx...
```

## Verification
```bash
cd ~/.hermes/hermes-agent
python3 -c "
from hermes_cli.models import provider_model_ids
ids = provider_model_ids('custom:chutes')
print(f'{len(ids)} models found')
"
```
