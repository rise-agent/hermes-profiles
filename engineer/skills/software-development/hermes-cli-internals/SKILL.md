---
name: hermes-cli-internals
description: Architecture notes for debugging and extending the Hermes CLI model discovery, provider resolution, and config system. Critical for any work on hermes_cli/ codebase.
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes-cli, model-discovery, custom-providers, architecture]
---

# Hermes CLI Internals

## Model Discovery: Two Separate Paths

**The #1 pitfall:** There are two independent model discovery systems that can get out of sync. Fixing one does NOT fix the other.

### Path 1: `provider_model_ids()` — models.py:1276
- Used by: `/model` slash command, `curated_models_for_provider()`, internal callers
- Handles `custom:*` providers: looks up named provider in `custom_providers` config, calls `fetch_api_models()` → line 1334
- Handles bare `custom`: uses `_get_custom_base_url()` + env var API keys → line 1321
- Falls back to `_PROVIDER_MODELS` static dict

### Path 2: `list_authenticated_providers()` — model_switch.py:782
- Used by: TUI picker, gateway `/model` dropdown, CLI model switcher
- Builds provider rows with `slug`, `name`, `models`, `total_models`
- Section 4 (line 1078): processes `custom_providers` config entries
- **Was missing**: live API model discovery via `fetch_api_models()` — only showed config-declared `model` field
- **Fix applied**: now calls `fetch_api_models()` for each custom provider group, merges with config models

### Rule: Always check both paths
When adding/changing model discovery for any provider:
1. Check `provider_model_ids()` in models.py
2. Check `list_authenticated_providers()` in model_switch.py
3. Ensure both return consistent results

## Provider Normalization Flow

```
User input → normalize_provider() → _PROVIDER_ALIASES lookup → canonical slug
```

- `normalize_provider()` in models.py:1171 — lowercases, looks up aliases
- `custom:*` format passes through unchanged (not in aliases dict)
- `custom_provider_slug()` in providers.py:484 — builds `"custom:<name>"` slugs from display names
- All three must agree on slug format: `custom:<lowercase-hyphenated-name>`

## Config Architecture

### Two formats for custom providers:
1. **Legacy**: `custom_providers:` list of dicts with `name`, `base_url`, `api_key`, optional `model`
2. **New**: `providers:` dict with structured provider configs
- `get_compatible_custom_providers()` in config.py merges both into a single list
- Always use this function to read custom providers, never access config keys directly

### Config loading chain:
```
config.yaml → load_config() → validate_config() → get_compatible_custom_providers()
```

## Key File Locations

| File | Purpose |
|------|---------|
| `hermes_cli/models.py` | Model catalog, `provider_model_ids()`, `normalize_provider()`, `fetch_api_models()` |
| `hermes_cli/model_switch.py` | Picker builder `list_authenticated_providers()`, `switch_model()` |
| `hermes_cli/providers.py` | `custom_provider_slug()`, `resolve_custom_provider()`, `ProviderDef` |
| `hermes_cli/config.py` | Config loading, validation, migration, `get_compatible_custom_providers()` |
| `hermes_cli/auth.py` | Credential resolution, `resolve_provider()` |

## fetch_api_models() — models.py:1855

- Thin wrapper over `probe_api_models()` — hits `/v1/models` endpoint
- Returns `list[str]` of model IDs or `None` on failure
- Timeout default: 5.0s (use 6-8s for custom providers that may be slow)
- Non-blocking pattern: `if live: merge()` — always fallback to static/config models

## Common Pitfalls

1. **Shell quoting in terminal tests**: Multi-line Python via `-c "..."` is fragile. Write a temp script instead.
2. **Custom providers without `model` field**: Config entries may only have `name`+`base_url`+`api_key`. Don't assume `model` exists.
3. **API key in config vs env vars**: `custom:*` path reads from config dict. Bare `custom` path reads from env vars (`CUSTOM_API_KEY`, `OPENAI_API_KEY`). These are different code paths.
4. **`_PROVIDER_MODELS` static fallback**: If live API fails, falls back to hardcoded dict. Custom providers won't be in this dict, so they'll show 0 models if the API call fails silently.
