<p align="center">
  <strong>didit-agent-skills</strong><br>
  <em>Official AI Agent Skills for the Didit Identity Verification Platform</em>
</p>

<p align="center">
  <a href="https://didit.me">didit.me</a> · <a href="https://docs.didit.me">API Docs</a> · <a href="https://business.didit.me">Business Console</a> · <a href="https://clawhub.ai">ClawHub</a>
</p>

---

11 production-ready skills that teach AI agents how to call every Didit API — identity verification, KYC workflows, AML screening, biometric checks, and session management. Drop them into **Cursor**, install from **ClawHub**, or use with any `SKILL.md`-compatible agent.

## What's Inside

| Skill | v | What it does |
|---|---|---|
| [**didit-sessions**](skills/didit-sessions/) | 2.0.0 | The hub — create sessions, retrieve decisions, list/delete/update-status, generate PDF reports, share KYC between partners, manage blocklist. 11 API endpoints. |
| [**didit-id-verification**](skills/didit-id-verification/) | 1.2.0 | Verify passports, ID cards, driver's licenses. OCR, MRZ, NFC. 4000+ document types, 220+ countries. |
| [**didit-passive-liveness**](skills/didit-passive-liveness/) | 1.2.0 | Single-image liveness detection. 99.9% accuracy. Anti-spoofing for print, screen, and mask attacks. |
| [**didit-face-match**](skills/didit-face-match/) | 1.2.0 | Compare two faces. Returns similarity score 0–100. Selfie-to-document matching. |
| [**didit-face-search**](skills/didit-face-search/) | 1.0.0 | 1:N search across all verified sessions. Detect duplicate accounts and blocklist matches. |
| [**didit-age-estimation**](skills/didit-age-estimation/) | 1.0.0 | Estimate age from a selfie. Built-in liveness check. Configurable thresholds for age-gated services. |
| [**didit-email-verification**](skills/didit-email-verification/) | 1.2.0 | Send and check email OTP codes. Detects breached, disposable, and undeliverable addresses. |
| [**didit-phone-verification**](skills/didit-phone-verification/) | 1.2.0 | Send and check phone OTP via SMS, WhatsApp, or Telegram. Detects VoIP and disposable numbers. |
| [**didit-aml-screening**](skills/didit-aml-screening/) | 1.0.0 | Screen against 1300+ sanctions, PEP, and adverse media databases. Dual-score risk system. |
| [**didit-proof-of-address**](skills/didit-proof-of-address/) | 1.0.0 | Verify utility bills, bank statements, government documents. OCR extraction with geocoding. |
| [**didit-database-validation**](skills/didit-database-validation/) | 1.0.0 | Validate identity against government databases in 18 countries. |

> Webhook signature verification is included in the `didit-sessions` skill.

---

## Install

### Option 1: Cursor IDE (project-level)

```bash
git clone https://github.com/didit-protocol/didit-agent-skills.git
cp -r didit-agent-skills/skills/didit-* your-project/.cursor/skills/
```

### Option 2: Cursor IDE (global — all projects)

```bash
git clone https://github.com/didit-protocol/didit-agent-skills.git
cp -r didit-agent-skills/skills/didit-* ~/.cursor/skills/
```

### Option 3: ClawHub

```bash
# Install all
npx clawhub@latest install didit-sessions
npx clawhub@latest install didit-id-verification
npx clawhub@latest install didit-passive-liveness
# ... etc for each skill you need
```

### Option 4: Manual

Copy any `skills/<name>/SKILL.md` into your agent's skill directory. Each skill is self-contained.

---

## Setup

1. **Get an API key** from [Didit Business Console](https://business.didit.me) → API & Webhooks
2. **Set the environment variable:**

```bash
export DIDIT_API_KEY="your_api_key"
```

3. **(Optional)** For session/workflow skills, also set:

```bash
export DIDIT_WORKFLOW_ID="your_workflow_id"    # from Console → Workflows
export DIDIT_WEBHOOK_SECRET="your_secret"      # from Console → API & Webhooks
```

4. **Talk to your agent.** Once skills are installed, just ask naturally:

> "Create a KYC verification session for this user"
> "Verify this passport image"
> "Check if this selfie is a real person"
> "Screen John Smith against AML databases"
> "Send a verification code to user@example.com"

---

## API Endpoints Covered

| Category | Skill | Endpoints |
|---|---|---|
| Sessions & Workflows | `didit-sessions` | `POST /v3/session/`, `GET /v3/session/{id}/decision/`, `GET /v3/sessions/`, `DELETE /v3/session/{id}/delete/`, `PATCH /v3/session/{id}/update-status/`, `GET /v3/session/{id}/generate-pdf`, `POST /v3/session/{id}/share/`, `POST /v3/session/import-shared/`, `POST /v3/blocklist/add/`, `POST /v3/blocklist/remove/`, `GET /v3/blocklist/` |
| ID Verification | `didit-id-verification` | `POST /v3/id-verification/` |
| Liveness | `didit-passive-liveness` | `POST /v3/passive-liveness/` |
| Face Match | `didit-face-match` | `POST /v3/face-match/` |
| Face Search | `didit-face-search` | `POST /v3/face-search/` |
| Age Estimation | `didit-age-estimation` | `POST /v3/age-estimation/` |
| Email | `didit-email-verification` | `POST /v3/email/send/`, `POST /v3/email/check/` |
| Phone | `didit-phone-verification` | `POST /v3/phone/send/`, `POST /v3/phone/check/` |
| AML | `didit-aml-screening` | `POST /v3/aml/` |
| Proof of Address | `didit-proof-of-address` | `POST /v3/poa/` |
| Database Validation | `didit-database-validation` | `POST /v3/database-validation/` |

**23 endpoints total**, all tested.

---

## Testing

```bash
export DIDIT_API_KEY="your_key"
export DIDIT_WORKFLOW_ID="your_workflow_id"
python3 tests/test_all_skills.py
```

```
RESULTS: 23/23 passed, 0 failed
```

---

## Repo Structure

```
skills/                         ← 11 skills, each a standalone folder
├── didit-sessions/SKILL.md        (11 session/workflow/blocklist endpoints)
├── didit-id-verification/         SKILL.md + scripts/verify_id.py
├── didit-passive-liveness/        SKILL.md + scripts/check_liveness.py
├── didit-face-match/              SKILL.md + scripts/match_faces.py
├── didit-face-search/SKILL.md
├── didit-age-estimation/SKILL.md
├── didit-email-verification/      SKILL.md + scripts/verify_email.py
├── didit-phone-verification/      SKILL.md + scripts/verify_phone.py
├── didit-aml-screening/SKILL.md
├── didit-proof-of-address/SKILL.md
└── didit-database-validation/SKILL.md
tests/test_all_skills.py       ← 23-endpoint test suite
scripts/scrape_docs.py         ← docs.didit.me scraper (regenerates /docs)
```

Each `SKILL.md` contains ClawHub-compatible frontmatter:

```yaml
---
name: didit-sessions
description: >
  ...
version: 2.0.0
metadata:
  openclaw:
    requires:
      env:
        - DIDIT_API_KEY
        - DIDIT_WORKFLOW_ID
    primaryEnv: DIDIT_API_KEY
    emoji: "🔄"
    homepage: https://docs.didit.me
---
```

---

## Contributing

1. Fork the repo
2. Update or add a skill in `skills/`
3. Run `python3 tests/test_all_skills.py` to verify
4. Open a PR

---

## License

MIT — see [LICENSE](LICENSE).
