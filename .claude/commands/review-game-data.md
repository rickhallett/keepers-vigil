# Game Data Review

Review the game content and puzzle design in The Last Vigil:

## Files to Review
- `backend/data/rooms.py` - Room definitions
- `backend/data/objects.py` - Examinable objects
- `backend/data/conversations.py` - Dialogue trees and endings

## Checklist

### 1. Rooms (`rooms.py`)
- [ ] All rooms have proper exits
- [ ] Exit aliases cover natural language variations
- [ ] Locked rooms have clear requirements
- [ ] Room descriptions mention exits naturally
- [ ] Characters are placed appropriately

### 2. Objects (`objects.py`)
- [ ] All objects have base descriptions
- [ ] `requires_flag` creates logical progression
- [ ] `sets_flag` matches expected game flow
- [ ] Object aliases cover natural names
- [ ] Narrative notes guide LLM properly

### 3. Conversations (`conversations.py`)
- [ ] Traveler conversation stages flow logically
- [ ] Companion topics unlock appropriately
- [ ] All endings are reachable
- [ ] Dialogue prompts give LLM enough context

### 4. Puzzle Flow Verification

Check this critical path works:
```
1. Start in threshold
2. Go to archive
3. Examine technical_diagrams → sets found_technical_diagrams
4. Examine companion_origin_record (now visible) → sets found_companion_origin
5. Ask companion about recognition → sets companion_admitted_recognition
6. Examine keeper_logs (now visible) → sets found_keeper_logs
7. Examine creator_journal → sets found_creator_journal
8. Go to letter_room
9. Examine old_letter → sets found_old_letter
10. Talk to traveler through stages → sets traveler_identity_revealed
11. Ask companion about player → sets player_identity_revealed
12. Go to passage (now unlocked)
13. Trigger ending
```

### 5. Content Quality
- [ ] Descriptions are atmospheric and consistent
- [ ] No typos or grammatical errors
- [ ] Tone matches game aesthetic
- [ ] Hidden lore rewards exploration

## Known Issues
1. `companion_origin_record` was renamed to "Crystalline Device" - verify consistency
2. Some objects have `narrative_note` hinting at next discovery
3. Passage requires only `found_companion_origin` to unlock

## Output
Report on:
1. Data consistency and completeness
2. Puzzle progression logic
3. Content quality
4. Missing or broken connections
5. Suggested improvements
