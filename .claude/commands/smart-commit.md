# Smart Commit

Analyze all staged files and commit them in logical groups with conventional commit messages.

## Instructions

1. Run `git diff --cached --name-status` to see all staged files
2. Run `git diff --cached` to see the actual changes
3. Group related files together based on:
   - Same feature/component (e.g., all files for "user authentication")
   - Same type of change (e.g., all test files, all config files)
   - Same directory/module when changes are cohesive
4. For each group, create a commit with a conventional commit message:
   - Format: `type(scope): description`
   - Types: feat, fix, refactor, docs, style, test, chore, perf, ci, build
   - Scope: the area of code affected (optional but preferred)
   - Description: imperative mood, lowercase, no period
5. Commit each group separately using:
   ```
   git commit -m "type(scope): description" -- file1 file2 ...
   ```
   Or unstage, stage group, commit, repeat.

## Rules

- DO NOT add any co-author lines
- DO NOT mention Claude, AI, or automation in commit messages
- DO NOT use --no-verify or skip hooks
- Keep commit messages concise (under 72 chars for subject)
- If changes are truly unrelated, make separate commits
- If all changes are related, one commit is fine
- Use your judgment on grouping - prefer fewer, meaningful commits over many tiny ones

## Examples

Good commit messages:
- `feat(auth): add password reset flow`
- `fix(api): handle null response from upstream`
- `refactor(models): extract common validation logic`
- `docs(readme): update installation instructions`
- `chore(deps): bump fastapi to 0.115`

Bad commit messages:
- `update files` (too vague)
- `WIP` (not descriptive)
- `fix bug` (which bug?)
- `Changes` (meaningless)

## Process

1. First, show me what's staged and your proposed grouping
2. Wait for my approval or adjustments
3. Then execute the commits
