#!/usr/bin/env python3
"""Validate static harness criteria from issues #1 and #2."""

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


def require_count_at_least(path: str, needle: str, minimum: int) -> None:
    count = text(path).count(needle)
    if count < minimum:
        failures.append(
            f"{path}: expected at least {minimum} occurrences of {needle!r}, got {count}"
        )


def require_order(path: str, *needles: str) -> None:
    body = text(path)
    cursor = -1
    for needle in needles:
        position = body.find(needle, cursor + 1)
        if position < 0:
            failures.append(f"{path}: missing ordered text {needle!r}")
            return
        if position <= cursor:
            failures.append(f"{path}: out-of-order text {needle!r}")
            return
        cursor = position


def section(path: str, start: str, end: str) -> str:
    body = text(path)
    start_at = body.find(start)
    end_at = body.find(end, start_at + len(start)) if start_at >= 0 else -1
    if start_at < 0 or end_at < 0:
        failures.append(f"{path}: cannot resolve section {start!r} -> {end!r}")
        return ""
    return body[start_at:end_at]


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

    # Issue #2 — season rollup, character growth, bounded context, and archives.
    require(
        orchestrator,
        "## Phase 8.7",
        "G7.7",
        "season_summary.md",
        "P04_continuity/sNN/_archive/",
        "P04_continuity/sNN/chapters/_archive/",
        "rollup_log.md",
        "`auto` 모드에서도 G7.7은 항상 정지",
        "인물 추가·카드 수정",
        "아카이브된 시즌이면 `_archive/`에서 해당 챕터 배관 파일을 먼저 복원",
    )
    require_order(orchestrator, "## Phase 8.5", "## Phase 8.7", "## Phase 9")
    gate_definition = section(orchestrator, "### 게이트 정의", "### 진행 모드")
    if "| G7.7 | Phase 8.7 완료 후 | 정지 |" not in gate_definition:
        failures.append(f"{orchestrator}: gate definition missing exact G7.7 stop row")
    gate_status = section(orchestrator, "### 게이트 상태 파일", "### 사용자 퇴고 루프")
    if "| G7.7 | 대기 |" not in gate_status:
        failures.append(f"{orchestrator}: gate status template missing G7.7 row")
    execution_summary = section(orchestrator, "## 실행 모드 요약", "## Phase 0")
    if "| 8.7 | 시즌 롤업 | 순차 서브 에이전트 2단계 | G7.7 |" not in execution_summary:
        failures.append(f"{orchestrator}: execution summary missing Phase 8.7 row")
    phase_4 = section(orchestrator, "## Phase 4", "## Phase 5")
    if "Phase 8.7 시즌 롤업과 G7.7 승인을 먼저 완료한다" not in phase_4:
        failures.append(f"{orchestrator}: Phase 4 can start before rollup approval")
    phase_3 = section(orchestrator, "## Phase 3", "## Phase 4")
    for needle in ("characters/README.md", "시즌 씨앗에 등장하는 조연 카드", "무관한 시즌의 `supporting_sNN.md`는 열지 않는다"):
        if needle not in phase_3:
            failures.append(f"{orchestrator}: Phase 3 input is not selective: {needle!r}")
    phase_6 = section(orchestrator, "## Phase 6", "## Phase 7")
    if "시즌 끝의 남은 배치가 1~2화여도 완료 직후 같은 G6를 실행한다" not in phase_6:
        failures.append(f"{orchestrator}: final partial chapter batch can bypass G6")
    phase_7 = section(orchestrator, "## Phase 7", "## Phase 8:")
    for needle in (
        "critical_status.md",
        "open / resolved / user_accepted",
        "승인 일시·게이트",
        "근거 없이 삭제하지 않는다",
    ):
        if needle not in phase_7:
            failures.append(f"{orchestrator}: Phase 7 missing Critical contract {needle!r}")
    phase_85 = section(orchestrator, "## Phase 8.5", "## Phase 8.7")
    for needle in ("시즌제 작품은 Phase 8.7로 진행", "단권(`s01` 단독) 작품만 G8로 진행"):
        if needle not in phase_85:
            failures.append(f"{orchestrator}: Phase 8.5 missing route {needle!r}")
    if "`gate_status.md`를 갱신하고 G8로 진행한다" in phase_85:
        failures.append(f"{orchestrator}: Phase 8.5 still bypasses Phase 8.7")
    phase_87 = section(orchestrator, "## Phase 8.7", "## Phase 9")
    for needle in (
        "남은 계획 시즌",
        "마지막 계획 시즌이면",
        "`s{N+1}` 성장 방향을 생성하지 않고",
        "사전 검사",
        "새 활성 추적 파일 전체",
        "pre_rollup_snapshot/",
        "커밋 롤백",
        "style_log_sNN.md",
        "critical_status.md",
        "원본 로그보다 상태 파일이 오래되었으면",
        "아카이브를 시작하지 않는다",
        "마지막 계획 시즌이면 최종 챕터 값을 유지하고 리셋하지 않는다",
        "## 품질 게이트 상태",
        "미회수·이월 복선 행 전체",
        "인물 카드 갱신을 포함한 어떤 쓰기도 시작하지 않는다",
        "프로젝트 상대 경로를 보존",
        "{CCC}_draft*.md",
        "{CCC}_final_v*.md",
        "카드·색인·관계·용어집·추적·Critical 상태 파일",
        "향후 시즌 계획에 있는 표기는 미사용으로 보지 않는다",
        "각 조작 **전에**",
    ):
        if needle not in phase_87:
            failures.append(f"{orchestrator}: Phase 8.7 missing contract {needle!r}")
    phase_9 = section(orchestrator, "## Phase 9", "## 에러 핸들링")
    for needle in (
        "critical_status.md",
        "파일이 없거나",
        "오래되었거나",
        "`open` 항목",
        "`user_accepted`",
        "승인 일시·게이트 근거",
    ):
        if needle not in phase_9:
            failures.append(f"{orchestrator}: G8 missing Critical contract {needle!r}")
    require(
        ".claude/agents/continuity-keeper.md",
        "### 인물 등재 추적",
        "### 카드 미등재 인물",
        "season_summary.md",
        "rollup_log.md",
    )
    require(
        ".claude/skills/narrative-review/SKILL.md",
        "### 축 6 — 인물 성장 곡선",
        "카드 미등재 인물 후보",
        "계획 방향 | 실제 변화 | 일치 여부",
    )
    for path in (".claude/skills/novel-planning/SKILL.md", ".claude/agents/story-bible-planner.md"):
        require(
            path,
            "## 시즌별 상태 변화",
            "### sNN 성장 방향",
            "supporting_sNN.md",
            "characters/README.md",
            "마지막 계획 시즌이면",
            "`s{N+1}` 방향을 생성하지 않고",
            "결과를 원본 경로에 직접 쓰지 않는다",
            ".staging/new-active/",
            "프로젝트 상대 경로 그대로",
            "신설/교체 대상 목록",
        )
        require_count_at_least(path, "## 시즌별 상태 변화", 2)
    for path in (
        ".claude/agents/chapter-novelist.md",
        ".claude/agents/continuity-keeper.md",
        ".claude/agents/novel-style-guardian.md",
        ".claude/agents/chapter-plotter.md",
        ".claude/agents/season-planner.md",
    ):
        require(path, "continuity_log.md", "season_summary.md", "_archive/", "characters/README.md")
        forbid(path, "`{slug}/P02_bible/characters/*.md`")
    require(
        ".claude/agents/novel-style-guardian.md",
        "style_log_sNN.md",
        "축 6 인물 성장 곡선",
    )
    require(
        ".claude/agents/continuity-keeper.md",
        "style_log_sNN.md",
        "critical_status.md",
        "critical_status_sNN.md",
        "파일이 누락·오래되었거나 `open`이 있으면",
        "마지막 계획 시즌이면 최종 챕터 값을 유지하고 리셋하지 않는다",
        "미완료 `pending` 저널",
        "인물 카드 갱신을 포함한 어떤 쓰기도 시작하지 않는다",
        "미회수·이월 복선 행 전체",
        "{CCC}_draft*.md",
        "{CCC}_final_v*.md",
        "카드·색인·관계·용어집·추적·Critical 상태 파일",
        "현재 및 향후 시즌 계획 어디에도 쓰이지 않은 용어",
        "사전 검사",
        "새 활성 추적 파일",
        "pre_rollup_snapshot/",
        "커밋 롤백",
    )
    for path in (
        ".claude/skills/novel-chapter-writing/SKILL.md",
        ".claude/agents/chapter-prose-reviser.md",
        ".claude/skills/novel-prose-revision/SKILL.md",
    ):
        require(path, "characters/README.md", "supporting_sNN.md", "season_summary.md", "명시적으로 요청")
        forbid(path, "characters/*.md")
    require(
        ".claude/skills/novel-illustration/SKILL.md",
        "characters/README.md",
        "삽화 후보 장면에 등장하는 인물 카드만",
        "supporting_sNN.md",
    )
    forbid(".claude/skills/novel-illustration/SKILL.md", "characters/*.md")
    require(track_a, "chapters/_archive/", "사전 검사", "롤백", "기존 아카이브 파일을 덮어쓰지 않는다")
    require(track_a, "*_draft*.md", "*_final_v*.md", "미완료 이동 저널", "예상 바이트")
    require(
        ".claude/agents/editor.md",
        "chapters/_archive/",
        "배관 파일 무손실 아카이브",
        "사전 검사",
        "롤백",
        "*_draft*.md",
        "*_final_v*.md",
        "미완료 저널",
    )

    if failures:
        print("Harness validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "Issue #1 WP1-WP12 and issue #2 WP15-WP20 static acceptance criteria passed. "
        "WP21 actual pilot A/B is not covered."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
