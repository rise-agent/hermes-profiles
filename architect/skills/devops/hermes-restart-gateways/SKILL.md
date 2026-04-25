---
name: hermes-restart-gateways
version: 1.0
description: Restart Hermes gateway systemd services per profile. Supports all profiles, specific profiles, or status checks only.
trigger: When user asks to restart Hermes gateway, restart all gateways, restart a specific gateway profile, or check gateway status
---

# Hermes Gateway Restart

Manages the systemd user services that run Hermes gateway instances (one per profile). Each profile with messaging enabled has a `hermes-gateway-<profile>.service` unit.

## Service Naming

| Profile | Service Name |
|---------|-------------|
| architect | `hermes-gateway-architect.service` |
| assistant | `hermes-gateway-assistant.service` |
| engineer | `hermes-gateway-engineer.service` |
| invest | `hermes-gateway-invest.service` |
| research | `hermes-gateway-research.service` |
| default | `hermes-gateway-default.service` (if running) |
| cron | `hermes-gateway-cron.service` (if running) |

## Quick Reference

```bash
# Restart ALL running gateways
for svc in $(systemctl --user list-units --type=service --state=running | grep -o 'hermes-gateway-[^.]*\.service'); do
    echo "→ Restarting $svc"
    systemctl --user restart "$svc"
done

# Restart a specific profile gateway
systemctl --user restart hermes-gateway-architect.service

# Check all gateway statuses
for svc in $(systemctl --user list-unit-files | grep '^hermes-gateway-' | awk '{print $1}'); do
    state=$(systemctl --user is-active "$svc" 2>/dev/null || echo "unknown")
    printf "%-40s %s\n" "$svc" "$state"
done

# Check a single gateway status
systemctl --user status hermes-gateway-architect.service --no-pager

# Stop a gateway
systemctl --user stop hermes-gateway-architect.service

# Start a stopped gateway
systemctl --user start hermes-gateway-architect.service
```

## Full Restart with Verification

```bash
#!/usr/bin/env bash
# Restart all Hermes gateways and verify they come back healthy

RESTARTED=()
FAILED=()

for svc in $(systemctl --user list-units --type=service --state=running | grep -o 'hermes-gateway-[^.]*\.service'); do
    profile=${svc#hermes-gateway-}
    profile=${profile%.service}

    echo "Restarting $svc (profile: $profile)..."
    if systemctl --user restart "$svc"; then
        RESTARTED+=("$profile")
    else
        FAILED+=("$profile")
    fi
done

# Wait and verify
echo "Waiting 5s for services to settle..."
sleep 5

for profile in "${RESTARTED[@]}"; do
    svc="hermes-gateway-${profile}.service"
    state=$(systemctl --user is-active "$svc" 2>/dev/null || echo "failed")
    pid=$(systemctl --user show "$svc" --property=MainPID --value 2>/dev/null || echo "none")
    printf "%-15s %-10s PID:%s\n" "$profile" "$state" "$pid"
done

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "FAILED to restart: ${FAILED[*]}"
fi
```

## Restart After Hermes Update

When Hermes source code is updated (e.g., via `hermes-update`), all gateway processes must be restarted to load the new code:

```bash
cd ~/.hermes/hermes-agent
source venv/bin/activate

# Verify Hermes version after pull
hermes --version

# Restart all gateways
for svc in $(systemctl --user list-units --type=service --state=running | grep -o 'hermes-gateway-[^.]*\.service'); do
    systemctl --user restart "$svc"
done

# Verify all came back up
sleep 3
systemctl --user list-units --type=service --state=running | grep hermes-gateway
```

## Troubleshooting

### Gateway fails to start after restart

```bash
# Check logs
journalctl --user -u hermes-gateway-PROFILE.service -n 50 --no-pager

# Check config validity for that profile
HERMES_HOME="$HOME/.hermes/profiles/PROFILE" hermes config check

# Reset failed state (if it crashed looped)
systemctl --user reset-failed hermes-gateway-PROFILE.service
```

### Gateway dies on SSH logout / session close

```bash
# Enable linger so user services survive logout
sudo loginctl enable-linger $USER
```

### WSL2: gateway dies when terminal closes

```bash
# Requires systemd=true in /etc/wsl.conf
# Restart WSL after adding it
```

## Listing All Configured Gateways

```bash
# Active/running
systemctl --user list-units --type=service --state=running | grep hermes-gateway

# All installed (including stopped)
systemctl --user list-unit-files | grep hermes-gateway

# From CLI profile list
hermes profile list
```
