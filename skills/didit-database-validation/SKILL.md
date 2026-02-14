---
name: didit-database-validation
description: >
  Integrate Didit Database Validation API to verify personal data against government
  databases. Use when the user wants to validate identity against government records,
  verify national ID numbers, check CPF/CURP/DNI/cedula numbers, perform identity database
  lookups, validate identity documents against official sources, or implement database
  verification for Latin American or Spanish identity documents using Didit.
  Supports 18 countries with 1x1 and 2x2 matching methods.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - DIDIT_API_KEY
    primaryEnv: DIDIT_API_KEY
    emoji: "🗄️"
    homepage: https://docs.didit.me
---

# Didit Database Validation API

## Overview

Verifies personal data and identity documents against trusted government and financial databases. Prevents synthetic identity fraud and ensures identity authenticity.

**Key constraints:**
- Requires at least the **national ID/document number** for the target country
- Coverage: **18 countries** (primarily Latin America + Spain)
- Results: `full_match`, `partial_match`, or `no_match`
- Only charged per **successful query** — no charge if insufficient data

**Matching methods:**

| Method | Description | Starting Price |
|---|---|---|
| **1x1** | Single data source validation | $0.05 |
| **2x2** | Two data sources cross-validation | $0.30 |

**API Reference:** https://docs.didit.me/reference/database-validation-api

---

## Authentication

All requests require `x-api-key` header. Get your key from [Didit Business Console](https://business.didit.me) → API & Webhooks.

---

## Endpoint

```
POST https://verification.didit.me/v3/database-validation/
```

### Headers

| Header | Value | Required |
|---|---|---|
| `x-api-key` | Your API key | **Yes** |
| `Content-Type` | `application/json` | **Yes** |

### Body (JSON)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id_number` | string | **Yes** | Universal ID number — auto-maps to correct country field |
| `first_name` | string | No | First name for matching |
| `last_name` | string | No | Last name for matching |
| `date_of_birth` | string | No | DOB in `YYYY-MM-DD` (required for some countries) |
| `issuing_state` | string | No | ISO 3166-1 alpha-3 country code |
| `save_api_request` | boolean | No | Save in Business Console |
| `vendor_data` | string | No | Your identifier for session tracking |

The `id_number` field auto-maps to the correct country-specific field:

| Country | Mapped Field | Document | Format |
|---|---|---|---|
| ARG | `document_number` | DNI | — |
| BOL | `document_number` | CI | — |
| BRA | `tax_number` | CPF | 11 digits |
| CHL | `personal_number` | RUT | — |
| COL | `personal_number` | Cedula | — |
| CRI | `personal_number` | Cedula | — |
| DOM | `personal_number` | Cedula | 11 digits |
| ECU | `personal_number` | Cedula | 10 digits |
| ESP | `personal_number` | DNI/NIE | — |
| GTM | `document_number` | DPI | — |
| HND | `document_number` | DNI | — |
| MEX | `personal_number` | CURP | 18 chars |
| PAN | `document_number` | Cedula | — |
| PER | `personal_number` | DNI | 8 digits |
| PRY | `document_number` | CI | — |
| SLV | `document_number` | DUI | — |
| URY | `personal_number` | CI | — |
| VEN | `document_number` | Cedula | — |

### Example

```python
import requests

response = requests.post(
    "https://verification.didit.me/v3/database-validation/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={
        "id_number": "12345678",
        "first_name": "Carlos",
        "last_name": "Garcia",
        "issuing_state": "PER",
    },
)
print(response.json())
```

```typescript
const response = await fetch("https://verification.didit.me/v3/database-validation/", {
  method: "POST",
  headers: { "x-api-key": "YOUR_API_KEY", "Content-Type": "application/json" },
  body: JSON.stringify({
    id_number: "12345678",
    first_name: "Carlos",
    last_name: "Garcia",
    issuing_state: "PER",
  }),
});
```

### Response (200 OK)

```json
{
  "request_id": "a1b2c3d4-...",
  "database_validation": {
    "status": "Approved",
    "match_type": "full_match",
    "issuing_state": "PER",
    "validation_type": "1x1",
    "screened_data": {
      "personal_number": "12345678",
      "first_name": "Carlos",
      "last_name": "Garcia"
    },
    "validations": {
      "full_name": "full_match",
      "identification_number": "full_match"
    }
  }
}
```

### Status Values & Handling

| Status | Meaning | Action |
|---|---|---|
| `"Approved"` | Full match against government records | Identity confirmed |
| `"Declined"` | No match found | Identity could not be verified |
| `"In Review"` | Partial match or insufficient data | Review screened_data and validations |

### Error Responses

| Code | Meaning | Action |
|---|---|---|
| `400` | Invalid request | Check ID number format for target country |
| `401` | Invalid API key | Verify `x-api-key` header |
| `403` | Insufficient credits | Top up at business.didit.me |

---

## Matching Logic

### Name Matching

| Result | Criteria |
|---|---|
| **Full Match** | Full name concatenation at **85% similarity** (Levenshtein), OR First + Last both full match |
| **Partial Match** | Any single name component full match |
| **No Match** | No component reaches 70% similarity |

> Individual name components use **70% Levenshtein threshold**. Example: "Christophel" vs "Christopher" = Full Match; "Chris" vs "Christopher" = No Match.

### 1x1 Decision

| Match Type | Name | ID Number |
|---|---|---|
| `full_match` | Full Match | Full Match |
| `partial_match` | Partial Match | Full Match |
| `no_match` | All other combinations | — |

### 2x2 Decision

Requires matching against **2 independent data sources**:

| Match Type | Condition |
|---|---|
| `full_match` | Both sources confirm name + ID |
| `partial_match` | One source confirms |
| `no_match` | Neither source confirms |

> DOB and ID number matching is **exact only** — no fuzzy matching.

---

## Warning Tags

| Tag | Description |
|---|---|
| `COULD_NOT_PERFORM_DATABASE_VALIDATION` | Missing required data — provide ID number, name, and country |
| `DATABASE_VALIDATION_PARTIAL_MATCH` | Partial match found — requires investigation |
| `DATABASE_VALIDATION_NO_MATCH` | No match found in government records |

> When `COULD_NOT_PERFORM_DATABASE_VALIDATION` fires, session goes to "In Review". Validation **auto-retriggers** once missing data is provided.

---

## Supported Countries

| Country | Method | Coverage | Required Input |
|---|---|---|---|
| Argentina | 1x1 | 95% | Document number |
| Bolivia | 1x1 | 95% | Document number + DOB |
| Brazil | 1x1 | 95% | Tax number (CPF) |
| Chile | 1x1 | 95% | Personal number (RUT) |
| Colombia | 1x1 | 95% | Document number + type |
| Costa Rica | 1x1 | 95% | Personal number |
| Dominican Republic | 1x1 | 95% | Personal number |
| Ecuador | 1x1 / 2x2 | 90-96% | Personal number |
| El Salvador | 1x1 | 95% | Document number + DOB |
| Guatemala | 1x1 | 95% | Document number |
| Honduras | 1x1 | 95% | Document number |
| Mexico | 1x1 | 95% | Personal number (CURP) |
| Panama | 1x1 | 95% | Document number + DOB |
| Paraguay | 1x1 | 95% | Document number |
| Peru | 1x1 / 2x2 | 95-99% | Personal number |
| Spain | 1x1 | 95% | Personal number + doc type + expiry |
| Uruguay | 1x1 | 95% | Personal number + DOB |
| Venezuela | 1x1 | 95% | Document number |
