# Hermes Profiles Backup

Profile configurations, persistent memories, custom patches, and gateway state for the [Hermes Agent](https://github.com/NousResearch/hermes-agent) instance.

## Stats

- **6 profiles**: `architect`, `assistant`, `engineer`, `invest`, `research`, `cron`
- **~316 KB** total (configs, memories, cron outputs, patch file)
- **API keys sanitized** — all `api_key` fields are empty strings; restore from your own `.env`

## What's Included

| Path | Description |
|------|-------------|
| `<profile>/config.yaml` | Profile-specific config (model, gateway, tools, display, memory, etc.) |
| `<profile>/memories/MEMORY.md` | Persistent cross-session notes |
| `<profile>/memories/USER.md` | User profile for that profile |
| `<profile>/SOUL.md` | Personality prompt |
| `<profile>/gateway_state.json` | Gateway platform configuration |
| `<profile>/channel_directory.json` | Home channel mapping |
| `<profile>/gateway.pid` | Process ID (reference only) |
| `cron/output/` | Generated research reports and equity summaries |
| `root/custom-provider-enhancements.patch` | Custom Chutes provider patch (22+29 lines + 14 tests) |
| `root/config.yaml` | Root/default configuration |
| `root/memories/` | Root-level persistent memories |

## What's **Excluded** (Secrets & Ephemeral State)

- `.env` files (API keys, tokens)
- `auth.json` / `auth.lock`
- `state.db` / `sessions/` / `logs/`
- `*.lock` files
- `cache/`, `models_dev_cache.json`
- `skills/` (backed up separately in [`hermes-skills`](https://github.com/rise-agent/hermes-skills))

## How to Restore

1. Recreate profiles:
   ```bash
   hermes profile create architect
   hermes profile create assistant
   hermes profile create engineer
   hermes profile create invest
   hermes profile create research
   hermes profile create cron
   ```

2. Copy configs and memories:
   ```bash
   for profile in architect assistant engineer invest research cron; do
       cp hermes-profiles/$profile/config.yaml ~/.hermes/profiles/$profile/
       cp -r hermes-profiles/$profile/memories/* ~/.hermes/profiles/$profile/memories/
       [ -f hermes-profiles/$profile/SOUL.md ] && \
           cp hermes-profiles/$profile/SOUL.md ~/.hermes/profiles/$profile/
   done
   ```

3. Restore root config:
   ```bash
   cp hermes-profiles/root/config.yaml ~/.hermes/config.yaml
   cp -r hermes-profiles/root/memories/* ~/.hermes/memories/
   ```

4. Set up `.env` with your API keys on each profile:
   ```bash
   for profile in architect assistant engineer invest research; do
       cp ~/.hermes/.env ~/.hermes/profiles/$profile/.env
       # Or create profile-specific .env files
   done
   ```

5. Reapply custom patch (if new install):
   ```bash
   cd ~/.hermes/hermes-agent
   git am < ~/.hermes/custom-provider-enhancements.patch
   ```

## Custom Patch

`root/custom-provider-enhancements.patch` adds:
- `provider_model_ids("custom:<name>")` — resolves named custom providers from config
- Live `/models` probing in the model picker
- 14 tests in `tests/hermes_cli/test_custom_name_provider.py`

See also: [`hermes-agent-patch` skill](https://github.com/rise-agent/hermes-skills/tree/main/devops/hermes-agent-patch)

## Companion Repo

- [`rise-agent/hermes-skills`](https://github.com/rise-agent/hermes-skills) — 92 skills across all categories
