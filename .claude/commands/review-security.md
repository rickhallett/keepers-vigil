# Security Review

Review security concerns for The Last Vigil:

## Review Checklist

### 1. API Security
- [ ] Check for rate limiting on `/api/command` (LLM calls are expensive)
- [ ] Verify session IDs are cryptographically secure
- [ ] Check CORS configuration in `main.py`
- [ ] Verify no sensitive data in error responses
- [ ] Check for input validation/sanitization

### 2. Session Management (`engine/state_store.py`)
- [ ] Sessions have expiration/cleanup
- [ ] Session IDs cannot be enumerated
- [ ] No session fixation vulnerabilities
- [ ] Memory limits on session storage

### 3. LLM Security
- [ ] API key not exposed in frontend
- [ ] No prompt injection vulnerabilities
- [ ] Rate limits on LLM calls
- [ ] Fallbacks don't expose internal errors

### 4. Frontend Security
- [ ] No sensitive data in localStorage
- [ ] API base URL configured properly
- [ ] No XSS vulnerabilities in narrative rendering
- [ ] CSP headers appropriate

### 5. Dependencies
- [ ] Check for known vulnerabilities: `npm audit` / `uv pip check`
- [ ] Dependencies are pinned versions
- [ ] No unnecessary dependencies

## Known Concerns
1. No rate limiting currently implemented
2. Session IDs use UUID4 (sufficient for game, not for sensitive apps)
3. CORS origins hardcoded in main.py
4. No session expiration (DoS via session creation)

## Environment Checks
- [ ] `ANTHROPIC_API_KEY` not in version control
- [ ] `.env.example` doesn't contain real values
- [ ] Production URLs use HTTPS

## Output Format
Classify findings by severity:
- **Critical**: Immediate security risk
- **High**: Should fix before public release
- **Medium**: Harden when possible
- **Low**: Defense in depth
