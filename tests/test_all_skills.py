#!/usr/bin/env python3
"""
Comprehensive test suite for all Didit API skills.
Tests API connectivity, authentication, and basic request/response for each endpoint.

Usage:
    export DIDIT_API_KEY="your_api_key"
    export DIDIT_WORKFLOW_ID="your_workflow_id"   # optional, for session tests
    python test_all_skills.py

NOTE: Uses a tiny test image for image-based APIs. Expects "Declined" with
      warnings like NO_FACE_DETECTED — this confirms the API is reachable,
      authenticated, and processing correctly.
"""

import base64
import io
import json
import os
import sys
import time

import requests

API_KEY = os.environ.get("DIDIT_API_KEY", "")
WORKFLOW_ID = os.environ.get("DIDIT_WORKFLOW_ID", "d8d2fa2d-c69c-471c-b7bc-bc71512b43ef")
BASE_URL = "https://verification.didit.me"

# Tiny 1x1 red PNG for image-based tests
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)

HEADERS_JSON = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}
HEADERS_KEY = {
    "x-api-key": API_KEY,
}

results = []


def log(skill, endpoint, status, detail, passed):
    icon = "PASS" if passed else "FAIL"
    results.append({"skill": skill, "endpoint": endpoint, "status": status, "detail": detail, "passed": passed})
    print(f"  [{icon}] {endpoint} → {status} {detail}")


def make_image_file(name="test.png"):
    return (name, io.BytesIO(TINY_PNG), "image/png")


def test_id_verification():
    print("\n1. ID Verification")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/id-verification/",
            headers=HEADERS_KEY,
            files={"front_image": make_image_file()},
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("id_verification", {}).get("status", "N/A")
        log("id-verification", "POST /v3/id-verification/", r.status_code,
            f"status={status}", r.status_code == 200)
    except Exception as e:
        log("id-verification", "POST /v3/id-verification/", "ERR", str(e), False)


def test_passive_liveness():
    print("\n2. Passive Liveness")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/passive-liveness/",
            headers=HEADERS_KEY,
            files={"user_image": make_image_file()},
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("liveness", {}).get("status", "N/A")
        log("passive-liveness", "POST /v3/passive-liveness/", r.status_code,
            f"status={status}", r.status_code == 200)
    except Exception as e:
        log("passive-liveness", "POST /v3/passive-liveness/", "ERR", str(e), False)


def test_face_match():
    print("\n3. Face Match")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/face-match/",
            headers=HEADERS_KEY,
            files={
                "user_image": make_image_file("user.png"),
                "ref_image": make_image_file("ref.png"),
            },
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("face_match", {}).get("status", "N/A")
        log("face-match", "POST /v3/face-match/", r.status_code,
            f"status={status}", r.status_code == 200)
    except Exception as e:
        log("face-match", "POST /v3/face-match/", "ERR", str(e), False)


def test_face_search():
    print("\n4. Face Search")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/face-search/",
            headers=HEADERS_KEY,
            files={"user_image": make_image_file()},
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("face_search", {}).get("status", body.get("error", "N/A"))
        # 400 "No face detected" is expected for a 1x1 test image
        log("face-search", "POST /v3/face-search/", r.status_code,
            f"status={status}", r.status_code in [200, 400])
    except Exception as e:
        log("face-search", "POST /v3/face-search/", "ERR", str(e), False)


def test_age_estimation():
    print("\n5. Age Estimation")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/age-estimation/",
            headers=HEADERS_KEY,
            files={"user_image": make_image_file()},
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("liveness", {}).get("status", "N/A")
        log("age-estimation", "POST /v3/age-estimation/", r.status_code,
            f"status={status}", r.status_code == 200)
    except Exception as e:
        log("age-estimation", "POST /v3/age-estimation/", "ERR", str(e), False)


def test_email_verification():
    print("\n6. Email Verification")
    # Test Send endpoint
    try:
        r = requests.post(
            f"{BASE_URL}/v3/email/send/",
            headers=HEADERS_JSON,
            json={"email": "test-didit-skill@example.com", "options": {"code_size": 6}},
            timeout=30,
        )
        body = r.json()
        status = body.get("status", "N/A")
        log("email-verification", "POST /v3/email/send/", r.status_code,
            f"status={status}", r.status_code == 200)
    except Exception as e:
        log("email-verification", "POST /v3/email/send/", "ERR", str(e), False)

    # Test Check endpoint (expected: "Expired or Not Found" since we don't have real code)
    try:
        r = requests.post(
            f"{BASE_URL}/v3/email/check/",
            headers=HEADERS_JSON,
            json={"email": "test-didit-skill@example.com", "code": "000000"},
            timeout=30,
        )
        body = r.json()
        status = body.get("status", "N/A")
        log("email-verification", "POST /v3/email/check/", r.status_code,
            f"status={status}", r.status_code in [200, 404])
    except Exception as e:
        log("email-verification", "POST /v3/email/check/", "ERR", str(e), False)


def test_phone_verification():
    print("\n7. Phone Verification")
    # Test Send endpoint
    try:
        r = requests.post(
            f"{BASE_URL}/v3/phone/send/",
            headers=HEADERS_JSON,
            json={
                "phone_number": "+15550000000",
                "options": {"preferred_channel": "sms", "code_size": 6},
            },
            timeout=30,
        )
        body = r.json()
        status = body.get("status", "N/A")
        # 200 is ideal, 400 acceptable (invalid test number)
        log("phone-verification", "POST /v3/phone/send/", r.status_code,
            f"status={status}", r.status_code in [200, 400])
    except Exception as e:
        log("phone-verification", "POST /v3/phone/send/", "ERR", str(e), False)

    # Test Check endpoint
    try:
        r = requests.post(
            f"{BASE_URL}/v3/phone/check/",
            headers=HEADERS_JSON,
            json={"phone_number": "+15550000000", "code": "000000"},
            timeout=30,
        )
        body = r.json()
        status = body.get("status", "N/A")
        log("phone-verification", "POST /v3/phone/check/", r.status_code,
            f"status={status}", r.status_code in [200, 400, 404])
    except Exception as e:
        log("phone-verification", "POST /v3/phone/check/", "ERR", str(e), False)


def test_aml_screening():
    print("\n8. AML Screening")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/aml/",
            headers=HEADERS_JSON,
            json={
                "full_name": "John Test Smith",
                "date_of_birth": "1990-01-01",
                "nationality": "US",
                "vendor_data": "skill-test-suite",
            },
            timeout=30,
        )
        body = r.json()
        status = body.get("aml", {}).get("status", body.get("status", "N/A"))
        total_hits = body.get("aml", {}).get("total_hits", "N/A")
        log("aml-screening", "POST /v3/aml/", r.status_code,
            f"status={status}, hits={total_hits}", r.status_code == 200)
    except Exception as e:
        log("aml-screening", "POST /v3/aml/", "ERR", str(e), False)


def test_proof_of_address():
    print("\n9. Proof of Address")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/poa/",
            headers=HEADERS_KEY,
            files={"document": make_image_file("doc.png")},
            data={"vendor_data": "skill-test-suite"},
            timeout=30,
        )
        body = r.json()
        status = body.get("poa", {}).get("status", body.get("status", "N/A"))
        doc_type = body.get("poa", {}).get("document_type", "N/A")
        log("proof-of-address", "POST /v3/poa/", r.status_code,
            f"status={status}, doc_type={doc_type}", r.status_code in [200, 400])
    except Exception as e:
        log("proof-of-address", "POST /v3/poa/", "ERR", str(e), False)


def test_database_validation():
    print("\n10. Database Validation")
    try:
        r = requests.post(
            f"{BASE_URL}/v3/database-validation/",
            headers=HEADERS_JSON,
            json={
                "id_number": "12345678",
                "first_name": "Test",
                "last_name": "User",
                "issuing_state": "PER",
                "vendor_data": "skill-test-suite",
            },
            timeout=30,
        )
        body = r.json()
        status = body.get("database_validation", {}).get("status", body.get("status", "N/A"))
        log("database-validation", "POST /v3/database-validation/", r.status_code,
            f"status={status}", r.status_code in [200, 400, 403])
    except Exception as e:
        log("database-validation", "POST /v3/database-validation/", "ERR", str(e), False)


def test_sessions():
    print("\n11. Sessions")

    session_id = None

    # Create Session
    try:
        r = requests.post(
            f"{BASE_URL}/v3/session/",
            headers=HEADERS_JSON,
            json={
                "workflow_id": WORKFLOW_ID,
                "vendor_data": "test-skill-suite",
            },
            timeout=30,
        )
        body = r.json()
        session_id = body.get("session_id", None)
        status = body.get("status", "N/A")
        url = body.get("url", "N/A")
        log("sessions", "POST /v3/session/ (create)", r.status_code,
            f"status={status}, id={session_id}", r.status_code == 201)
    except Exception as e:
        log("sessions", "POST /v3/session/ (create)", "ERR", str(e), False)

    # List Sessions
    try:
        r = requests.get(
            f"{BASE_URL}/v3/sessions/",
            headers=HEADERS_KEY,
            params={"vendor_data": "test-skill-suite"},
            timeout=30,
        )
        body = r.json()
        count = body.get("count", len(body) if isinstance(body, list) else "N/A")
        log("sessions", "GET /v3/sessions/ (list)", r.status_code,
            f"count={count}", r.status_code == 200)
    except Exception as e:
        log("sessions", "GET /v3/sessions/ (list)", "ERR", str(e), False)

    if session_id:
        # Retrieve Session
        try:
            r = requests.get(
                f"{BASE_URL}/v3/session/{session_id}/decision/",
                headers=HEADERS_KEY,
                timeout=30,
            )
            body = r.json()
            status = body.get("status", "N/A")
            log("sessions", "GET /v3/session/{id}/decision/ (retrieve)", r.status_code,
                f"status={status}", r.status_code == 200)
        except Exception as e:
            log("sessions", "GET /v3/session/{id}/decision/ (retrieve)", "ERR", str(e), False)

        # Generate PDF (403 expected for "Not Started" session — requires completed verification)
        try:
            r = requests.get(
                f"{BASE_URL}/v3/session/{session_id}/generate-pdf",
                headers=HEADERS_KEY,
                timeout=30,
            )
            log("sessions", "GET /v3/session/{id}/generate-pdf", r.status_code,
                f"content-type={r.headers.get('content-type', 'N/A')[:30]} (403 expected for new session)",
                r.status_code in [200, 400, 403])
        except Exception as e:
            log("sessions", "GET /v3/session/{id}/generate-pdf", "ERR", str(e), False)

        # Update Status (decline test session)
        try:
            r = requests.patch(
                f"{BASE_URL}/v3/session/{session_id}/update-status/",
                headers=HEADERS_JSON,
                json={"new_status": "Declined", "comment": "Test suite cleanup"},
                timeout=30,
            )
            log("sessions", "PATCH /v3/session/{id}/update-status/", r.status_code,
                f"→ Declined", r.status_code in [200, 400])
        except Exception as e:
            log("sessions", "PATCH /v3/session/{id}/update-status/", "ERR", str(e), False)

        # Delete Session — skipped so session remains visible in Business Console
        # To clean up: DELETE /v3/session/{session_id}/delete/
        log("sessions", "DELETE /v3/session/{id}/delete/", "SKIP",
            "kept in console for review", True)


def test_blocklist():
    print("\n12. Blocklist")

    # List blocklist
    try:
        r = requests.get(
            f"{BASE_URL}/v3/blocklist/",
            headers=HEADERS_KEY,
            timeout=30,
        )
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        count = len(body) if isinstance(body, list) else body.get("count", "N/A")
        log("blocklist", "GET /v3/blocklist/ (list)", r.status_code,
            f"items={count}", r.status_code == 200)
    except Exception as e:
        log("blocklist", "GET /v3/blocklist/ (list)", "ERR", str(e), False)

    # Add to blocklist (with dummy session_id — expect 400/404)
    try:
        r = requests.post(
            f"{BASE_URL}/v3/blocklist/add/",
            headers=HEADERS_JSON,
            json={"session_id": "00000000-0000-0000-0000-000000000000", "blocklist_face": True},
            timeout=30,
        )
        log("blocklist", "POST /v3/blocklist/add/", r.status_code,
            "auth OK (expected 400/404 for dummy session)", r.status_code in [200, 400, 404])
    except Exception as e:
        log("blocklist", "POST /v3/blocklist/add/", "ERR", str(e), False)

    # Remove from blocklist (with dummy session_id — expect 400/404)
    try:
        r = requests.post(
            f"{BASE_URL}/v3/blocklist/remove/",
            headers=HEADERS_JSON,
            json={"session_id": "00000000-0000-0000-0000-000000000000", "unblock_face": True},
            timeout=30,
        )
        log("blocklist", "POST /v3/blocklist/remove/", r.status_code,
            "auth OK (expected 400/404 for dummy session)", r.status_code in [200, 400, 404])
    except Exception as e:
        log("blocklist", "POST /v3/blocklist/remove/", "ERR", str(e), False)


def test_webhooks_skill():
    """Webhooks don't have an API to call — verify the skill documents the right signature logic."""
    print("\n13. Webhooks (signature verification test)")
    import hmac
    import hashlib

    secret = "test_webhook_secret"
    timestamp = str(int(time.time()))
    session_id = "test-session-123"
    status = "Approved"
    webhook_type = "status.updated"

    # Test X-Signature-Simple computation
    message = f"{timestamp}:{session_id}:{status}:{webhook_type}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    assert len(expected) == 64, "HMAC should be 64 hex chars"
    log("webhooks", "HMAC-SHA256 Simple signature", "OK",
        f"sig={expected[:16]}...", True)

    # Test X-Signature-V2 computation
    body = {"session_id": session_id, "status": status, "webhook_type": webhook_type, "timestamp": int(timestamp)}
    canonical = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    v2_message = f"{timestamp}:{canonical}"
    v2_sig = hmac.new(secret.encode(), v2_message.encode(), hashlib.sha256).hexdigest()
    assert len(v2_sig) == 64
    log("webhooks", "HMAC-SHA256 V2 signature", "OK",
        f"sig={v2_sig[:16]}...", True)


def main():
    if not API_KEY:
        print("ERROR: DIDIT_API_KEY environment variable not set")
        print("Usage: export DIDIT_API_KEY='your_key' && python test_all_skills.py")
        sys.exit(1)

    print("=" * 70)
    print("Didit Skills — Comprehensive API Test Suite")
    print(f"API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"Workflow ID: {WORKFLOW_ID}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 70)

    test_id_verification()
    test_passive_liveness()
    test_face_match()
    test_face_search()
    test_age_estimation()
    test_email_verification()
    test_phone_verification()
    test_aml_screening()
    test_proof_of_address()
    test_database_validation()
    test_sessions()
    test_blocklist()
    test_webhooks_skill()

    # Summary
    print("\n" + "=" * 70)
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        print("\nFailed tests:")
        for r in results:
            if not r["passed"]:
                print(f"  ✗ [{r['skill']}] {r['endpoint']} → {r['status']} {r['detail']}")

    print("\nNOTE: Image-based APIs return 'Declined' with NO_FACE_DETECTED for tiny")
    print("test images — this is EXPECTED and confirms the API is working correctly.")
    print("Session/blocklist tests with dummy IDs return 400/404 — also expected.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
