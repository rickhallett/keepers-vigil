# Doublecheck

Verify that an implemented spec works correctly from a UX perspective.

## Arguments

- `$ARGUMENTS` - The spec name (e.g., `imp-0002` or `imp-0002-creator-journal-hints`)

## Instructions

### 1. Locate the Spec and Worktree

```bash
# Find the spec file
ls docs/specs/*.spec.md | grep -i "$ARGUMENTS"
```

```bash
# Check if worktree exists
ls -d ../worktrees/*$ARGUMENTS* 2>/dev/null || echo "No worktree found"
```

If no worktree exists, check if changes are on a branch in the main repo.

### 2. Read and Parse the Spec

Read the spec file and extract:
- **Problem Statement**: What issue is being solved?
- **Proposed Solution**: What changes were specified?
- **Affected Files**: Which files should have been modified?
- **Success Criteria**: How do we know it works?

### 3. Verify Code Changes

For each affected file listed in the spec:

1. Read the file in the worktree (or branch)
2. Confirm the specified changes are present
3. Check for any missing implementations

Create a checklist:
```
[ ] Change 1 from spec
[ ] Change 2 from spec
...
```

### 4. Run the Backend

Start the backend server to test the actual game flow:

```bash
cd ../worktrees/$ARGUMENTS/backend
uv run uvicorn main:app --port 8001 &
```

Wait for server to be ready:
```bash
sleep 3 && curl -s http://localhost:8001/api/health
```

### 5. Test the UX Flow

Create a new game session and simulate the user journey that exercises the changes:

```bash
# Create session
curl -s -X POST http://localhost:8001/api/new-game | jq -r '.session_id'
```

For each success criterion in the spec:
1. Execute the necessary game commands to reach the test scenario
2. Verify the expected behavior occurs
3. Document the actual vs expected results

### 6. Cleanup

Kill the test server:
```bash
pkill -f "uvicorn main:app --port 8001"
```

### 7. Generate Report

Provide a verification report with:

```markdown
## Doublecheck Report: [SPEC_NAME]

### Code Changes
| File | Expected Change | Status |
|------|-----------------|--------|
| file1.py | Description | ✅/❌ |
| file2.py | Description | ✅/❌ |

### Success Criteria
| Criterion | Test Method | Result |
|-----------|-------------|--------|
| Criterion 1 | How tested | ✅/❌ |
| Criterion 2 | How tested | ✅/❌ |

### UX Verification
- **Scenario tested**: [description]
- **Steps taken**: [list of commands]
- **Observed behavior**: [what happened]
- **Expected behavior**: [what should happen]
- **Match**: ✅/❌

### Issues Found
- [List any problems discovered]

### Verdict
[PASS/FAIL] - [Brief explanation]
```

## Rules

- Always test against the actual running game, not just code inspection
- Test the full user flow, not just isolated functions
- If the spec has multiple success criteria, test ALL of them
- Report any deviations or unexpected behaviors
- If tests fail, provide actionable suggestions for fixes

## Example Usage

```
/doublecheck imp-0002
/doublecheck imp-0005-reduce-difficulty
```

## Quick Verification (No Arguments)

If no arguments provided, attempt to detect the most recent implementation:
1. Check git log for recent `feat: implement` commits
2. Find the corresponding spec
3. Run verification on that spec
