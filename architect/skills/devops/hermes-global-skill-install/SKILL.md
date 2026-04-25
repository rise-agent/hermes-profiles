---
name: hermes-global-skill-install
description: >
  Install a skill across ALL Hermes profiles (global installation). Hermes has no --global flag
  for `skills install`, so each profile must be targeted individually. Sub-skills from a repo
  may not be published to the skills hub and must be manually copied.
  Use when user says "install globally", "all profiles", "every profile", or wants a skill
  available everywhere.
---

# Install a Skill Globally Across All Hermes Profiles

## Step 1: Add the Repo as a Skill Source (if from GitHub)

```bash
hermes skills tap add <owner>/<repo>
```

Example: `hermes skills tap add JuliusBrussee/caveman`

## Step 2: Search and Install the Main Skill Per-Profile

```bash
# Search for the skill
hermes skills search <query>

# Install for each profile — no --global flag exists
hermes -p architect skills install <skill-name> -y
hermes -p assistant skills install <skill-name> -y
hermes -p engineer skills install <skill-name> -y
hermes -p invest skills install <skill-name> -y
hermes -p research skills install <skill-name> -y
# etc.
```

Loop approach:
```bash
for profile in architect assistant engineer invest research; do
  hermes -p "$profile" skills install <skill-name> -y
done
```

**Note:** The default profile installs to `~/.hermes/skills/` (global dir), not a profile-specific dir:
```bash
hermes -p default skills install <skill-name> -y
```

## Step 3: Install Sub-Skills Not in the Hub

The skills hub often only publishes the main skill, not sub-skills. Check the repo's `skills/` directory.

```bash
# Clone the repo
cd /tmp && git clone --depth 1 https://github.com/<owner>/<repo>.git

# Copy sub-skills to every profile
for profile in architect assistant engineer invest research; do
  for skill in <sub-skill-1> <sub-skill-2>; do
    cp -r "/tmp/<repo>/skills/$skill" "/home/linuxuser/.hermes/profiles/$profile/skills/$skill"
  done
done

# Also copy to global dir for the default profile
for skill in <sub-skill-1> <sub-skill-2>; do
  cp -r "/tmp/<repo>/skills/$skill" "/home/linuxuser/.hermes/skills/$skill"
done
```

## Step 4: Verify

```bash
for profile in architect assistant engineer invest research; do
  echo "--- $profile ---"
  ls /home/linuxuser/.hermes/profiles/$profile/skills/ | grep -E "<pattern>"
done
echo "--- global ---"
ls /home/linuxuser/.hermes/skills/ | grep -E "<pattern>"
```

## Pitfalls

- **No --global flag** — `hermes skills install` only targets the current profile. Must loop.
- **Default profile has no directory** — installs to `~/.hermes/skills/` instead of `~/.hermes/profiles/default/skills/`.
- **Sub-skills missing from hub** — repos often publish only the main skill. Check `skills/` directory in the repo for sub-skills (e.g., caveman has caveman-commit, caveman-review, caveman-help, compress).
- **Sub-skills won't auto-update** — manually copied sub-skills are not tracked by `hermes skills update`. Re-clone and re-copy to update them.
- **Skill identifier format** — `hermes skills install` accepts short names (e.g., `caveman`) and auto-resolves to the full identifier. No need to type `skills-sh/owner/repo/skill`.
- **Confirmation prompt** — use `-y` flag to skip the "Install?" prompt, especially in loops.
