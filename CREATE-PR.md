<!-- #ai-assisted with OCA/OpenAI Model with human supervision -->

# Create PR

This workflow prepares a local commit and PR description. Do not push or open a remote PR unless explicitly asked.

## Steps

1. Show current status and diff:

   ```bash
   git status --short
   git diff --stat
   git diff --name-status
   ```

2. Stage only specific files:

   ```bash
   git add <specific files>
   ```

3. Run validation:

   ```bash
   make validate
   ```

4. Create one focused commit:

   ```bash
   git commit -m "<concise imperative subject>"
   ```

5. Handoff branch, commit hash, files changed, validation, docs updated, risks, and PR text.

## Rules

- Do not use `git add .` unless the user explicitly asks and the file list is reviewed.
- Do not push unless the user explicitly asks.
- Do not open a remote PR unless the user explicitly asks.
- Keep one logical change per commit.
- Documentation drift is incomplete work.

## PR Description Template

```md
## Summary

- <what changed and why>

## Validation

- <commands run and results>

## Documentation

- <docs updated or not applicable>

## Risks

- <known risks, blockers, or insufficient data>
```
