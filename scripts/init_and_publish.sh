#!/usr/bin/env bash
# One-shot: validate + publish a skill to GitHub
#
# Usage:
#   bash scripts/init_and_publish.sh <skill-name> <github-owner> [visibility]
#
# Example:
#   bash scripts/init_and_publish.sh code-reviewer Weiming3 public
#
# Requires: gh CLI (authenticated), python3 + pyyaml

set -euo pipefail

SKILL_NAME="${1:?Usage: $0 <skill-name> <github-owner> [public|private]}"
GH_OWNER="${2:?Usage: $0 <skill-name> <github-owner> [public|private]}"
VISIBILITY="${3:-private}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

# 1. detect source directory
if [[ -d "$ROOT/$SKILL_NAME" ]]; then
    SOURCE="$ROOT/$SKILL_NAME"
elif [[ -f "$ROOT/SKILL.md" ]]; then
    SOURCE="$ROOT"
else
    echo "[ERROR] No source found. Expected: $ROOT/$SKILL_NAME/SKILL.md or $ROOT/SKILL.md"
    exit 2
fi

echo "============================================================"
echo "  Skill Publisher (one-shot)"
echo "  skill:   $SKILL_NAME"
echo "  source:  $SOURCE"
echo "  owner:   $GH_OWNER"
echo "  visibility: $VISIBILITY"
echo "============================================================"
echo

# 2. validate
echo "[1/3] Validating SKILL.md ..."
python3 "$SCRIPT_DIR/validate_skill.py" "$SOURCE/SKILL.md"

# 3. publish
echo
echo "[2/3] Publishing to GitHub ..."
python3 "$SCRIPT_DIR/publish.py" \
    --name "$SKILL_NAME" \
    --source "$SOURCE" \
    --owner "$GH_OWNER" \
    --visibility "$VISIBILITY"

# 4. done
echo
echo "[3/3] ✓ Done"
echo
echo "Next steps:"
echo "  1. Visit https://github.com/$GH_OWNER/$SKILL_NAME"
echo "  2. Add topics: agent-skill, anthropic-skills, mavis"
echo "  3. (Optional) PR to awesome-claude-skills:"
echo "     https://github.com/ComposioHQ/awesome-claude-skills/blob/main/README.md"