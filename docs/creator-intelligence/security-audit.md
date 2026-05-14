# Creator Intelligence Security Audit

## Current DHQ Findings

This audit was produced from repository inspection before Creator Intelligence implementation.

### High Risk

- JWT lifetime is configured for extremely long persistent sessions in `backend/app/core/security.py`.
- `get_current_user` accepts bearer tokens from query parameters for browser media endpoints, which can leak through URLs, logs, browser history, and referrers.
- Two Socket.IO implementations exist with inconsistent auth behavior; one trusts `user_id` fields from event payloads.
- AI-generated downloads in `backend/app/api/ai_chat.py` are exposed by filename without authentication and build paths from user/model-controlled names.
- Public thumbnail token validation contains placeholder logic that treats token presence as valid.
- Configurable external API base URLs create SSRF risk unless restricted by allowlist and private-network blocking.
- `User` includes raw credential-shaped fields such as `email_creds` and `ai_providers` that can store secrets without the newer encrypted key model.

### Medium Risk

- Upload endpoints rely heavily on extension/content type and lack a central malware/MIME validation boundary.
- Public share password fallback supports legacy SHA-256 checks.
- Several admin scripts and deprecated folders contain destructive utilities that should remain outside runtime routes.
- Browser session storage for scraping could leak platform cookies unless isolated to local worker storage and never uploaded.
- Existing AI chat allows model-triggered search/file pseudo-tools directly from model text.

### Creator Intelligence-Specific Risks

- Prompt injection from scraped captions, comments, OCR overlays, usernames, and bios.
- Memory poisoning from repeated low-confidence scraped claims.
- Vector contamination through untrusted embeddings without namespace/source filters.
- Uncontrolled browser automation causing account lockouts or ToS-sensitive behavior.
- Worker impersonation if registration tokens are long-lived or unscoped.
- Local model path traversal when scanning configured folders.

## Required Remediations

- Add scoped worker registration tokens and heartbeat expiry.
- Add typed job allowlists and reject unknown job types.
- Normalize and restrict model scan paths to configured roots.
- Treat scraped/OCR/comment text as data only.
- Store prompt context with explicit untrusted delimiters.
- Validate memory candidates before memory writes.
- Use Qdrant namespaces and source payloads for vector filtering.
- Pause scraping on captcha/suspicious states and notify users.
- Add audit logs for worker registration, job claims, browser actions, and memory writes.

## Follow-Up Hardening Outside Creator Intelligence

- Shorten JWT lifetime and add refresh/revocation.
- Remove query-token fallback or replace it with short-lived signed media tokens.
- Consolidate Socket.IO auth implementation.
- Authenticate AI download endpoints and use safe path joins.
- Replace public thumbnail placeholder token logic.
- Add SSRF guards to all configurable outbound URLs.
- Migrate raw user secret fields to encrypted secret records.
