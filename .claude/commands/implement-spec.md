# Implement Spec

Implement an improvement specification in an isolated worktree and create a PR.

## Arguments

- `$ARGUMENTS` - The spec name (e.g., `imp-0005` or `imp-0005-reduce-difficulty`)

## Instructions

### 1. Validate and Locate Spec

```bash
# Find the spec file
ls docs/specs/*.spec.md | grep -i "$ARGUMENTS"
```

If not found, list available specs and ask user to clarify.

### 2. Create Worktree

```bash
source scripts/git-worktree-new.sh
git_worktree_new -n "$ARGUMENTS"
```

The worktree will be created at `../worktrees/$ARGUMENTS`

### 3. Verify Hidden Files

Check that essential hidden files were copied:

```bash
cd ../worktrees/$ARGUMENTS
ls -la | grep -E "^\."
```

If `.env` or other critical files are missing, copy them manually:

```bash
cp ../../keepers-vigil/.env* . 2>/dev/null || true
cp -r ../../keepers-vigil/.claude . 2>/dev/null || true
```

### 4. Read and Understand the Spec

Read the spec file thoroughly:
- Understand the problem statement
- Review the proposed solution
- Note the affected files
- Check implementation steps
- Review success criteria

### 5. Implement the Spec

Work in the worktree directory to implement all changes:

1. Make changes to affected files as specified
2. Follow the implementation steps in order
3. Run any necessary build/test commands to verify
4. Ensure all success criteria can be met

### 6. Commit Changes

```bash
cd ../worktrees/$ARGUMENTS
git add -A
git commit -m "feat: implement $ARGUMENTS

[Brief description of what was implemented]

Implements $ARGUMENTS from improvement specifications."
```

### 7. Create PR

Follow the `/create-pr` command process:

1. Push the branch
2. Create PR with proper format
3. Return the PR URL

## Rules

- Always work in the worktree, not the main repository
- Verify the build passes before creating PR
- Follow the spec's implementation steps precisely
- If the spec is ambiguous, ask for clarification before implementing
- Do not modify files outside the scope of the spec
- Clean up the worktree after PR is merged (user will handle this)

## Example Usage

```
/implement-spec imp-0005
/implement-spec imp-0006-optimize-response-times
```

## Output

When complete, provide:
1. Summary of changes made
2. Any deviations from the spec (with justification)
3. PR URL
4. Worktree location for reference
