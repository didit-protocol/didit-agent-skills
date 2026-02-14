# didit-agent-skills

**Official Didit AI Agent Skills** — 11 production-ready skills for identity verification, KYC, AML screening, biometric APIs, and session management.

Compatible with **Cursor**, **OpenClaw/ClawHub**, and any `SKILL.md`-compatible AI agent.

---

## Skills

| Skill | Version | Description |
|---|---|---|
| [`didit-sessions`](skills/didit-sessions/) | 2.0.0 | Session & workflow management — 11 endpoints (create, retrieve, list, delete, update-status, generate-pdf, share, import-shared, blocklist) |
| [`didit-id-verification`](skills/didit-id-verification/) | 1.2.0 | Identity document verification with OCR, MRZ, and NFC support |
| [`didit-passive-liveness`](skills/didit-passive-liveness/) | 1.2.0 | Passive liveness detection (99.9% accuracy, anti-spoofing) |
| [`didit-face-match`](skills/didit-face-match/) | 1.2.0 | Face comparison between two images |
| [`didit-face-search`](skills/didit-face-search/) | 1.0.0 | 1:N face search with blocklist integration |
| [`didit-age-estimation`](skills/didit-age-estimation/) | 1.0.0 | Age estimation from facial images with liveness check |
| [`didit-email-verification`](skills/didit-email-verification/) | 1.2.0 | Email OTP verification (send + check) |
| [`didit-phone-verification`](skills/didit-phone-verification/) | 1.2.0 | Phone OTP verification via SMS or WhatsApp |
| [`didit-aml-screening`](skills/didit-aml-screening/) | 1.0.0 | Anti-Money Laundering screening (sanctions, PEP, adverse media) |
| [`didit-proof-of-address`](skills/didit-proof-of-address/) | 1.0.0 | Address document verification with OCR and geocoding |
| [`didit-database-validation`](skills/didit-database-validation/) | 1.0.0 | Government database validation (18 countries) |
| | | *Webhook handling is included in `didit-sessions`* |

---

## Quick Start

### Prerequisites

- A Didit API key from [Didit Business Console](https://business.didit.me) -> API & Webhooks
- A workflow ID (for session-based flows) from Console -> Workflows

### Install for Cursor IDE

Copy all skills into your project's `.cursor/skills/` directory:

```bash
# Clone the repo
git clone https://github.com/didit-protocol/didit-agent-skills.git

# Copy skills into your project
cp -r didit-agent-skills/skills/didit-* your-project/.cursor/skills/
```

Or install globally (available in all Cursor projects):

```bash
cp -r didit-agent-skills/skills/didit-* ~/.cursor/skills/
```

### Install via ClawHub

```bash
npx clawhub@latest install didit-agent-skills
```

Or install individual skills:

```bash
npx clawhub@latest install didit-sessions
npx clawhub@latest install didit-id-verification
```

### Using with Your Agent

Once installed, your AI agent automatically picks up the skills. Just ask naturally:

- *"Create a verification session for this user"*
- *"Verify this ID document"*
- *"Check if this face is alive"*
- *"Send an email verification code"*
- *"Screen this person against AML databases"*
- *"Set up webhook signature verification"*

---

## Authentication

All Didit APIs use API key authentication via the `x-api-key` header.

```bash
export DIDIT_API_KEY="your_api_key_here"
```

Get your key: [Didit Business Console](https://business.didit.me) -> API & Webhooks

---

## Testing

Run the comprehensive test suite to verify all 23 API endpoints:

```bash
export DIDIT_API_KEY="your_api_key"
export DIDIT_WORKFLOW_ID="your_workflow_id"   # optional
python3 tests/test_all_skills.py
```

Expected output: `RESULTS: 23/23 passed, 0 failed`

---

## Repository Structure

```
didit-agent-skills/
├── README.md                  # This file
├── LICENSE                    # MIT License
├── CHANGELOG.md               # Version history
├── .clawhubignore             # ClawHub publish exclusions
├── .gitignore
├── skills/                    # All 11 skills (each is a ClawHub-publishable folder)
│   ├── didit-sessions/        # Session & workflow management (11 endpoints)
│   │   └── SKILL.md
│   ├── didit-id-verification/
│   │   ├── SKILL.md
│   │   └── scripts/verify_id.py
│   ├── didit-passive-liveness/
│   │   ├── SKILL.md
│   │   └── scripts/check_liveness.py
│   ├── didit-face-match/
│   │   ├── SKILL.md
│   │   └── scripts/match_faces.py
│   ├── didit-face-search/
│   │   └── SKILL.md
│   ├── didit-age-estimation/
│   │   └── SKILL.md
│   ├── didit-email-verification/
│   │   ├── SKILL.md
│   │   └── scripts/verify_email.py
│   ├── didit-phone-verification/
│   │   ├── SKILL.md
│   │   └── scripts/verify_phone.py
│   ├── didit-aml-screening/
│   │   └── SKILL.md
│   ├── didit-proof-of-address/
│   │   └── SKILL.md
│   ├── didit-database-validation/
│   │   └── SKILL.md
├── .cursor/skills/            # Symlinks to skills/ (auto-detected by Cursor IDE)
├── tests/
│   └── test_all_skills.py     # Full API test suite (23 endpoints)
└── scripts/
    └── scrape_docs.py         # Documentation scraper
```

Each skill folder contains a `SKILL.md` with ClawHub-compatible YAML frontmatter (`metadata.openclaw` declaring required env vars, primary credential, emoji, and homepage).

---

## API Coverage

| Category | Endpoints | Skill |
|---|---|---|
| **Sessions & Workflows** | 11 endpoints | `didit-sessions` |
| **Biometrics** | 4 endpoints | `didit-id-verification`, `didit-passive-liveness`, `didit-face-match`, `didit-face-search` |
| **Age & Identity** | 2 endpoints | `didit-age-estimation`, `didit-database-validation` |
| **Contact Verification** | 4 endpoints | `didit-email-verification`, `didit-phone-verification` |
| **Compliance** | 2 endpoints | `didit-aml-screening`, `didit-proof-of-address` |
| **Infrastructure** | Webhooks, blocklist, sharing | Included in `didit-sessions` |

**Total: 23 API endpoints tested and documented.**

---

## Publishing to ClawHub

```bash
# Install CLI
npm i -g clawhub

# Login (opens browser for GitHub OAuth)
clawhub login

# Publish each skill individually
for skill in skills/didit-*/; do
  clawhub publish "$skill" --slug "$(basename $skill)"
done

# Or use sync to auto-detect and publish all new/updated skills
clawhub sync --root ./skills --all
```

**Skill format:** Each `SKILL.md` includes `metadata.openclaw` frontmatter declaring `requires.env` (e.g. `DIDIT_API_KEY`), `primaryEnv`, `emoji`, and `homepage`. See [ClawHub skill format docs](https://clawhub.ai) for the full spec.

---

## Links

- [Didit Website](https://didit.me)
- [Didit Business Console](https://business.didit.me)
- [API Documentation](https://docs.didit.me)
- [ClawHub Registry](https://clawhub.ai)

---

## License

MIT - see [LICENSE](LICENSE) for details.
