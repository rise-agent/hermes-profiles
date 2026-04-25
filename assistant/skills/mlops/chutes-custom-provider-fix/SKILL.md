---
name: chutes-custom-provider-fix
category: mlops
description: Fix model discovery for named custom providers like custom:chutes
created: 2026-04-21
---

# Custom Provider Model Discovery Fix

## Problem
Custom provider models (e.g., custom:chutes) don't appear in Hermes model dropdown because provider_model_ids() only handles bare "custom" format.

## Root Cause
hermes_cli/models.py functions:
- provider_model_ids(normalized) expects normalized == "custom"  
- custom:chutes becomes normalized="custom:chutes" 

## Solution
Patch hermes_cli/models.py to handle custom:* pattern:

1. Add branch to provider_model_ids():
```python
if normalized == "custom":
    # existing code block
elif normalized.startswith("custom:"):
    # Lookup custom provider by name
    provider_name = normalized.split(":")[1]
    config = load_hermes_config()
    for cp in config.get("custom_providers", []):
        if cp["name"] == provider_name:
            base_url = cp.get("base_url")
            api_key = cp.get("api_key")
            if profile_lists are enabled:
                return fetch_api_models(api_key, base_url)
            return None  # But probe() will attempt live fetching
```

2. Should also patch probe_provider_models to recognize custom:* format

## Impact
- Enables interactive model switching via `hermes model` for custom providers
- Populates dropdown with custom provider models
- Maintains existing custom provider config structure

## Test
```bash
curl -H "Authorization: Bearer [key]" https://llm.chutes.ai/v1/models
# Should show 36+ models
```

Curl verification works; provider_model_ids("custom:chutes") should now return model list.