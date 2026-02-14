#!/usr/bin/env python3
"""Scrape all pages from docs.didit.me using Playwright (headless browser).

Handles JavaScript-rendered SPA content that plain HTTP requests can't capture.
Automatically skips pages that already have sufficient content.

Usage:
    pip install playwright beautifulsoup4 markdownify
    python -m playwright install chromium
    python scrape_docs.py [--force] [--delay SECONDS] [--output DIR] [--min-size BYTES]

Options:
    --force      Re-scrape all pages even if they already have content
    --delay      Delay between requests in seconds (default: 1.0)
    --output     Output directory (default: docs)
    --min-size   Minimum file size in bytes to consider "already scraped" (default: 300)
"""

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# All URLs from sitemap.xml
URLS = [
    "https://docs.didit.me/",
    "https://docs.didit.me/docs/getting-started",
    "https://docs.didit.me/reference/api-authentication",
    "https://docs.didit.me/reference/competition-analysis",
    "https://docs.didit.me/reference/features",
    "https://docs.didit.me/reference/introduction",
    "https://docs.didit.me/reference/database-validation-pricing",
    "https://docs.didit.me/reference/pricing",
    "https://docs.didit.me/reference/phone-verification-pricing",
    "https://docs.didit.me/reference/quick-start",
    "https://docs.didit.me/reference/user-verification-journey",
    "https://docs.didit.me/reference/api-full-flow",
    "https://docs.didit.me/reference/demos",
    "https://docs.didit.me/reference/zapier",
    "https://docs.didit.me/reference/android-sdk",
    "https://docs.didit.me/reference/flutter-sdk",
    "https://docs.didit.me/reference/native-sdks",
    "https://docs.didit.me/reference/ios-sdk",
    "https://docs.didit.me/reference/react-native-sdk",
    "https://docs.didit.me/reference/rate-limiting",
    "https://docs.didit.me/reference/supported-languages",
    "https://docs.didit.me/reference/verification-statuses",
    "https://docs.didit.me/reference/incontext-iframe",
    "https://docs.didit.me/reference/web-sdks",
    "https://docs.didit.me/reference/javascript-sdk",
    "https://docs.didit.me/reference/web-redirect",
    "https://docs.didit.me/reference/webview-in-ios-android",
    "https://docs.didit.me/reference/wordpress-woocommerce",
    "https://docs.didit.me/reference/webhooks",
    "https://docs.didit.me/reference/age-estimation-standalone-api",
    "https://docs.didit.me/reference/aml-screening-standalone-api",
    "https://docs.didit.me/reference/database-validation-api",
    "https://docs.didit.me/reference/check-email-verification-code-api",
    "https://docs.didit.me/reference/send-email-verification-code-api",
    "https://docs.didit.me/reference/face-match-standalone-api",
    "https://docs.didit.me/reference/face-search-standalone-api",
    "https://docs.didit.me/reference/id-verification-standalone-api",
    "https://docs.didit.me/reference/passive-liveness-api",
    "https://docs.didit.me/reference/check-phone-verification-code-api-1",
    "https://docs.didit.me/reference/send-phone-verification-code-api",
    "https://docs.didit.me/reference/proof-of-address-standalone-api",
    "https://docs.didit.me/reference/add-blocklist-verification-items",
    "https://docs.didit.me/reference/list-blocklist-verification-items",
    "https://docs.didit.me/reference/remove-blocklist-verification-items",
    "https://docs.didit.me/reference/create-session-verification-sessions",
    "https://docs.didit.me/reference/delete-sessions-verification-sessions",
    "https://docs.didit.me/reference/generate-pdf-verification-sessions",
    "https://docs.didit.me/reference/import-shared-session",
    "https://docs.didit.me/reference/list-sessions-verification-sessions",
    "https://docs.didit.me/reference/retrieve-session-verification-sessions",
    "https://docs.didit.me/reference/share-session",
    "https://docs.didit.me/reference/update-status-verification-sessions",
    "https://docs.didit.me/reference/analytics-dashboard",
    "https://docs.didit.me/reference/audit-logs",
    "https://docs.didit.me/reference/blocklist-users",
    "https://docs.didit.me/reference/data-retention",
    "https://docs.didit.me/reference/export-to-pdf-csv-dashboard",
    "https://docs.didit.me/reference/manual-review",
    "https://docs.didit.me/reference/session-chats",
    "https://docs.didit.me/reference/uni-links",
    "https://docs.didit.me/reference/verification-links-dashboard",
    "https://docs.didit.me/reference/white-label-dashboard",
    "https://docs.didit.me/reference/workflows-dashboard",
    "https://docs.didit.me/reference/age-estimation-core-technology",
    "https://docs.didit.me/reference/report-age-estimation",
    "https://docs.didit.me/reference/warnings-age-estimation",
    "https://docs.didit.me/reference/aml-match-score",
    "https://docs.didit.me/reference/aml-risk-score",
    "https://docs.didit.me/reference/continuous-monitoring-aml-screening",
    "https://docs.didit.me/reference/aml-screening-core-technology",
    "https://docs.didit.me/reference/report-aml-screening",
    "https://docs.didit.me/reference/warnings-aml-screening",
    "https://docs.didit.me/reference/watchlist-database-aml-screening",
    "https://docs.didit.me/reference/biometric-authentication-core-technology",
    "https://docs.didit.me/reference/report-biometric-authentication",
    "https://docs.didit.me/reference/warnings-biometric-authentication",
    "https://docs.didit.me/reference/data-transfer-core-technology",
    "https://docs.didit.me/reference/use-cases-data-transfer",
    "https://docs.didit.me/reference/user-scopes-data-transfer",
    "https://docs.didit.me/reference/database-validation-matching-methods",
    "https://docs.didit.me/reference/database-validation-report",
    "https://docs.didit.me/reference/database-validation-supported-countries",
    "https://docs.didit.me/reference/database-validation-warnings",
    "https://docs.didit.me/reference/database-validation",
    "https://docs.didit.me/reference/email-verification-core-technology",
    "https://docs.didit.me/reference/report-phone-verification-1",
    "https://docs.didit.me/reference/warnings-email-verification",
    "https://docs.didit.me/reference/face-match-11-core-technology",
    "https://docs.didit.me/reference/report-face-match",
    "https://docs.didit.me/reference/warnings-face-match",
    "https://docs.didit.me/reference/face-search-1n-core-technology",
    "https://docs.didit.me/reference/report-face-search",
    "https://docs.didit.me/reference/warnings-face-search",
    "https://docs.didit.me/reference/document-geolocation-id-verification",
    "https://docs.didit.me/reference/document-monitoring-id-verification",
    "https://docs.didit.me/reference/id-verification-core-technology",
    "https://docs.didit.me/reference/report-id-verification",
    "https://docs.didit.me/reference/supported-documents-id-verification",
    "https://docs.didit.me/reference/warnings-id-verification",
    "https://docs.didit.me/reference/ip-analysis-core-technology",
    "https://docs.didit.me/reference/report-ip-analysis",
    "https://docs.didit.me/reference/warnings-ip-analysis",
    "https://docs.didit.me/reference/liveness-core-technology",
    "https://docs.didit.me/reference/report-liveness",
    "https://docs.didit.me/reference/warnings-liveness",
    "https://docs.didit.me/reference/nfc-verification-core-technology",
    "https://docs.didit.me/reference/report-nfc-verification",
    "https://docs.didit.me/reference/supported-documents-nfc-verification",
    "https://docs.didit.me/reference/warnings-nfc-verification",
    "https://docs.didit.me/reference/phone-verification-core-technology",
    "https://docs.didit.me/reference/report-phone-verification",
    "https://docs.didit.me/reference/warnings-phone-verification",
    "https://docs.didit.me/reference/proof-of-address-core-technology",
    "https://docs.didit.me/reference/report-proof-of-address",
    "https://docs.didit.me/reference/warnings-proof-of-address",
    "https://docs.didit.me/reference/questionnaires",
    "https://docs.didit.me/reference/report-questionnaire",
    "https://docs.didit.me/reference/reusable-kyc-core-technology",
    "https://docs.didit.me/reference/share-kyc-via-api",
    "https://docs.didit.me/reference/sign-in-core-technology",
    "https://docs.didit.me/reference/security-sign-in",
    "https://docs.didit.me/changelog",
    "https://docs.didit.me/changelog/january-2026",
    "https://docs.didit.me/changelog/didit-v3-smarter-workflows-updated-pricing",
    "https://docs.didit.me/changelog/december-2025",
    "https://docs.didit.me/changelog/november",
    "https://docs.didit.me/changelog/october-2025",
    "https://docs.didit.me/changelog/september-2025",
    "https://docs.didit.me/changelog/august-2025",
    "https://docs.didit.me/changelog/july-2025",
    "https://docs.didit.me/changelog/june-2025",
    "https://docs.didit.me/changelog/april-may-2025",
    "https://docs.didit.me/changelog/march-2025",
    "https://docs.didit.me/changelog/february-2025",
    "https://docs.didit.me/changelog/january-2025",
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def url_to_filepath(url: str, output_dir: Path) -> Path:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return output_dir / "index.md"
    return output_dir / f"{path}.md"


def extract_content_from_page(page, url: str) -> str:
    """Extract content using Playwright's JS execution for best results."""

    # Strategy 1: Use JS to get the main content's innerText directly
    text = page.evaluate("""
        () => {
            // Try specific content selectors first
            const selectors = [
                '#content-container',
                'article',
                '[class*="markdown-body"]',
                'main [class*="content"]',
                'main article',
                'main',
                '[role="main"]',
                '.rm-Article',
            ];
            for (const sel of selectors) {
                const el = document.querySelector(sel);
                if (el && el.innerText.trim().length > 100) {
                    return el.innerText.trim();
                }
            }
            // Fallback to body minus nav/sidebar
            const body = document.body;
            if (!body) return '';
            const clone = body.cloneNode(true);
            clone.querySelectorAll('nav, header, footer, [class*="sidebar"], [class*="nav-"], [class*="menu"]').forEach(el => el.remove());
            return clone.innerText.trim();
        }
    """)

    if text and len(text) > 50:
        return text

    # Strategy 2: Get rendered HTML and convert with BeautifulSoup
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["script", "style", "noscript", "svg"]):
        tag.decompose()

    content = None
    for selector in [
        "#content-container", "article", '[class*="markdown-body"]',
        "main", '[role="main"]',
    ]:
        found = soup.select(selector)
        if found:
            best = max(found, key=lambda el: len(el.get_text(strip=True)))
            if len(best.get_text(strip=True)) > 50:
                content = best
                break

    if content:
        return md(str(content), heading_style="ATX", bullets="-", strip=["img"], wrap=False)

    return text or ""


def scrape_all(urls: list, output_dir: Path, delay: float, force: bool, min_size: int):
    total = len(urls)

    # Determine which URLs need scraping
    to_scrape = []
    skipped = 0
    for url in urls:
        fp = url_to_filepath(url, output_dir)
        if not force and fp.exists() and fp.stat().st_size >= min_size:
            skipped += 1
            sys.stdout.write(f"  SKIP {fp.name} ({fp.stat().st_size:,}b)\n")
            sys.stdout.flush()
        else:
            to_scrape.append(url)

    if not to_scrape:
        print(f"All {total} pages already scraped (min_size={min_size}). Use --force to re-scrape.")
        return 0, 0, skipped

    print(f"\nScraping {len(to_scrape)} pages ({skipped} already done)...\n")

    success = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=UA,
        )
        page = context.new_page()

        # Block heavy resources
        def route_handler(route):
            if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
                route.abort()
            else:
                route.continue_()

        page.route("**/*", route_handler)

        for i, url in enumerate(to_scrape, 1):
            filepath = url_to_filepath(url, output_dir)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)

                # Wait for JS content to render
                page.wait_for_timeout(3000)

                # Try waiting for content indicator
                try:
                    page.wait_for_selector(
                        "article, main, [class*='content'], h1, h2",
                        timeout=5000,
                    )
                except PlaywrightTimeout:
                    pass

                content = extract_content_from_page(page, url)

                # If content is sparse, try scrolling and waiting more
                if len(content) < 100:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                    content = extract_content_from_page(page, url)

                # Build final file
                header = f"---\nsource: {url}\nscraped_at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n---\n\n"
                full = header + content

                filepath.write_text(full, encoding="utf-8")
                size = len(full)

                status = "OK  " if size >= min_size else "WARN"
                sys.stdout.write(f"[{i}/{len(to_scrape)}] {status} {filepath.name} ({size:,} chars)\n")
                sys.stdout.flush()

                if size >= min_size:
                    success += 1
                else:
                    failed += 1

            except Exception as e:
                err = f"---\nsource: {url}\nerror: true\n---\n\n# Error\n\n{type(e).__name__}: {e}\n"
                filepath.write_text(err, encoding="utf-8")
                sys.stdout.write(f"[{i}/{len(to_scrape)}] FAIL {url} — {e}\n")
                sys.stdout.flush()
                failed += 1

            if i < len(to_scrape):
                time.sleep(delay)

        browser.close()

    return success, failed, skipped


def generate_index(urls: list, output_dir: Path, stats: dict):
    index_path = output_dir / "_INDEX.md"
    lines = [
        "# docs.didit.me — Complete Documentation Archive\n",
        f"Scraped: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
        f"Total pages: {len(urls)}\n\n",
    ]

    groups = defaultdict(list)
    for url in urls:
        fp = url_to_filepath(url, output_dir)
        group = str(fp.parent.relative_to(output_dir))
        name = fp.stem
        groups[group].append((name, url, fp))

    for group in sorted(groups):
        lines.append(f"## {group}\n")
        for name, url, fp in sorted(groups[group]):
            rel = fp.relative_to(output_dir)
            size = fp.stat().st_size if fp.exists() else 0
            lines.append(f"- [{name}]({rel}) `[{size:,}b]`")
        lines.append("")

    index_path.write_text("\n".join(lines), encoding="utf-8")

    # JSON manifest
    manifest = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(urls),
        **stats,
        "pages": [],
    }
    for url in urls:
        fp = url_to_filepath(url, output_dir)
        manifest["pages"].append({
            "url": url,
            "file": str(fp),
            "size": fp.stat().st_size if fp.exists() else 0,
        })

    (output_dir / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Index: {index_path}")
    print(f"Manifest: {output_dir / '_manifest.json'}")


def main():
    parser = argparse.ArgumentParser(description="Scrape docs.didit.me")
    parser.add_argument("--force", action="store_true", help="Re-scrape all pages")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument("--output", type=str, default="docs", help="Output directory")
    parser.add_argument("--min-size", type=int, default=300, help="Min file size to skip (bytes)")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scraping {len(URLS)} pages from docs.didit.me")
    print(f"Output: {output_dir.absolute()}")
    print(f"Delay: {args.delay}s | Force: {args.force} | Min size: {args.min_size}b")
    print("=" * 70)

    success, failed, skipped = scrape_all(URLS, output_dir, args.delay, args.force, args.min_size)

    print("=" * 70)
    print(f"Done! {success} new, {failed} failed, {skipped} skipped")

    generate_index(URLS, output_dir, {"success": success, "failed": failed, "skipped": skipped})

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
