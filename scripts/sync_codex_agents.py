#!/usr/bin/env python3
"""Synchronize .claude agent instructions into existing .codex agent TOML files.

The Claude Markdown files are the source of truth. Codex-specific model and sandbox
settings are preserved; only description and developer_instructions are refreshed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_AGENT_DIR = REPO_ROOT / ".claude" / "agents"
CODEX_AGENT_DIR = REPO_ROOT / ".codex" / "agents"
CLAUDE_SKILL_DIR = REPO_ROOT / ".claude" / "skills"
AGENTS_SKILL_DIR = REPO_ROOT / ".agents" / "skills"


def parse_agent(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing frontmatter")

    try:
        close_idx = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: unclosed frontmatter") from exc

    fields: dict[str, str] = {}
    for line in lines[1:close_idx]:
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()

    name = fields.get("name", "")
    description = fields.get("description", "")
    if not name or not description:
        raise ValueError(f"{path}: name and description are required")

    body = "\n".join(lines[close_idx + 1 :]).lstrip("\n").rstrip() + "\n"
    if "'''" in body:
        raise ValueError(f"{path}: body contains unsupported triple single quotes")
    return name, description, body


def render_instructions(name: str, body: str) -> str:
    return f"""developer_instructions = '''
You are the `{name}` custom Codex subagent converted from `.claude/agents/{name}.md`.

Codex adaptation rules:
- Use repository skills from `.agents/skills` when these instructions name a skill; load the referenced `SKILL.md` and only the resources needed for the task.
- Coordinate through the parent Codex session. Report requested handoffs, review requests, blockers, and file paths so the parent can route the next step.
- Keep edits scoped to the files and artifacts requested by the parent session. Do not modify unrelated project files.
- Return status, produced file paths, a core summary of at most 10 lines, and next-step handoff information. Never return an artifact body in full.

Original role instructions follow.

{body.rstrip()}
'''
"""


def expected_toml(markdown_path: Path, toml_path: Path) -> str:
    name, description, body = parse_agent(markdown_path)
    current = toml_path.read_text(encoding="utf-8")
    current = re.sub(
        r'^description = .*$',
        f"description = {json.dumps(description, ensure_ascii=False)}",
        current,
        count=1,
        flags=re.MULTILINE,
    )
    instructions = render_instructions(name, body)
    updated, count = re.subn(
        r"developer_instructions = '''.*?'''\n?",
        lambda _: instructions,
        current,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError(f"{toml_path}: developer_instructions block not found")
    return updated


def sync_skills(check: bool) -> bool:
    """Synchronize skill contents and return True when drift was found."""
    claude_files = {
        path.relative_to(CLAUDE_SKILL_DIR): path
        for path in CLAUDE_SKILL_DIR.rglob("*")
        if path.is_file()
    }
    agent_files = {
        path.relative_to(AGENTS_SKILL_DIR): path
        for path in AGENTS_SKILL_DIR.rglob("*")
        if path.is_file()
    }
    if claude_files.keys() != agent_files.keys():
        missing = sorted(str(path) for path in claude_files.keys() - agent_files.keys())
        extra = sorted(str(path) for path in agent_files.keys() - claude_files.keys())
        raise ValueError(f"Skill file-set mismatch: missing={missing}, extra={extra}")

    stale = [
        rel
        for rel in sorted(claude_files)
        if claude_files[rel].read_bytes() != agent_files[rel].read_bytes()
    ]
    for rel in stale:
        action = "Stale" if check else "Updated"
        print(f"{action}: .agents/skills/{rel}")
        if not check:
            shutil.copyfile(claude_files[rel], agent_files[rel])
    if not stale:
        print(f"All {len(claude_files)} skill mirror files are current.")
    return bool(stale)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report drift without writing")
    parser.add_argument(
        "--sync-skills",
        action="store_true",
        help="also synchronize .claude/skills into .agents/skills",
    )
    args = parser.parse_args()

    skill_drift = sync_skills(args.check) if args.sync_skills else False

    markdown_paths = sorted(CLAUDE_AGENT_DIR.glob("*.md"))
    expected_names = {path.stem for path in markdown_paths}
    actual_names = {path.stem for path in CODEX_AGENT_DIR.glob("*.toml")}
    if expected_names != actual_names:
        missing = sorted(expected_names - actual_names)
        extra = sorted(actual_names - expected_names)
        print(f"Agent file-set mismatch: missing={missing}, extra={extra}")
        return 1

    stale: list[Path] = []
    for markdown_path in markdown_paths:
        toml_path = CODEX_AGENT_DIR / f"{markdown_path.stem}.toml"
        expected = expected_toml(markdown_path, toml_path)
        current = toml_path.read_text(encoding="utf-8")
        if current == expected:
            continue
        stale.append(toml_path)
        if not args.check:
            toml_path.write_text(expected, encoding="utf-8")

    if stale:
        action = "Stale" if args.check else "Updated"
        for path in stale:
            print(f"{action}: {path.relative_to(REPO_ROOT)}")
        return 1 if args.check else 0

    print(f"All {len(markdown_paths)} Codex agent mirrors are current.")
    return 1 if args.check and skill_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
