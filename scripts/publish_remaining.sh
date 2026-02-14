#!/bin/bash
# Publish remaining skills to ClawHub (rate limit: 5 new skills/hour)
# Run this after the rate limit resets (~1 hour from first batch)

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/../skills" && pwd)"

REMAINING=(
  didit-face-search
  didit-id-verification
  didit-passive-liveness
  didit-phone-verification
  didit-proof-of-address
  didit-sessions
)

for skill in "${REMAINING[@]}"; do
  version=$(grep '^version:' "$SKILLS_DIR/$skill/SKILL.md" | head -1 | awk '{print $2}')
  echo "=== Publishing $skill@$version ==="
  clawhub publish "$SKILLS_DIR/$skill" --slug "$skill" --version "$version" --changelog "Initial release"
  echo "✅ $skill published. Waiting 10s..."
  sleep 10
done

echo ""
echo "All done! Verify with: clawhub explore"
