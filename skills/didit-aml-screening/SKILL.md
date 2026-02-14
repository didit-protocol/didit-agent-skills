---
name: didit-aml-screening
description: >
  Integrate Didit AML Screening standalone API to screen individuals or companies against
  global watchlists. Use when the user wants to perform AML checks, screen against sanctions
  lists, check PEP status, detect adverse media, implement KYC/AML compliance, screen against
  OFAC/UN/EU watchlists, calculate risk scores, or perform anti-money laundering screening
  using Didit. Supports 1300+ databases, fuzzy name matching, configurable scoring weights,
  and continuous monitoring.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - DIDIT_API_KEY
    primaryEnv: DIDIT_API_KEY
    emoji: "🛡️"
    homepage: https://docs.didit.me
---

# Didit AML Screening API

## Overview

Screens individuals or companies against 1,300+ global watchlists and high-risk databases in real-time. Uses a two-score system: **Match Score** (identity confidence) and **Risk Score** (threat level).

**Key constraints:**
- `full_name` is the only **required** field
- Supports `entity_type`: `"person"` (default) or `"company"`
- Document number acts as a "Golden Key" for definitive matching
- All weight parameters must sum to 100

**Coverage:** OFAC SDN, UN, EU, HM Treasury, Interpol, FBI, 170+ national sanction lists, PEP Levels 1-4, 50,000+ adverse media sources, financial crime databases.

**Scoring system:**
1. **Match Score** (0-100): Is this the same person? → classifies hits as False Positive or Unreviewed
2. **Risk Score** (0-100): How risky is this entity? → determines final AML status

**API Reference:** https://docs.didit.me/reference/aml-screening-standalone-api

---

## Authentication

All requests require `x-api-key` header. Get your key from [Didit Business Console](https://business.didit.me) → API & Webhooks.

---

## Endpoint

```
POST https://verification.didit.me/v3/aml/
```

### Headers

| Header | Value | Required |
|---|---|---|
| `x-api-key` | Your API key | **Yes** |
| `Content-Type` | `application/json` | **Yes** |

### Body (JSON)

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `full_name` | string | **Yes** | — | Full name of person or entity |
| `date_of_birth` | string | No | — | DOB in `YYYY-MM-DD` format |
| `nationality` | string | No | — | ISO country code (alpha-2 or alpha-3) |
| `document_number` | string | No | — | ID document number ("Golden Key") |
| `entity_type` | string | No | `"person"` | `"person"` or `"company"` |
| `aml_name_weight` | integer | No | `60` | Name weight in match score (0-100) |
| `aml_dob_weight` | integer | No | `25` | DOB weight in match score (0-100) |
| `aml_country_weight` | integer | No | `15` | Country weight in match score (0-100) |
| `aml_match_score_threshold` | integer | No | `93` | Below = False Positive, at/above = Unreviewed |
| `save_api_request` | boolean | No | `true` | Save in Business Console |
| `vendor_data` | string | No | — | Your identifier for session tracking |

### Example

```python
import requests

response = requests.post(
    "https://verification.didit.me/v3/aml/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={
        "full_name": "John Smith",
        "date_of_birth": "1985-03-15",
        "nationality": "US",
        "document_number": "AB1234567",
        "entity_type": "person",
    },
)
print(response.json())
```

```typescript
const response = await fetch("https://verification.didit.me/v3/aml/", {
  method: "POST",
  headers: { "x-api-key": "YOUR_API_KEY", "Content-Type": "application/json" },
  body: JSON.stringify({
    full_name: "John Smith",
    date_of_birth: "1985-03-15",
    nationality: "US",
  }),
});
```

### Response (200 OK)

```json
{
  "request_id": "a1b2c3d4-...",
  "aml": {
    "status": "Approved",
    "total_hits": 2,
    "score": 45.5,
    "hits": [
      {
        "id": "hit-uuid",
        "caption": "John Smith",
        "match_score": 85,
        "risk_score": 45.5,
        "review_status": "False Positive",
        "datasets": ["PEP"],
        "properties": {"name": ["John Smith"], "country": ["US"]},
        "score_breakdown": {
          "name_score": 95, "name_weight": 60,
          "dob_score": 100, "dob_weight": 25,
          "country_score": 100, "country_weight": 15
        },
        "risk_view": {
          "categories": {"score": 55, "risk_level": "High"},
          "countries": {"score": 23, "risk_level": "Low"},
          "crimes": {"score": 0, "risk_level": "Low"}
        }
      }
    ],
    "screened_data": {
      "full_name": "John Smith",
      "date_of_birth": "1985-03-15",
      "nationality": "US",
      "document_number": "AB1234567"
    },
    "warnings": []
  }
}
```

---

## Match Score System

**Formula:** `(Name × W1) + (DOB × W2) + (Country × W3)`

| Component | Default Weight | Algorithm |
|---|---|---|
| Name | 60% | RapidFuzz WRatio — handles typos, word order, middle name variations |
| DOB | 25% | Exact=100%, Year-only=100%, Same year diff date=50%, Mismatch=-100% |
| Country | 15% | Exact=100%, Mismatch=-50%, Missing=0%. Auto-converts ISO codes |

**Document Number "Golden Key":**

| Scenario | Effect |
|---|---|
| Same type, same value | Override score to **100** |
| Different type or one missing | Keep base score (neutral) |
| Same type, different value | **-50 point penalty** |

**Classification:** Score < threshold (default 93) → **False Positive**. Score >= threshold → **Unreviewed**.

> When data is missing, remaining weights are re-normalized. E.g., name-only → name weight becomes 100%.

---

## Risk Score System

**Formula:** `(Country × 0.30) + (Category × 0.50) + (Criminal × 0.20)`

**Final AML Status (from highest risk score among non-FP hits):**

| Highest Risk Score | Status |
|---|---|
| Below 80 (default) | **Approved** |
| Between 80-100 | **In Review** |
| Above 100 | **Declined** |
| All False Positives | **Approved** |

**Category scores (50% weight):**

| Category | Score |
|---|---|
| Sanctions / PEP Level 1 | 100 |
| Warnings & Regulatory | 95 |
| PEP Level 2 / Insolvency | 80 |
| Adverse Media | 60 |
| PEP Level 4 / Businessperson | 55 |

---

## Status Values & Handling

| Status | Meaning | Action |
|---|---|---|
| `"Approved"` | No significant matches or all False Positives | Safe to proceed |
| `"In Review"` | Matches found with moderate risk | Manual compliance review needed |
| `"Rejected"` | High-risk matches confirmed | Block or escalate per your policy |
| `"Not Started"` | Screening not yet performed | Check for missing data |

### Error Responses

| Code | Meaning | Action |
|---|---|---|
| `400` | Invalid request body | Check `full_name` and parameter formats |
| `401` | Invalid API key | Verify `x-api-key` header |
| `403` | Insufficient credits | Check credits in Business Console |

---

## Warning Tags

| Tag | Description |
|---|---|
| `POSSIBLE_MATCH_FOUND` | Potential watchlist matches requiring review |
| `COULD_NOT_PERFORM_AML_SCREENING` | Missing KYC data. Provide full name, DOB, nationality, document number |

---

## Response Field Reference

### Hit Object

| Field | Type | Description |
|---|---|---|
| `match_score` | integer | 0-100 identity confidence score |
| `risk_score` | float | 0-100 threat level score |
| `review_status` | string | `"False Positive"`, `"Unreviewed"`, `"Confirmed Match"`, `"Inconclusive"` |
| `datasets` | array | e.g. `["Sanctions"]`, `["PEP"]`, `["Adverse Media"]` |
| `pep_matches` | array | PEP match details |
| `sanction_matches` | array | Sanction match details |
| `adverse_media_matches` | array | `{headline, summary, source_url, sentiment_score, adverse_keywords}` |
| `linked_entities` | array | Related persons/entities |
| `first_seen` / `last_seen` | string | ISO 8601 timestamps |

**Adverse media sentiment:** `-1` = slightly negative, `-2` = moderately, `-3` = highly negative.

---

## Continuous Monitoring

Available on **Pro plan**. Automatically included for all AML-screened sessions.

- **Daily automated re-screening** against updated watchlists
- New hits → session status updated to "In Review" or "Declined" based on thresholds
- **Real-time webhook notifications** on status changes
- Zero additional integration — uses same thresholds from workflow config

---

## Common Workflows

### Basic AML Check

```
1. POST /v3/aml/ → {"full_name": "John Smith", "nationality": "US"}
2. If "Approved" → no significant watchlist matches
   If "In Review" → review hits[].datasets, hits[].risk_view for details
   If "Rejected" → block user, check hits for sanctions/PEP details
```

### Comprehensive KYC + AML

```
1. POST /v3/id-verification/ → extract name, DOB, nationality, document number
2. POST /v3/aml/ → screen extracted data with all fields populated
3. More data = higher match accuracy = fewer false positives
```
