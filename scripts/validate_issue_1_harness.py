#!/usr/bin/env python3
"""Validate the static acceptance criteria from GitHub issue #1 (WP1-WP12)."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
failures: list[str] = []


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(path: str, *needles: str) -> None:
    body = text(path)
    for needle in needles:
        if needle not in body:
            failures.append(f"{path}: missing {needle!r}")


def forbid(path: str, *needles: str) -> None:
    body = text(path)
    for needle in needles:
        if needle in body:
            failures.append(f"{path}: forbidden text remains: {needle!r}")


def validate_skill_mirrors() -> None:
    claude_root = ROOT / ".claude" / "skills"
    agents_root = ROOT / ".agents" / "skills"
    claude = {p.relative_to(claude_root): p for p in claude_root.rglob("*") if p.is_file()}
    agents = {p.relative_to(agents_root): p for p in agents_root.rglob("*") if p.is_file()}
    if claude.keys() != agents.keys():
        failures.append("WP1: .claude/skills and .agents/skills file sets differ")
        return
    for rel in sorted(claude):
        if claude[rel].read_bytes() != agents[rel].read_bytes():
            failures.append(f"WP1: skill mirror differs: {rel}")


def validate_agent_contracts() -> None:
    claude_agents = sorted((ROOT / ".claude" / "agents").glob("*.md"))
    codex_agents = sorted((ROOT / ".codex" / "agents").glob("*.toml"))
    if len(claude_agents) != 21 or len(codex_agents) != 21:
        failures.append(
            f"WP5: expected 21 Claude and 21 Codex agents, got "
            f"{len(claude_agents)} and {len(codex_agents)}"
        )
    for path in claude_agents:
        body = path.read_text(encoding="utf-8")
        for needle in ("### 반환 형식", "**상태:**", "**산출 파일:**", "**핵심 요약:**"):
            if needle not in body:
                failures.append(f"WP5: {path.relative_to(ROOT)} missing {needle!r}")
    for path in codex_agents:
        body = path.read_text(encoding="utf-8")
        if "Never return an artifact body in full" not in body or "### 반환 형식" not in body:
            failures.append(f"WP5: {path.relative_to(ROOT)} return contract is stale")


def main() -> int:
    validate_skill_mirrors()

    orchestrator = ".claude/skills/lightnovel-writing-orchestrator/SKILL.md"
    require(
        orchestrator,
        "## 진행 게이트와 보고 형식",
        "G1",
        "G2",
        "G3",
        "G4",
        "G5",
        "G6",
        "G7.5",
        "G7",
        "G8",
        "15줄 이내 다이제스트",
        "P00_meta/gate_status.md",
        "### 사용자 퇴고 루프",
        "voice_profile.md",
        "품질 하락 추세",
        "proofread_log.md",
        "glossary.md",
    )
    forbid(orchestrator, "Codex", "gpt-5")

    require(
        "style-guides/lightnovel-style-guide.md",
        "장면 vs 요약",
        "서브텍스트",
        "### 초반부 특칙",
        "요약 서술 (Summary Narration)",
    )
    require(".claude/skills/novel-chapter-writing/SKILL.md", "### 단계 0 — 씬 카드 분해", "### 씬 카드")
    require(".claude/agents/chapter-novelist.md", "장면화 원칙", "캐릭터 고유 어투·행동", "glossary.md")
    require(".claude/agents/chapter-prose-reviser.md", "사용자 퇴고 루프 라운드")

    validate_agent_contracts()

    require(".claude/agents/season-planner.md", "### 챕터 규격", "4,500~5,500자", "30~50%")
    require(".claude/agents/chapter-plotter.md", "분량 계획", "리텐션 장치")
    require(".claude/agents/novel-style-guardian.md", "행동 일관성", "요약 서술", "분량", "시즌 통독 모드")
    require(".claude/skills/narrative-review/SKILL.md", "## 섹션 5: 시즌 통독 검수", "핵심 소재가 도달하지 않음")
    for path in (".claude/skills/novel-planning/SKILL.md", ".claude/agents/story-bible-planner.md"):
        require(path, "성격 키워드", "습관적 동작·버릇", "감정 반응 패턴", "glossary.md")
    require(".claude/agents/continuity-keeper.md", "새로 드러난 버릇·행동 패턴", "### 용어집 추적")

    track_a = ".claude/skills/book-writing-orchestrator/SKILL.md"
    require(track_a, "GA1", "GA2", "GA3", "style_notes.md", "proofread_log.md")
    forbid(track_a, "Phase 7-2", "Codex", "gpt-5")
    require("CLAUDE.md", "## 공통 실행 원칙", "하네스 원본은 `.claude/`")
    require("scripts/validate_harness_frontmatter.py", "validate_skill_mirrors", "orchestrator_path")

    require(
        ".claude/agents/interior-illustrator.md",
        "prompt_ready",
        "image_missing",
        "generated",
        "user_provided",
        "excluded",
    )
    require(".claude/skills/novel-illustration/SKILL.md", "이미지 생성 수단", "generated", "excluded")
    require(".claude/agents/novel-editor.md", "P02_bible/glossary.md", "proofread_log.md", "교열과 윤문 분리")
    require(".claude/agents/editor.md", "proofread_log.md", "교열과 윤문 분리")

    if failures:
        print("Issue #1 harness validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("Issue #1 WP1-WP12 static acceptance criteria passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
