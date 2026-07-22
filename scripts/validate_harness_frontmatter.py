#!/usr/bin/env python3
"""Validate YAML frontmatter and skill references in agent/skill Markdown files.

Checks performed:
  1. File starts with '---'
  2. Frontmatter has a closing '---'
  3. Required fields exist and are non-empty
     - agents: name, description, model
     - skills:  name, description
  4. Every skill declared under '## 사용하는 스킬' in an agent file
     has a corresponding .claude/skills/{skill-name}/SKILL.md
  5. The lightnovel orchestrator's required agent references exist
  6. .claude/skills and .agents/skills are exact mirrors
  7. .claude/agents and .codex/agents have a one-to-one file mapping

Usage:
    python3 scripts/validate_harness_frontmatter.py

Exit codes:
    0 — all checks pass
    1 — one or more checks fail
"""

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

AGENT_GLOB = ".claude/agents/*.md"
SKILL_GLOB = ".claude/skills/*/SKILL.md"

REQUIRED_AGENT_FIELDS = {"name", "description", "model"}
REQUIRED_SKILL_FIELDS = {"name", "description"}

# Section heading that lists skill names inside agent files.
SKILL_SECTION_HEADING = "## 사용하는 스킬"

# ---------------------------------------------------------------------------
# Frontmatter parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> tuple[dict[str, str] | None, list[str]]:
    """Return (fields_dict, errors).

    fields_dict is None when the file does not have a valid frontmatter block.
    errors is a list of human-readable problem descriptions.
    """
    errors: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()

    if not lines or lines[0].strip() != "---":
        errors.append("does not start with '---'")
        return None, errors

    # Find closing ---
    close_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close_idx = i
            break

    if close_idx is None:
        errors.append("frontmatter has no closing '---'")
        return None, errors

    fm_lines = lines[1:close_idx]

    # Simple key: value parser.
    # Handles plain scalars and block scalars introduced by `|` or `>`.
    fields: dict[str, str] = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        # Skip blank lines and comment lines
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        if ":" in line:
            key, _, raw_value = line.partition(":")
            key = key.strip()
            raw_value = raw_value.strip()
            if raw_value in ("|", ">", "|2", ">2", "|-", ">-"):
                # Block scalar: collect indented continuation lines
                block_lines: list[str] = []
                i += 1
                while i < len(fm_lines):
                    next_line = fm_lines[i]
                    if next_line == "" or next_line.startswith((" ", "\t")):
                        block_lines.append(next_line.strip())
                        i += 1
                    else:
                        break
                fields[key] = " ".join(block_lines).strip()
            else:
                fields[key] = raw_value
                i += 1
        else:
            i += 1

    return fields, errors


# ---------------------------------------------------------------------------
# Skill-reference extractor
# ---------------------------------------------------------------------------

_BACKTICK_RE = re.compile(r"`([^`]+)`")

def extract_declared_skills(path: Path) -> list[str]:
    """Parse an agent file and return skill names listed under SKILL_SECTION_HEADING.

    Skill names are extracted from backtick-quoted tokens on list-item lines
    (lines starting with '-') that appear after the section heading and before
    the next '##' heading.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    skill_names: list[str] = []
    inside_section = False

    for line in lines:
        stripped = line.strip()

        if stripped == SKILL_SECTION_HEADING:
            inside_section = True
            continue

        if inside_section:
            # Stop at next level-2 heading
            if stripped.startswith("## "):
                break
            # Only pick up list-item lines
            if stripped.startswith("- "):
                for match in _BACKTICK_RE.finditer(stripped):
                    skill_names.append(match.group(1))

    return skill_names


# ---------------------------------------------------------------------------
# Per-file frontmatter validation
# ---------------------------------------------------------------------------

def validate_frontmatter(path: Path, required_fields: set[str]) -> list[str]:
    """Return a list of error strings for this file (empty = valid)."""
    errors: list[str] = []

    fields, parse_errors = parse_frontmatter(path)
    errors.extend(parse_errors)

    if fields is None:
        return errors

    for field in sorted(required_fields):
        if field not in fields:
            errors.append(f"missing required field: '{field}'")
        elif not fields[field].strip():
            errors.append(f"field '{field}' is present but empty")

    return errors


# ---------------------------------------------------------------------------
# Skill-reference validation
# ---------------------------------------------------------------------------

def validate_skill_refs(agent_path: Path, skill_dirs: set[str]) -> list[str]:
    """Return error strings for any skill declared in the agent that has no SKILL.md."""
    errors: list[str] = []
    declared = extract_declared_skills(agent_path)
    for skill_name in declared:
        if skill_name not in skill_dirs:
            errors.append(
                f"declares skill '{skill_name}' but "
                f".claude/skills/{skill_name}/SKILL.md does not exist"
            )
    return errors


def validate_lightnovel_agent_refs(orchestrator_path: Path, agent_names: set[str]) -> list[str]:
    """Lightweight check for lightnovel orchestrator's critical agent references."""
    errors: list[str] = []
    if not orchestrator_path.is_file():
        return [f"missing orchestrator skill: {orchestrator_path.relative_to(REPO_ROOT)}"]

    text = orchestrator_path.read_text(encoding="utf-8")
    # Keep this check intentionally lightweight: only guard must-have Phase agents.
    required_agents = {
        "story-bible-planner",
        "season-planner",
        "chapter-plotter",
        "chapter-novelist",
        "chapter-prose-reviser",
        "novel-editor",
        "epub-builder",
    }
    for name in sorted(required_agents):
        if f"`{name}`" in text and name not in agent_names:
            errors.append(
                f"references agent '{name}' but .claude/agents/{name}.md does not exist"
            )
    return errors


def validate_skill_mirrors() -> list[str]:
    """Require .claude/skills and .agents/skills to contain identical files."""
    errors: list[str] = []
    claude_root = REPO_ROOT / ".claude" / "skills"
    agents_root = REPO_ROOT / ".agents" / "skills"
    claude_files = {
        path.relative_to(claude_root): path
        for path in claude_root.rglob("*")
        if path.is_file()
    }
    agent_files = {
        path.relative_to(agents_root): path
        for path in agents_root.rglob("*")
        if path.is_file()
    }

    for rel in sorted(claude_files.keys() - agent_files.keys()):
        errors.append(f"missing .agents/skills/{rel}")
    for rel in sorted(agent_files.keys() - claude_files.keys()):
        errors.append(f"extra .agents/skills/{rel}")
    for rel in sorted(claude_files.keys() & agent_files.keys()):
        if claude_files[rel].read_bytes() != agent_files[rel].read_bytes():
            errors.append(f"skill mirror differs: {rel}")
    return errors


def validate_agent_file_mapping(agent_names: set[str]) -> list[str]:
    """Require every Claude agent to have exactly one Codex TOML mirror."""
    codex_names = {path.stem for path in (REPO_ROOT / ".codex" / "agents").glob("*.toml")}
    errors: list[str] = []
    for name in sorted(agent_names - codex_names):
        errors.append(f"missing .codex/agents/{name}.toml")
    for name in sorted(codex_names - agent_names):
        errors.append(f"extra .codex/agents/{name}.toml")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    agent_paths = sorted(REPO_ROOT.glob(AGENT_GLOB))
    skill_paths = sorted(REPO_ROOT.glob(SKILL_GLOB))

    if not agent_paths and not skill_paths:
        print("WARNING: no agent or skill files found — check REPO_ROOT path")
        return 1

    # Build set of skill directory names that actually exist.
    skill_dirs: set[str] = {p.parent.name for p in skill_paths}

    agent_names: set[str] = {p.stem for p in agent_paths}

    total = 0
    failed = 0

    def check(path: Path, required: set[str], extra_errors: list[str]) -> None:
        nonlocal total, failed
        total += 1
        errs = validate_frontmatter(path, required) + extra_errors
        rel = path.relative_to(REPO_ROOT)
        if errs:
            failed += 1
            print(f"  FAIL  {rel}")
            for e in errs:
                print(f"        → {e}")
        else:
            print(f"  OK    {rel}")

    print(f"=== Agents ({len(agent_paths)} files) ===")
    for p in agent_paths:
        skill_ref_errors = validate_skill_refs(p, skill_dirs)
        check(p, REQUIRED_AGENT_FIELDS, skill_ref_errors)

    print()
    print(f"=== Skills ({len(skill_paths)} files) ===")
    for p in skill_paths:
        extra_errors: list[str] = []
        if p == REPO_ROOT / ".claude/skills/lightnovel-writing-orchestrator/SKILL.md":
            extra_errors = validate_lightnovel_agent_refs(p, agent_names)
        check(p, REQUIRED_SKILL_FIELDS, extra_errors)

    harness_errors = validate_skill_mirrors() + validate_agent_file_mapping(agent_names)
    print()
    print("=== Harness mirrors ===")
    if harness_errors:
        failed += 1
        print("  FAIL  harness mirrors")
        for error in harness_errors:
            print(f"        → {error}")
    else:
        print("  OK    skill content and agent file mappings")

    print()
    if failed == 0:
        print(f"All {total} files valid.")
        return 0
    else:
        print(f"{failed}/{total} file(s) failed validation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
