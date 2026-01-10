# Create Pull Request

Create a GitHub pull request using the `gh` CLI with a meaningful title and body.

## Instructions

1. Run `git status` to check the current branch and if it's clean
2. Run `git log --oneline main..HEAD` (or master..HEAD) to see commits on this branch
3. Run `git diff main...HEAD --stat` to see changed files summary
4. If there are uncommitted changes, ask if the user wants to commit them first
5. Push the branch if not already pushed: `git push -u origin <branch-name>`
6. Analyze the commits and changes to create:
   - A concise PR title following conventional commits format: `type(scope): description`
   - A detailed PR body with Summary, Changes, and Test Plan sections

## PR Body Format

```markdown
## Summary

[1-3 sentences describing what this PR does and why]

### Changes

- [Bullet list of key changes]
- [Group by category if many changes]

## Test Plan

- [ ] [Checklist of testing steps]
- [ ] [Include both manual and automated testing where applicable]

## References

- [Link to related issues, specs, or docs if applicable]
```

## Rules

- DO NOT add any co-author lines
- DO NOT mention Claude, AI, automation, or "Generated with" in the PR
- DO NOT add Claude Code as a collaborator or reviewer
- Use conventional commit format for PR title
- Keep title under 72 characters
- Make the summary explain the "why", not just the "what"
- Test plan should be actionable and specific

## Process

1. First, show me the proposed PR title and body
2. Wait for my approval or adjustments
3. Then create the PR using:
   ```bash
   gh pr create --title "title here" --body "$(cat <<'EOF'
   body here
   EOF
   )"
   ```
4. Return the PR URL when done
