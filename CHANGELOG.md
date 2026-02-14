# Changelog

All notable changes to the Didit Agent Skills collection will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-14

### Added
- **didit-sessions** (v2.0.0) — Consolidated session & workflow skill covering 11 API endpoints: create, retrieve, list, delete, update-status, generate-pdf, share, import-shared, blocklist-add, blocklist-remove, blocklist-list.
- **didit-age-estimation** (v1.0.0) — Age estimation from facial images with liveness check.
- **didit-aml-screening** (v1.0.0) — Anti-Money Laundering screening with dual-score system.
- **didit-database-validation** (v1.0.0) — Government database validation for 18 countries.
- **didit-face-search** (v1.0.0) — 1:N face search with blocklist integration.
- **didit-proof-of-address** (v1.0.0) — Address document verification with OCR and geocoding.
- **didit-webhooks** (v1.0.0) — Webhook signature verification (V2, Simple, X-Signature).
- Comprehensive test suite (`tests/test_all_skills.py`) covering all 23 API endpoints.
- ClawHub manifests (`claw.json`) for every skill.
- Documentation scraper (`scripts/scrape_docs.py`) for `docs.didit.me`.

### Changed
- **didit-email-verification** bumped to v1.2.0 — Enhanced with full response schemas, rate limit details, retry logic patterns, and expanded error handling.
- **didit-phone-verification** bumped to v1.2.0 — Added SMS/WhatsApp channel details, code expiration timing, carrier-specific notes.
- **didit-id-verification** bumped to v1.2.0 — Added common workflows section, more warning tags, full identity pipeline example.
- **didit-passive-liveness** bumped to v1.2.0 — Added 99.9% accuracy stats, blocklist face warning, configurable thresholds.
- **didit-face-match** bumped to v1.2.0 — Added score interpretation table, NO_FACE_DETECTED warning tag.
- **didit-proof-of-address** — Fixed endpoint to correct `/v3/poa/` (was `/v3/proof-of-address/`), fixed field name to `document` (was `document_image`).
- **didit-sessions** — Fixed list endpoint to `GET /v3/sessions/` (was `/v3/session/`).

### Removed
- Separate `didit-workflows`, `didit-blocklist`, and `didit-reusable-kyc` skills (consolidated into `didit-sessions`).

## [1.0.0] - 2026-02-13

### Added
- Initial release with 6 standalone API skills: id-verification, passive-liveness, face-match, email-verification, phone-verification, workflows.
- Utility scripts for email, phone, face-match, id-verification, and passive-liveness.
