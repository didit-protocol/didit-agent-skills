---
name: didit-sessions
description: >
  Integrate Didit Session & Workflow APIs — the central hub for managing verification sessions.
  Use when the user wants to create a verification session, set up a KYC workflow, create a
  session with a workflow_id, retrieve session results, get session decisions, list sessions,
  delete sessions, update session status, approve or decline sessions, request resubmission,
  generate PDF reports, share sessions between partners, import shared sessions, add or remove
  users from blocklist, manage blocked faces/documents/phones/emails, handle webhooks, or
  implement any end-to-end verification flow using Didit.
  Covers 11 API endpoints: create, retrieve, list, delete, update-status, generate-pdf,
  share, import-shared, blocklist-add, blocklist-remove, blocklist-list.
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

# Didit Session & Workflow APIs

## Overview

Sessions are the core unit of Didit verification. Every verification starts by creating a session linked to a **workflow** (configured in Console). The workflow defines what checks run (ID, liveness, AML, etc.) and the decision logic.

**Base URL:** `https://verification.didit.me/v3`

**Session lifecycle:**
```
Create Session → User verifies at URL → Receive webhook/poll decision → Optionally update status
```

**Rate limits:** 300 req/min per method. Session creation: 600 req/min. Decision polling: 100 req/min. On 429: check `Retry-After` header, use exponential backoff.

**API Reference:** https://docs.didit.me/reference/create-session-verification-sessions

---

## Authentication

All requests require `x-api-key` header. Get your key from [Didit Business Console](https://business.didit.me) → API & Webhooks.

---

## Session Statuses

| Status | Description | Terminal |
|---|---|---|
| `Not Started` | Created, user hasn't begun | No |
| `In Progress` | User is completing verification | No |
| `In Review` | Needs manual review | No |
| `Approved` | Verification successful | Yes |
| `Declined` | Verification failed | Yes |
| `Abandoned` | User left without completing | Yes |
| `Expired` | Session expired (default: 7 days) | Yes |
| `Resubmitted` | Steps sent back for resubmission | No |

---

## Workflow Types

Workflows are created in the **Business Console** (UI only, not via API). Each has a unique `workflow_id`.

| Template | Starts With | Use Case |
|---|---|---|
| **KYC** | ID Verification (OCR) | Full identity onboarding |
| **Adaptive Age Verification** | Selfie age estimation | Age-gated services (auto-fallback to ID if borderline) |
| **Biometric Authentication** | Liveness detection | Re-verify returning users (pass `portrait_image`) |
| **Address Verification** | Proof of Address | Residential address validation |
| **Questionnaire** | Custom questionnaire | Structured attestations and documents |

**Two build modes:**
- **Simple Mode**: Toggle features on/off from a template
- **Advanced Mode**: Visual node-based graph builder with conditional branches, parallel paths, action automation

**Available features in workflows:** ID Verification, Liveness, Face Match, NFC, AML Screening, Phone Verification, Email Verification, Proof of Address, Database Validation, IP Analysis, Age Estimation, Questionnaire.

---

## 1. Create Session

```
POST /v3/session/
```

| Header | Value | Required |
|---|---|---|
| `x-api-key` | Your API key | **Yes** |
| `Content-Type` | `application/json` | **Yes** |

### Body (JSON)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | uuid | **Yes** | Workflow ID from Console → Workflows |
| `vendor_data` | string | No | Your identifier (UUID/email) for tracking |
| `callback` | url | No | Redirect URL. Didit appends `verificationSessionId` + `status` as query params |
| `callback_method` | string | No | `"initiator"` (default), `"completer"`, or `"both"` — which device handles redirect |
| `metadata` | JSON string | No | Custom data stored with session. e.g. `{"account_id": "ABC123"}` |
| `language` | string | No | ISO 639-1 code for UI language (auto-detected if omitted) |
| `contact_details.email` | string | No | Pre-fill email for email verification step |
| `contact_details.phone` | string | No | Pre-fill phone (E.164) for phone verification step |
| `contact_details.send_notification_emails` | boolean | No | Send status update emails (default: `false`) |
| `expected_details.first_name` | string | No | Expected first name (triggers mismatch warning if different) |
| `expected_details.last_name` | string | No | Expected last name |
| `expected_details.date_of_birth` | string | No | Expected DOB (`YYYY-MM-DD`) |
| `expected_details.gender` | string | No | `"M"`, `"F"`, or `null` |
| `expected_details.nationality` | string | No | ISO 3166-1 alpha-3 (e.g. `USA`) |
| `portrait_image` | base64 | No | Reference portrait for Biometric Auth workflows (max 1MB) |

### Example

```python
import requests

response = requests.post(
    "https://verification.didit.me/v3/session/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={
        "workflow_id": "d8d2fa2d-c69c-471c-b7bc-bc71512b43ef",
        "vendor_data": "user-123",
        "callback": "https://yourapp.com/callback",
        "language": "en",
    },
)
session = response.json()
# session["url"] → send user here to verify
# session["session_token"] → use for SDK initialization
```

```typescript
const response = await fetch("https://verification.didit.me/v3/session/", {
  method: "POST",
  headers: { "x-api-key": "YOUR_API_KEY", "Content-Type": "application/json" },
  body: JSON.stringify({
    workflow_id: "d8d2fa2d-c69c-471c-b7bc-bc71512b43ef",
    vendor_data: "user-123",
    callback: "https://yourapp.com/callback",
  }),
});
const session = await response.json();
// session.url → redirect user here
```

### Response (201 Created)

```json
{
  "session_id": "11111111-2222-3333-4444-555555555555",
  "session_number": 1234,
  "session_token": "abcdef123456",
  "url": "https://verify.didit.me/session/abcdef123456",
  "vendor_data": "user-123",
  "status": "Not Started",
  "workflow_id": "d8d2fa2d-c69c-471c-b7bc-bc71512b43ef",
  "callback": "https://yourapp.com/callback"
}
```

| Error | Meaning | Action |
|---|---|---|
| `400` | Invalid workflow_id or insufficient credits | Verify workflow ID exists, check credits |
| `403` | No permission | Check API key permissions |

---

## 2. Retrieve Session (Get Decision)

```
GET /v3/session/{sessionId}/decision/
```

Returns all verification results for a completed session. Image/media URLs expire after **60 minutes**.

### Response (200 OK)

```json
{
  "session_id": "...",
  "status": "Approved",
  "features": ["ID_VERIFICATION", "LIVENESS", "FACE_MATCH", "AML"],
  "vendor_data": "user-123",
  "id_verifications": [{"status": "Approved", "document_type": "...", "first_name": "..."}],
  "liveness_checks": [{"status": "Approved", "method": "ACTIVE_3D", "score": 89.92}],
  "face_matches": [{"status": "Approved", "score": 95.5}],
  "phone_verifications": [{"status": "Approved", "full_number": "+14155552671"}],
  "email_verifications": [{"status": "Approved", "email": "user@example.com"}],
  "aml_screenings": [{"status": "Approved", "total_hits": 0}],
  "poa_verifications": [...],
  "nfc_verifications": [...],
  "ip_analyses": [...],
  "database_validations": [...],
  "reviews": [...]
}
```

---

## 3. List Sessions

```
GET /v3/sessions/
```

| Query Param | Type | Description |
|---|---|---|
| `vendor_data` | string | Filter by your identifier |
| `status` | string | Filter by status |
| `page` | integer | Page number |
| `page_size` | integer | Results per page |

### Response (200 OK)

```json
{
  "count": 42,
  "next": "https://verification.didit.me/v3/sessions/?page=2",
  "previous": null,
  "results": [
    {"session_id": "...", "session_number": 34, "status": "Approved", "vendor_data": "user-123", "created_at": "..."}
  ]
}
```

```python
response = requests.get(
    "https://verification.didit.me/v3/sessions/",
    headers={"x-api-key": "YOUR_API_KEY"},
    params={"vendor_data": "user-123", "status": "Approved"},
)
```

---

## 4. Delete Session

```
DELETE /v3/session/{sessionId}/delete/
```

Permanently deletes a session and **all associated data**. Returns `204 No Content` on success, `404` if not found.

```python
response = requests.delete(
    f"https://verification.didit.me/v3/session/{session_id}/delete/",
    headers={"x-api-key": "YOUR_API_KEY"},
)
# response.status_code == 204 → success
```

---

## 5. Update Session Status

```
PATCH /v3/session/{sessionId}/update-status/
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `new_status` | string | **Yes** | `"Approved"`, `"Declined"`, or `"Resubmitted"` |
| `comment` | string | No | Reason for status change |
| `send_email` | boolean | No | Send email notification (default: `false`) |
| `email_address` | string | No* | **Required** when `send_email` is `true` |
| `email_language` | string | No | Language for email (default: `"en"`) |
| `nodes_to_resubmit` | array | No | For Resubmitted: `[{"node_id": "feature_ocr", "feature": "OCR"}]` |

> **Resubmit:** Session must be Declined, In Review, or Abandoned. Approved steps are preserved.

```python
# Approve
requests.patch(f"https://verification.didit.me/v3/session/{session_id}/update-status/",
    headers=headers, json={"new_status": "Approved", "comment": "Manual review passed"})

# Resubmit specific steps with notification
requests.patch(f"https://verification.didit.me/v3/session/{session_id}/update-status/",
    headers=headers, json={
        "new_status": "Resubmitted",
        "nodes_to_resubmit": [{"node_id": "feature_ocr", "feature": "OCR"}],
        "send_email": True, "email_address": "user@example.com"
    })
```

---

## 6. Generate PDF Report

```
GET /v3/session/{sessionId}/generate-pdf
```

Generates a PDF verification report. Rate limited to **100 req/min** (CPU-bound).

```python
response = requests.get(
    f"https://verification.didit.me/v3/session/{session_id}/generate-pdf",
    headers={"x-api-key": "YOUR_API_KEY"},
)
# Returns PDF content or URL
```

---

## 7. Share Session

Generate a `share_token` for B2B KYC sharing. Only works for **finished sessions** (Approved, Declined, In Review).

```
POST /v3/session/{sessionId}/share/
```

```python
response = requests.post(
    f"https://verification.didit.me/v3/session/{session_id}/share/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
)
share_token = response.json()["share_token"]
# Transmit share_token to partner via your backend
```

---

## 8. Import Shared Session

Used by the **receiving partner** to import a shared verification session.

```
POST /v3/session/import-shared/
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `share_token` | string | **Yes** | Token from the sharing partner |
| `trust_review` | boolean | **Yes** | `true`: keep original status. `false`: set to "In Review" |
| `workflow_id` | string | **Yes** | Your workflow ID to associate |
| `vendor_data` | string | No | Your own user identifier |

```python
response = requests.post(
    "https://verification.didit.me/v3/session/import-shared/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={
        "share_token": "eyJhbGciOiJIUzI1NiIs...",
        "trust_review": True,
        "workflow_id": "your-workflow-uuid",
        "vendor_data": "user-789",
    },
)
```

> A session can only be imported **once** per partner application. Requires legal data sharing agreement + user consent.

---

## 9. Blocklist — Add

Block faces, documents, phones, emails from a session. Matching items auto-decline future sessions.

```
POST /v3/blocklist/add/
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `session_id` | uuid | **Yes** | — | Session to blocklist items from |
| `blocklist_face` | boolean | No | `false` | Block biometric face template |
| `blocklist_document` | boolean | No | `false` | Block document fingerprint |
| `blocklist_phone` | boolean | No | `false` | Block phone number |
| `blocklist_email` | boolean | No | `false` | Block email address |

```python
requests.post("https://verification.didit.me/v3/blocklist/add/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={"session_id": "...", "blocklist_face": True, "blocklist_document": True})
```

**Auto-decline warnings when matched:**

| Entity | Warning Tag |
|---|---|
| Face | `FACE_IN_BLOCKLIST` |
| Document | `ID_DOCUMENT_IN_BLOCKLIST` |
| Phone | `PHONE_NUMBER_IN_BLOCKLIST` |
| Email | `EMAIL_IN_BLOCKLIST` |

---

## 10. Blocklist — Remove

```
POST /v3/blocklist/remove/
```

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `session_id` | uuid | **Yes** | — | Session to unblock items from |
| `unblock_face` | boolean | No | `false` | Unblock face |
| `unblock_document` | boolean | No | `false` | Unblock document |
| `unblock_phone` | boolean | No | `false` | Unblock phone |
| `unblock_email` | boolean | No | `false` | Unblock email |

```python
requests.post("https://verification.didit.me/v3/blocklist/remove/",
    headers={"x-api-key": "YOUR_API_KEY", "Content-Type": "application/json"},
    json={"session_id": "...", "unblock_face": True})
```

---

## 11. Blocklist — List

```
GET /v3/blocklist/
```

| Query Param | Type | Description |
|---|---|---|
| `item_type` | string | Filter: `"face"`, `"document"`, `"phone"`, `"email"`. Omit for all |

---

## Error Responses (All Endpoints)

| Code | Meaning | Action |
|---|---|---|
| `400` | Invalid request body or parameters | Check required fields and formats |
| `401` | Invalid or missing API key | Verify `x-api-key` header |
| `403` | Insufficient credits or no permission | Check credits in Business Console |
| `404` | Session not found | Verify session_id |
| `429` | Rate limited | Check `Retry-After` header, exponential backoff |

---

## Common Workflows

### Basic KYC Flow

```
1. POST /v3/session/ → create session with KYC workflow_id, get URL
2. Redirect user to session URL
3. Listen for webhook OR poll GET /v3/session/{id}/decision/
4. "Approved"  → user verified
   "Declined"  → check decision, optionally resubmit
   "In Review" → manual review or auto-decide via API
```

### Programmatic Review + Blocklist

```
1. Receive webhook: status "In Review"
2. GET /v3/session/{id}/decision/ → inspect all results
3. Apply business logic
4. If fraud: PATCH → Declined + POST /v3/blocklist/add/ (block all entities)
   If legit: PATCH → Approved
```

### B2B KYC Sharing

```
Service X:
1. POST /v3/session/{id}/share/ → get share_token
2. Transmit token to Service Y via backend

Service Y:
3. POST /v3/session/import-shared/ → import with trust_review=true
4. Session imported instantly with original status
```

### Biometric Re-Authentication

```
1. Retrieve portrait_image from user's initial approved session
2. POST /v3/session/ → biometric auth workflow + portrait_image
3. User takes selfie → system matches against portrait
4. "Approved" → identity re-confirmed
```
