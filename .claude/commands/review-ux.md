# UX Review

Review the user experience of The Last Vigil text adventure game:

## Review Areas

### 1. Onboarding & Discovery
- How does the start screen introduce the game?
- Are commands discoverable for new players?
- Does the opening narrative hint at available actions?
- Is there a help system?

### 2. Feedback & Response
- Are player commands echoed clearly?
- Can players distinguish narrator from player text?
- Are state changes (room, inventory) announced?
- Is the typewriter effect appropriate speed?

### 3. Error Handling
- Are validation errors helpful and in-character?
- Do errors maintain narrative immersion?
- Are technical identifiers hidden from users (e.g., `technical_diagrams` vs "technical diagrams")?

### 4. Progress & Navigation
- Can players tell where they are? (StatusBar)
- Can players track their discoveries?
- Is the puzzle progression logical?
- Are locked areas explained?

### 5. Loading States
- How does the app handle LLM latency?
- Is there timeout handling?
- Are loading indicators clear?

### 6. Mobile Experience
- Are touch targets large enough (44px)?
- Does keyboard appearance handled well?
- Are quick actions discoverable?

## Game-Specific Checks

### Puzzle Flow
Check that these progressions are discoverable:
1. `technical_diagrams` → `companion_origin_record` becomes visible
2. `companion_origin_record` → `creator_journal` becomes visible
3. Talking to companion about "recognition" → `keeper_logs` visible
4. All flags needed for ending → passage unlocks

### Known UX Issues
1. Quick actions hidden on desktop
2. Object names show as `snake_case` in some errors
3. No progress indicator for story advancement
4. Desktop has no command hints (mobile has quick actions)

## Output Format
Rate each area:
- **Good**: Working well
- **Needs Work**: Has issues
- **Critical**: Blocking good UX

Provide specific recommendations with mockup text where helpful.
