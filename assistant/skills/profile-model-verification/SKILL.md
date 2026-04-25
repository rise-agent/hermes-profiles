---
name: profile-model-verification
description: Verify models configured across Hermes profiles
category: system-admin
created: 2025-04-25
---

# Profile Model Verification Script

Quick workflow to audit default models across all profiles.

## Steps

```bash
# 1. List all profiles
ls ~/.hermes/profiles/

# 2. Check each profile's model
for profile in ~/.hermes/profiles/*/; do
  if [ -f "${profile}config.yaml" ]; then
    name=$(basename "$profile")
    model=$(grep "model:" "${profile}config.yaml" | head -1 | awk '{print $2}')
    echo "$name: $model"
  fi
done

# 3. Check active profile
[ -f ~/.hermes/active_profile ] && echo "Active: $(cat ~/.hermes/active_profile)"

# 4. Compare with expected values from memory
```

## Expected Models by Profile (as of Apr 2026)
- global/none: zai-org/GLM-5.1-TEE
- architect: moonshotai/Kimi-K2.6-TEE
- engineer: zai-org/GLM-5.1-TEE
- research: zai-org/GLM-5.1-TEE
- assistant: XiaomiMiMo/MiMo-V2-Flash-TEE
- invest: XiaomiMiMo/MiMo-V2-Flash-TEE

## Pitfalls
- config.yaml structure: model is under top-level `model:` key
- Some profiles may use shared model config
- UI model override isn't reflected in config files

## Verification
- Confirm model names match Chutes API availability
- Check auxiliary vision: `auxiliary.vision` should be `Qwen/Qwen2.5-VL-32B-Instruct`
- Provider should be `Chutes` (endpoint: https://llm.chutes.ai/v1)