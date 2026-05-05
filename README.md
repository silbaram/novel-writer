# Novel Writer — 투트랙 저술 자동화 하네스

주제/아이디어를 던지면 리서치부터 EPUB 빌드까지 한 번에 수행하는 **에이전트 하네스**다. **기술서/논픽션**과 **라노벨/소설** 두 트랙이 독립적으로 공존한다.

- **Repo:** https://github.com/silbaram/novel-writer
- **실행 환경:** [Claude Code](https://claude.com/claude-code) + Claude Agent SDK
- **저자 모델:** Claude Opus (하네스 내 모든 에이전트가 `model: opus` 사용)

---

## 트랙 A: 기술서/논픽션 하네스

주제가 주어지면 리서치 → 저술 계획 → 계획 리뷰 → 챕터 저술(Toby 문체) → EPUB 빌드까지 자동 수행한다.

### 빠른 시작

```
주제: 효과적인 SQL 쿼리 튜닝
주요 내용: 실행 계획 읽기, 인덱스 설계, N+1 회피, 실전 사례
대상 독자: 백엔드 주니어 개발자 (SQL 기본은 아는 수준)
분량: 150페이지 정도
이 주제로 책 써줘.
```

### 워크플로우

| Phase | 담당 에이전트 | 내용 |
|-------|------------|------|
| 1. 리서치 | `research-lead` → `web/paper/community-researcher` 병렬 | `01_reference.md` 작성 |
| 2. 저술 계획 | `book-planner` | `02_plan.md` 작성 |
| 3. 계획 리뷰 | `book-planner` ↔ `plan-reviewer` (최대 2회 왕복) | `02_plan.md` 확정 + 사용자 승인 |
| 4. 챕터 저술 | `chapter-writer` × N + `style-guardian` | `{NN}_draft.md` → `{NN}_final.md` |
| 5. 통합 편집 | `editor` | `04_manuscript.md` + `book_manifest.json` |
| 6. EPUB 빌드 | `cover-designer` → `epub-builder` | EPUB + 책 소개 markdown |

### 스타일 가이드

`style-guides/toby-book-writing-style.md`가 기본 문체 기준이고, `.claude/skills/chapter-writing/references/toby-style-guide.md`가 확장 체크리스트다. 이 파일을 수정하면 저술 톤이 바뀐다.

### 기대 산출물

```
{slug}/
├── 01_reference.md
├── 02_plan.md
├── 03_review_log.md
├── chapters/
│   ├── 01_draft.md / 01_final.md
│   └── ...
├── 04_manuscript.md
├── style_log.md
├── book_manifest.json
├── cover.png
└── build_log.md

{책-제목}-v1.0.0.epub
{책-제목}-v1.0.0.md
```

---

## 트랙 B: 라노벨/소설 하네스

소설 아이디어를 던지면 스토리 바이블부터 EPUB까지 자동으로 수행한다.

### 빠른 시작

```
장르: 이세계 판타지 라노벨
구조: 시즌제 / 시즌 수: 3
주인공: 현실에서 서버 개발자였던 남자
핵심 설정: 이세계에서 마법 대신 시스템 로그를 읽을 수 있다
저자: silbaram

이 설정으로 라노벨을 기획하고 시즌 1부터 집필해줘.
```

### 워크플로우

| Phase | 담당 에이전트 | 내용 |
|-------|------------|------|
| 0. 분석 | 인라인 | 요청 파싱, 슬러그 생성 |
| 1. 리서치 | `web/paper/community-researcher` 병렬 | `01_reference.md` |
| 2. 스토리 바이블 | `story-bible-planner` ↔ `story-bible-reviewer` (최대 2회) | `02_story_bible.md` + 캐릭터·세계관 파일 |
| 3. 시즌 구조 | `season-planner` | `03_season_plan.md` + `seasons/sNN/season_bible.md` |
| 4. 챕터 플롯 | `chapter-plotter` | `seasons/sNN/chapter_plan.md` |
| 5. 플롯 리뷰 | `story-bible-reviewer` + `continuity-keeper` | `05_review_log.md` |
| 6. 챕터 집필 | `chapter-novelist` × 3 병렬 → `novel-style-guardian` → `continuity-keeper` | `{CCC}_draft.md` → `{CCC}_final.md` |
| 7. 시즌 검수 | `novel-style-guardian` + `continuity-keeper` | `style_log.md` + `continuity/` |
| 8. 통합 편집 | `novel-editor` | `04_manuscript.md` + `book_manifest.json` |
| 9. EPUB 빌드 | `cover-designer` → `epub-builder` | EPUB + 책 소개 markdown |

### 스타일 가이드

`style-guides/lightnovel-style-guide.md`가 모든 챕터 집필의 제약 조건이다.

### 기대 산출물

```
{slug}/
├── 02_story_bible.md / .json
├── characters/ worldbuilding/ relationships.md
├── seasons/s01/
│   ├── season_bible.md
│   ├── chapter_plan.md
│   └── chapters/ 001_draft.md / 001_final.md ...
├── continuity/
├── 04_manuscript.md
├── book_manifest.json
├── cover.png
└── build_log.md

{작품-제목}-v1.0.0.epub
{작품-제목}-v1.0.0.md
```

---

## 사전 준비

| 도구 | 용도 | 설치 |
|------|------|------|
| [Claude Code](https://claude.com/claude-code) | 하네스 실행 환경 | 공식 가이드 참조 |
| `pandoc` ≥ 3.0 | EPUB 생성 | `brew install pandoc` |
| `python3` ≥ 3.8 | 빌드 스크립트 | macOS 기본 제공 |
| `epubcheck` (선택) | EPUB 검증 | `brew install epubcheck` |
| `imagemagick` (선택) | 표지 폴백 | `brew install imagemagick` |

## 설치

```bash
git clone https://github.com/silbaram/novel-writer.git
cd novel-writer
```

## 디렉토리 구조

```
novel-writer/
├── CLAUDE.md                              # 하네스 포인터 (새 세션 자동 로드)
├── README.md
├── style-guides/
│   ├── toby-book-writing-style.md         # 기술서 Toby 문체 가이드
│   └── lightnovel-style-guide.md          # 라노벨 문체 가이드
└── .claude/
    ├── agents/                             # 19개 에이전트
    │   ├── [기술서] book-planner, chapter-writer, editor, plan-reviewer, style-guardian, research-lead
    │   ├── [라노벨] chapter-novelist, chapter-plotter, novel-editor, novel-style-guardian,
    │   │           season-planner, story-bible-planner, story-bible-reviewer, continuity-keeper
    │   └── [공용]   web-researcher, paper-researcher, community-researcher, cover-designer, epub-builder
    └── skills/                             # 17개 스킬
        ├── [기술서] book-writing-orchestrator, book-planning, book-editing,
        │           chapter-writing/, plan-review, style-review
        ├── [라노벨] lightnovel-writing-orchestrator, novel-planning, novel-chapter-writing,
        │           novel-editing, narrative-review
        └── [공용]   research-coordination, web-research, paper-research,
                    community-research, cover-design, epub-build/
```

## 트러블슈팅

### "pandoc: command not found"
```bash
brew install pandoc
```

### EPUB 크기 50KB 미만 경고
`{slug}/build_log.md`와 `.pandoc_err` 확인.

### 에이전트/스킬 파일 편집 후 프론트매터 오류 의심 시
```bash
python3 scripts/validate_harness_frontmatter.py
```

## 라이선스

MIT License. 전문은 [LICENSE](LICENSE) 참조.

## 크레딧

하네스 설계: silbaram + Claude Opus
