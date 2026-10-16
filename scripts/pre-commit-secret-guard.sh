#!/usr/bin/env bash
# Pre-commit guard: refuse to commit obvious secrets.
# Install:  cp scripts/pre-commit-secret-guard.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# This is a safety net, NOT a substitute for reviewing what you stage.

set -euo pipefail

PATTERNS=(
  'ghp_[A-Za-z0-9]{20,}'          # GitHub personal access token (classic)
  'gho_[A-Za-z0-9]{20,}'          # GitHub OAuth
  'ghu_[A-Za-z0-9]{20,}'          # GitHub user-to-server
  'ghs_[A-Za-z0-9]{20,}'          # GitHub server-to-server
  'ghr_[A-Za-z0-9]{20,}'          # GitHub refresh
  'github_pat_[A-Za-z0-9_]{20,}'  # GitHub fine-grained PAT
  'sk-[A-Za-z0-9]{20,}'           # OpenAI-style
  'sk-ant-[A-Za-z0-9-]{20,}'      # Anthropic
  'xox[baprs]-[A-Za-z0-9-]{10,}'  # Slack
  'AKIA[0-9A-Z]{16}'              # AWS access key id
  'AIza[0-9A-Za-z_-]{35}'         # Google API key
  'ya29\.[0-9A-Za-z_-]+'          # Google OAuth access token
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'ssh-rsa AAAA'
  'ssh-ed25519 AAAA'
)

staged=$(git diff --cached --name-only --diff-filter=ACM)
[ -z "$staged" ] && exit 0

fail=0
for f in $staged; do
  [ -f "$f" ] || continue
  # skip the guard script itself (it legitimately contains the patterns)
  case "$f" in
    *pre-commit-secret-guard.sh) continue ;;
  esac
  for p in "${PATTERNS[@]}"; do
    if grep -nEI "$p" "$f" >/dev/null 2>&1; then
      echo "❌ SECRET GUARD: pattern '$p' found in $f" >&2
      grep -nEI "$p" "$f" >&2 || true
      fail=1
    fi
  done
done

if [ "$fail" -ne 0 ]; then
  echo "" >&2
  echo "Commit blocked. Remove the secret, or bypass with: git commit --no-verify" >&2
  exit 1
fi
exit 0
