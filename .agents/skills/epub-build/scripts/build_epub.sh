#!/usr/bin/env bash
# Build EPUB 3 from manuscript + cover + manifest.
# Usage: build_epub.sh <slug>
#   Reads: <slug>/manuscript/04_manuscript.md
#          <slug>/assets/cover.png
#          <slug>/manuscript/book_manifest.json
#   Writes: <title-slug>-v<version>.epub (project root)
#           <slug>/reviews/build_log.md

set -euo pipefail

SLUG="${1:-}"
if [[ -z "$SLUG" ]]; then
  echo "usage: build_epub.sh <slug>" >&2
  exit 2
fi

WS="${SLUG}"
MANUSCRIPT="${WS}/manuscript/04_manuscript.md"
COVER="${WS}/assets/cover.png"
MANIFEST="${WS}/manuscript/book_manifest.json"
LOG="${WS}/reviews/build_log.md"
mkdir -p "$(dirname "$LOG")"

for f in "$MANUSCRIPT" "$MANIFEST"; do
  [[ -f "$f" ]] || { echo "missing: $f" >&2; exit 3; }
done

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not installed. Run: brew install pandoc" >&2
  exit 4
fi

# Extract metadata one field per call (avoids shell quoting issues with non-ASCII).
read_field() {
  python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get(sys.argv[2], ''))" "$MANIFEST" "$1"
}
TITLE=$(read_field title)
AUTHOR=$(read_field author)
LANG=$(read_field language)
VERSION=$(read_field version)
PUB_DATE=$(read_field pub_date)
IDENTIFIER=$(read_field identifier)
DESCRIPTION=$(read_field description)
STRUCTURE_TYPE=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print((d.get('structure') or {}).get('type', ''))" "$MANIFEST")

if [[ -z "$AUTHOR" ]]; then
  if [[ "$STRUCTURE_TYPE" == "light_novel" || -f "${WS}/bible/02_story_bible.md" ]]; then
    AUTHOR="AI-Author"
  else
    AUTHOR="Toby-AI"
  fi
  echo "info: manifest author empty — falling back to default '${AUTHOR}'" >&2
fi

# Slugify title for filename.
FILENAME_TITLE=$(python3 -c "
import re, sys
t = sys.argv[1]
t = t.replace(' ', '-')
t = re.sub(r'[\\\\/:*?\"<>|]', '', t)
print(t)
" "$TITLE")

OUTPUT="${FILENAME_TITLE}-v${VERSION}.epub"

# If output exists, move previous to _prev/.
if [[ -f "$OUTPUT" ]]; then
  mkdir -p "_prev"
  mv "$OUTPUT" "_prev/$(basename "$OUTPUT" .epub)-$(date +%Y%m%d%H%M%S).epub"
fi

META_YAML="${WS}/manuscript/.meta.yaml"
RIGHTS="© $(date +%Y) ${AUTHOR}"

# Build metadata YAML for pandoc using Python stdlib only.
# This avoids YAML breakage when values contain quotes/newlines/special chars.
python3 - "$META_YAML" "$TITLE" "$AUTHOR" "$LANG" "$PUB_DATE" "$IDENTIFIER" "$DESCRIPTION" "$RIGHTS" <<'PY'
from pathlib import Path
import sys

def yaml_single_quoted(value: str) -> str:
    # YAML single-quoted scalar: escape single quote by doubling it.
    return "'" + value.replace("'", "''") + "'"

out_path = Path(sys.argv[1])
title, author, lang, pub_date, identifier, description, rights = sys.argv[2:]

fields = [
    ("title", title),
    ("author", author),
    ("lang", lang),
    ("date", pub_date),
    ("identifier", identifier),
    ("description", description),
    ("rights", rights),
]

lines = ["---"]
for key, value in fields:
    if "\n" in value:
        lines.append(f"{key}: |-")
        for line in value.splitlines():
            lines.append(f"  {line}")
    else:
        lines.append(f"{key}: {yaml_single_quoted(value)}")
lines.append("---")
out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

# Build cover arg (optional).
COVER_ARG=()
if [[ -f "$COVER" ]]; then
  COVER_ARG+=(--epub-cover-image="$COVER")
fi

# Run pandoc.
set +e
pandoc "$MANUSCRIPT" \
  --from markdown \
  --to epub3 \
  --metadata-file="$META_YAML" \
  "${COVER_ARG[@]}" \
  --toc --toc-depth=2 \
  --split-level=1 \
  --output "$OUTPUT" 2>"${WS}/.pandoc_err"
PANDOC_EXIT=$?
set -e

SIZE=0
if [[ -f "$OUTPUT" ]]; then
  SIZE=$(stat -f%z "$OUTPUT" 2>/dev/null || stat -c%s "$OUTPUT" 2>/dev/null || echo 0)
fi

# epubcheck (optional).
CHECK_RESULT="skipped (epubcheck not installed)"
if command -v epubcheck >/dev/null 2>&1 && [[ -f "$OUTPUT" ]]; then
  if epubcheck "$OUTPUT" >"${WS}/.epubcheck.log" 2>&1; then
    CHECK_RESULT="passed"
  else
    CHECK_RESULT="failed — see ${WS}/.epubcheck.log"
  fi
fi

# Write build log.
{
  echo "# Build Log — ${TITLE} v${VERSION}"
  echo ""
  echo "- **Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "- **Output:** \`${OUTPUT}\`"
  echo "- **Size:** ${SIZE} bytes"
  echo "- **Pandoc exit:** ${PANDOC_EXIT}"
  echo "- **epubcheck:** ${CHECK_RESULT}"
  echo ""
  echo "## Metadata"
  echo "- title: ${TITLE}"
  echo "- author: ${AUTHOR}"
  echo "- language: ${LANG}"
  echo "- version: ${VERSION}"
  echo "- pub_date: ${PUB_DATE}"
  if [[ $PANDOC_EXIT -ne 0 ]]; then
    echo ""
    echo "## Pandoc stderr"
    echo '```'
    cat "${WS}/.pandoc_err"
    echo '```'
  fi
} > "$LOG"

# Cleanup.
rm -f "$META_YAML" "${WS}/.pandoc_err"

if [[ $PANDOC_EXIT -ne 0 ]]; then
  echo "build failed — see $LOG" >&2
  exit $PANDOC_EXIT
fi

if [[ $SIZE -lt 50000 ]]; then
  echo "warning: output is suspiciously small (${SIZE} bytes)" >&2
fi

echo "built: $OUTPUT ($SIZE bytes)"
