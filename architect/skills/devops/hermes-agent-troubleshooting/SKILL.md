---
name: hermes-agent-troubleshooting
description: Troubleshoot common Hermes agent module and config errors after upstream updates
---

# Hermes Agent Troubleshooting

## ModuleNotFoundError on startup

**Symptom:** Gateway fails with `ModuleNotFoundError: No module named 'agent.XYZ'`

**Likely cause:** Upstream removed a module but stale `.pyc` cache and/or profile configs still reference it.

**Fix:**
1. Search for the module name in profile configs:
   ```bash
   grep -rn "smart_model_routing" ~/.hermes/profiles/*/config.yaml
   ```
2. Remove or comment out the stale key from affected profiles.
3. Delete stale bytecode:
   ```bash
   find ~/.hermes -path "*/__pycache__/*" -name "*.pyc" | xargs rm -f
   ```
4. Restart the affected gateway process.
5. Verify:
   ```bash
   ~/.hermes/scripts/gateway.sh -p <profile> 2>&1 | head -20
   ```

**Historical example:** `agent.smart_model_routing` was removed in commit `424e9f36` but the config key persisted in all 5 default profiles (invest, architect, assistant, engineer, research).