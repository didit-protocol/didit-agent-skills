---
name: didit-face-search
description: >
  Integrate Didit Face Search standalone API to perform 1:N facial search against all
  previously verified sessions. Use when the user wants to detect duplicate accounts,
  search for matching faces, check if a face already exists in the system, prevent
  duplicate registrations, search against blocklist, or implement facial deduplication
  using Didit. Returns ranked matches with similarity percentages.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - DIDIT_API_KEY
    primaryEnv: DIDIT_API_KEY
    emoji: "🔍"
    homepage: https://docs.didit.me
---

# Didit Face Search API (1:N)

## Overview

Compares a reference face against **all previously approved verification sessions** to detect duplicate accounts and blocklisted faces. Returns ranked matches with similarity scores.

**Key constraints:**
- Supported formats: **JPEG, PNG, WebP, TIFF**
- Maximum file size: **5MB**
- Compares against all **approved** sessions in your application
- Blocklist matches cause **automatic decline**

**Similarity score guidance:**

| Range | Interpretation |
|---|---|
| 90%+ | Strong likelihood of same person |
| 70-89% | Possible match, may need manual review |
| Below 70% | Likely different individuals |

**API Reference:** https://docs.didit.me/reference/face-search-standalone-api

---

## Authentication

All requests require `x-api-key` header. Get your key from [Didit Business Console](https://business.didit.me) → API & Webhooks.

---

## Endpoint

```
POST https://verification.didit.me/v3/face-search/
```

### Headers

| Header | Value | Required |
|---|---|---|
| `x-api-key` | Your API key | **Yes** |
| `Content-Type` | `multipart/form-data` | **Yes** |

### Request Parameters (multipart/form-data)

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `user_image` | file | **Yes** | — | Face image to search (JPEG/PNG/WebP/TIFF, max 5MB) |
| `rotate_image` | boolean | No | `false` | Try 0/90/180/270 rotations for non-upright faces |
| `save_api_request` | boolean | No | `true` | Save in Business Console |
| `vendor_data` | string | No | — | Your identifier for session tracking |

### Example

```python
import requests

response = requests.post(
    "https://verification.didit.me/v3/face-search/",
    headers={"x-api-key": "YOUR_API_KEY"},
    files={"user_image": ("photo.jpg", open("photo.jpg", "rb"), "image/jpeg")},
)
print(response.json())
```

```typescript
const formData = new FormData();
formData.append("user_image", photoFile);

const response = await fetch("https://verification.didit.me/v3/face-search/", {
  method: "POST",
  headers: { "x-api-key": "YOUR_API_KEY" },
  body: formData,
});
```

### Response (200 OK)

```json
{
  "request_id": "a1b2c3d4-...",
  "face_search": {
    "status": "Approved",
    "total_matches": 1,
    "matches": [
      {
        "session_id": "uuid-...",
        "session_number": 1234,
        "similarity_percentage": 95.2,
        "vendor_data": "user-456",
        "verification_date": "2025-06-10T10:30:00Z",
        "user_details": {
          "name": "Elena Martinez",
          "document_type": "Identity Card",
          "document_number": "***456"
        },
        "match_image_url": "https://example.com/match.jpg",
        "status": "Approved",
        "is_blocklisted": false
      }
    ],
    "user_image": {
      "entities": [
        {"age": "27.6", "bbox": [40, 40, 120, 120], "confidence": 0.95, "gender": "female"}
      ],
      "best_angle": 0
    },
    "warnings": []
  }
}
```

### Status Values & Handling

| Status | Meaning | Action |
|---|---|---|
| `"Approved"` | No concerning matches found | Proceed — new unique user |
| `"In Review"` | Matches above similarity threshold | Review `matches[]` for potential duplicates |
| `"Declined"` | Blocklist match or policy violation | Check `matches[].is_blocklisted` and `warnings` |

### Error Responses

| Code | Meaning | Action |
|---|---|---|
| `400` | Invalid request | Check file format, size, parameters |
| `401` | Invalid API key | Verify `x-api-key` header |
| `403` | Insufficient credits | Top up at business.didit.me |

---

## Response Field Reference

### Match Object

| Field | Type | Description |
|---|---|---|
| `session_id` | string | UUID of the matching session |
| `session_number` | integer | Session number |
| `similarity_percentage` | float | 0-100 similarity score |
| `vendor_data` | string | Your reference from the matching session |
| `verification_date` | string | ISO 8601 timestamp |
| `user_details.name` | string | Name from the matching session |
| `user_details.document_type` | string | Document type used |
| `user_details.document_number` | string | Partially masked document number |
| `match_image_url` | string | Temporary URL (expires **60 min**) |
| `status` | string | Status of the matching session |
| `is_blocklisted` | boolean | Whether the match is from the blocklist |

### User Image Object

| Field | Type | Description |
|---|---|---|
| `entities[].age` | string | Estimated age |
| `entities[].bbox` | array | Face bounding box `[x1, y1, x2, y2]` |
| `entities[].confidence` | float | Detection confidence (0-1) |
| `entities[].gender` | string | `"male"` or `"female"` |
| `best_angle` | integer | Rotation applied (0, 90, 180, 270) |

---

## Warning Tags

### Auto-Decline

| Tag | Description |
|---|---|
| `NO_FACE_DETECTED` | No face found in image |
| `FACE_IN_BLOCKLIST` | Face matches a blocklisted entry |

### Configurable

| Tag | Description |
|---|---|
| `MULTIPLE_FACES_DETECTED` | Multiple faces detected — unclear which to use |

> **Similarity threshold** and **allow multiple faces** settings are configurable in Console.

Warning severity: `error` (→ Declined), `warning` (→ In Review), `information` (no effect).

---

## Common Workflows

### Duplicate Account Detection

```
1. During new user registration
2. POST /v3/face-search/ → {"user_image": selfie}
3. If total_matches == 0 → new unique user
   If matches found → check similarity_percentage:
     90%+ → likely duplicate, investigate matches[].vendor_data
     70-89% → possible match, flag for manual review
```

### Combined Verification + Dedup

```
1. POST /v3/passive-liveness/ → verify user is real
2. POST /v3/face-search/ → check for existing accounts
3. POST /v3/id-verification/ → verify identity document
4. POST /v3/face-match/ → compare selfie to document photo
5. All Approved → verified, unique, real user
```

> **Security:** Match image URLs expire after 60 minutes. Store only `session_id` and `similarity_percentage` — minimize biometric data on your servers.
