# Chutes Custom Provider Workflow

## After Fix
```bash
# Select Chutes models interactively
hermes model  # Shows 36+ models now

# Switch to specific model
/model NousResearch/Hermes-4-14B

# View ranking for capability decisions
cat ~/chutes-models-ranking.md
```

## Verification the fix works:
- Model dropdown lists all Chutes models
- Interactive selection populates correctly
- Provider crossover to `custom:chutes` works seamlessly