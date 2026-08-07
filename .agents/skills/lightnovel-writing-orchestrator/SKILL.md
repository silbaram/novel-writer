---
name: lightnovel-writing-orchestrator
description: Use for 소설/라노벨 Korean fiction workflows from premise to EPUB, including story bible, seasons, chapters, review, cover, and build.
---

# Lightnovel Writing Orchestrator

장르·분위기·주인공 아이디어를 받아 스토리 바이블 → 시즌 구조 → 챕터 집필 → EPUB 빌드까지 전 과정을 조율한다. 각 Phase에서 전문 에이전트를 호출하고, 중간 산출물을 `{slug}/` 하위에 축적한 뒤 최종 EPUB을 프로젝트 루트에 만든다.

> **저작권 원칙:** 기존 저작물(소설·웹툰·게임·애니메이션 등)의 캐릭터·세계관·고유 설정·문장을 허가 없이 복사하거나 직접 전용하지 않는다. 오마주·패러디를 의도하더라도 독립적 설정으로 치환한다. 이 원칙은 모든 Phase의 에이전트에 공통 적용된다.

---

## 산출물 디렉터리 원칙

라노벨 프로젝트는 `{slug}/` 루트에 Phase 파일을 직접 흩뿌리지 않는다. 목적별 묶음 디렉터리에 저장한다.

| 경로 | 역할 | 대표 파일 |
|------|------|-----------|
| `{slug}/P00_meta/` | 게이트 상태와 실행 메타데이터 | `gate_status.md` |
| `{slug}/P01_research/` | Phase 1 리서치 | `01_reference.md` |
| `{slug}/P02_bible/` | Phase 2 스토리 바이블과 설정 | `02_story_bible.md`, `02_story_bible.json`, `voice_profile.md`, `glossary.md`, `relationships.md`, `open_questions.md`, `season_seeds.md` |
| `{slug}/P02_bible/characters/` | 인물 카드 | `protagonist.md`, `heroine.md`, `supporting.md` |
| `{slug}/P02_bible/worldbuilding/` | 세계관 규칙과 세력/장소 | `world_rules.md`, `system_rules.md`, `factions.md`, `locations.md` |
| `{slug}/P03_planning/` | Phase 3~4 시즌/챕터 설계 | `03_season_plan.md`, `04_chapter_plan.md` |
| `{slug}/P03_planning/sNN/` | 시즌별 바이블·챕터 플랜·종료 요약 | `season_bible.md`, `chapter_plan.md`, `season_summary.md` |
| `{slug}/P04_continuity/sNN/` | 챕터 원고와 내부 검수 산출물 | `chapters/*_final.md` (승인 전: `*_draft.md`, `*_review.md`, `*_revised*.md`, `*_review2.md`, `*_user_review*.md`) |
| `{slug}/P04_continuity/sNN/_archive/` | 종료 시즌의 추적 원본 | `continuity_log_sNN.md`, `timeline_sNN.md`, `foreshadowing_tracker_sNN.md`, `character_state_table_sNN_end.md` |
| `{slug}/P04_continuity/sNN/chapters/_archive/` | 종료 시즌의 챕터 배관·백업 파일 | `*_draft*.md`, `*_review*.md`, `*_user_review*.md`, `*_revised*.md`, `*_final_v*.md` |
| `{slug}/P04_continuity/` | 연속성 추적 | `continuity_log.md`, `timeline.md`, `foreshadowing_tracker.md`, `character_state_table.md` |
| `{slug}/P00_meta/logs/` | 검수/편집/롤업/빌드 로그 | `05_review_log.md`, `style_log_sNN.md`, `critical_status.md`, `rollup_log.md`, `editor_notes.md`, `build_log.md` |
| `{slug}/P05_manuscript/` | 출판/EPUB용 최종 원고와 메타데이터 | `04_manuscript.md`, `book_manifest.json`, `s01/season_manuscript.md` |
| `{slug}/P06_publication/assets/` | 표지 등 출판용 공용 이미지 | `cover.png` |
| `{slug}/P06_publication/illustrations/` | 본문 삽화 계획, 프롬프트, 외부 생성 이미지 | `illustration_plan.md`, `style_sheet.md`, `s01/*_prompt.md` |

새 프로젝트 생성 시 이 디렉터리를 먼저 만들고, `PROJECT_LAYOUT.md`에 현재 구조를 기록한다.

---

## 에이전트 통신 원칙

**모든 에이전트 간 통신은 오케스트레이터가 중계한다.** 서브에이전트는 다른 에이전트에게 직접 메시지를 보낼 수 없다. 에이전트는 결과를 파일에 저장하고 반환값(result)으로 오케스트레이터에게 돌려준다. 오케스트레이터가 그 결과를 다음 에이전트 프롬프트에 실어 순차적으로 호출한다.

```
[오케스트레이터] → Agent(A) → 파일 저장 + 반환
[오케스트레이터] → A의 반환값을 읽어 Agent(B) 프롬프트에 포함 → Agent(B) → 파일 저장 + 반환
```

에이전트 파일의 "팀 통신 프로토콜" 섹션이 직접 메시지 전달을 언급하더라도, 실제 실행에서는 이 원칙을 따른다. 오케스트레이터가 라우팅 책임을 전담한다.

---

## 진행 게이트와 보고 형식

### 보고 형식 규칙 (모든 Phase 공통)

1. **산출물 전문을 채팅에 출력하지 않는다.** 모든 산출물은 파일에 저장하고 경로만 보고한다.
2. **게이트 보고는 15줄 이내 다이제스트**로 한다. 요약 + 파일 경로 + 판정/선택지만 포함한다.
3. 사용자가 특정 파일을 명시적으로 요청할 때만 그 내용을 보여준다.
4. 서브에이전트 반환값은 각 에이전트의 `반환 형식` 계약을 따른다. 산출물 전문을 반환값에 포함하지 않는다.

### 게이트 정의

| 게이트 | 시점 | 정지 유형 | 보고 내용 |
|--------|------|----------|----------|
| G1 | Phase 0 완료 후 | 정지 | 요청 해석 표: 장르·주인공·분량·시즌 |
| G2 | Phase 2 완료 후 | 정지 | 바이블 다이제스트: logline 1줄, 주인공 3줄, 핵심 인물 1줄씩 최대 4명, 세계 규칙 3줄, 시즌 씨앗 목록 |
| G3 | Phase 4 완료 후 | 정지 | 시즌 아크 요약 + 챕터당 1줄 요약표(제목·핵심 사건·훅 유형) |
| G4 | Phase 5 완료 후 | 조건부 정지 | 검증 판정. Critical이 있으면 정지하고, 없으면 보고 후 진행 |
| G5 | 1화 파일럿 2차 검수 완료 후 | 정지 | 파일럿 경로(`revised`) + 문체 확인 요청. **승인 시 final 생성.** 승인 전 배치 집필 금지 |
| G6 | 이후 3화 배치마다 | 정지 | 진행표(챕터·자수·검수 상태·미해결) + 계속/수정 선택. **승인 시 배치 final 일괄 생성** |
| G7 | Phase 8 완료 후 | 정지 | 시즌 검수·교열 요약 + 통합 원고 경로 |
| G7.5 | Phase 8.5 완료 후 | 정지 | 삽화 슬롯·이미지 상태 + 슬롯별 승인/수정/제외 선택 |
| G7.7 | Phase 8.7 완료 후 | 정지 | 시즌 롤업 다이제스트: 카드·성장 방향·압축·아카이브 결과 |
| G8 | Phase 9 실행 전 | 조건부 정지 | Critical 미해결 시 빌드 금지 |

G2에서 표시하는 핵심 인물 4명은 다이제스트 표시 상한일 뿐 등장인물 수 제한이 아니다. 전체 캐스트는 `P02_bible/characters/`에 인원 제한 없이 정의하고, 5명 이상이면 `외 조연 N명 — supporting.md 참조`로 표시한다.

위 게이트는 전부 적용한다. 건너뛰기 옵션은 없다 — 소설은 사용자가 각 게이트에서 직접 읽고 판단해야 하는 산출물이기 때문이다.

### 게이트 상태 파일

`{slug}/P00_meta/gate_status.md`에 게이트 통과를 즉시 기록한다. 새 세션에서 `이어서 진행` 요청을 받으면 이 파일을 먼저 읽고 마지막 통과 게이트 다음부터 재개한다.

```markdown
# Gate Status
- 현재 위치: G5 대기 (s01 001화 파일럿 완성)

| 게이트 | 상태 | 일시 | 비고 |
|--------|------|------|------|
| G1 | 통과 | 2026-07-21 | 시즌 1개, 20챕터 |
| G2 | 통과 | 2026-07-21 | 바이블 v1 승인 |
| G3 | 대기 | | |
| G4 | 대기 | | |
| G5 | 대기 | | |
| G6 | 대기 | | |
| G7 | 대기 | | |
| G7.5 | 대기 | | |
| G7.7 | 대기 | | |
| G8 | 대기 | | |
```

### 사용자 퇴고 루프

퇴고 루프는 두 종류다.

| 루프 | 주체 | 상한 |
|------|------|------|
| 내부 자동 루프 | 에이전트 간 (`novel-style-guardian` ↔ `chapter-prose-reviser`) | 2회 |
| 사용자 퇴고 루프 | 사용자 피드백 | 없음 — 사용자가 승인할 때까지 반복 |

사용자 퇴고 루프는 G5·G6·G7·G7.5·G7.7과 완료 후 부분 재실행에서 동일하게 적용한다.

1. 피드백을 분류한다. (문장·문체·리듬 / 사건·전개·씬 구조 / 전역 문체 규칙 / 설정·Canon)
2. **피드백을 review 규약으로 변환해 `{CCC}_user_review{N}.md`에 기록한다.** 사용자에게 형식을 요구하지 않고 오케스트레이터가 변환한다. 형식은 `{CCC}_review.md`와 동일하며 각 항목에 원문 인용·문제 유형·보존해야 할 의도·퇴고 방향을 포함하고, 사용자 발언 원문도 함께 남긴다.
3. 유형별로 라우팅한다.
   - 문장·문체·리듬 → `chapter-prose-reviser`에 마지막 퇴고본과 `{CCC}_user_review{N}.md`를 전달해 다음 미사용 번호의 `{CCC}_revised{N}.md`를 만든다. 표준 순서는 `{CCC}_user_review1.md → {CCC}_revised2.md → {CCC}_user_review2.md → {CCC}_revised3.md`이다. 내부 보정으로 출력 번호가 이미 사용됐으면 기존 파일을 덮어쓰지 않고 그 다음 미사용 번호를 쓴다.
   - 사건·전개·씬 구조 → `chapter-novelist` 부분 재집필 후 검수·퇴고를 재통과한다.
   - 전역 문체 규칙 → `voice_profile.md`의 `## 사용자 피드백 보정`에 규칙으로 추가하고 해당 챕터를 재퇴고한다. 확정된 다른 챕터 소급 여부는 사용자에게 확인한다.
   - 설정·Canon → 파급 범위를 다이제스트로 보고하고 승인 후 `story-bible-planner`로 개정한다.
4. 챕터 플랜과 어긋나는 사건·구조 수정은 `chapter_plan.md` 갱신 여부를 확인한다.
5. 라운드 이력을 현재 시즌의 `P00_meta/logs/style_log_sNN.md`에 1줄 기록한다. **승인 전에는 `_v{N}` 백업을 만들지 않는다** — 각 라운드가 별도 `{CCC}_revised{N}.md` 파일로 남으므로 백업이 중복이다.
6. 변경 다이제스트(무엇을 왜 어떻게, 5줄 이내)와 파일 경로만 재제시한다.
7. 사용자가 승인하면 아래 final 생성 절차 또는 Phase 6의 승인 절차를 따른다. 추가 피드백이 오면 2로 돌아간다.

### final 생성 이후의 수정

`{CCC}_final.md`가 이미 존재하는 상태에서 수정 요청이 오면 승인된 산출물을 되돌리는 것이므로 아래를 따른다.

1. 수정 전 `{CCC}_final.md`를 `{CCC}_final_v{N}.md`로 백업한다.
2. 수정 사유·범위·요청자를 `{CCC}_final.md` 본문 끝 저자 노트의 `### 승인 후 수정 이력`에 append한다.

   | 라운드 | 일시 | 게이트 | 요청 내용 | 변경 범위 | 백업 |
   |--------|------|--------|----------|----------|------|

3. 사건·구조 변경이면 `continuity-keeper`를 재호출해 연속성을 재갱신한다.
4. 변경 다이제스트를 5줄 이내로 재제시하고 재승인을 받는다.

**승인 전 라운드와 구분한다.** 승인 전에는 `_revised{N}.md`가 이력을 담당하므로 `_v{N}` 백업을 만들지 않는다. `_v{N}`은 승인 후 수정에만 쓴다.

---

## 실행 모드 요약

| Phase | 이름 | 실행 모드 | 게이트 |
|-------|------|----------|--------|
| 0 | 소설 요청 분석 | 인라인 | G1 |
| 1 | 소재/세계관 리서치 | 서브 에이전트 (병렬 가능) | - |
| 2 | 스토리 바이블 작성 | 단일 서브 → 오케스트레이터 중계 왕복 | G2 |
| 3 | 시즌 구조 설계 | 단일 서브 | - |
| 4 | 챕터 플롯 작성 | 단일 서브 (시즌별 순차) | G3 |
| 5 | 집필 전 종합 검증 | 순차 서브 에이전트 4단계 | G4 |
| 6 | 챕터 집필 | 파일럿 단독 → 배치 순환 | G5·G6 |
| 7 | 문체/연속성 검수 | 순차 서브 에이전트 (시즌 전체 관점) | - |
| 8 | 통합 편집·교열 | 단일 서브 | G7 |
| 8.5 | 본문 삽화 | 서브 에이전트 + 가용 시 이미지 생성 | G7.5 |
| 8.7 | 시즌 롤업 | 순차 서브 에이전트 2단계 | G7.7 |
| 9 | 표지 + EPUB 빌드 | 서브 에이전트 | G8 |

---

## Phase 0: 소설 요청 분석

**실행 모드:** 인라인

사용자 입력에서 다음 항목을 추출한다. 항목이 불명확하거나 누락된 경우 사용자에게 짧게 확인한다. 핵심 항목(장르·핵심 아이디어·주인공)이 없으면 Phase 1로 진행하지 않는다.

| 추출 항목 | 기본값 / 처리 |
|----------|-------------|
| 작품 장르 | 미지정 시 질문 |
| 핵심 아이디어 | 미지정 시 질문 |
| 주인공 | 미지정 시 Phase 2에서 설계 |
| 주요 갈등 | 미지정 시 Phase 2에서 설계 |
| 분위기/톤 | 미지정 시 Phase 2에서 설계 |
| 대상 독자 | 미지정 시 "일반 성인 웹소설 독자"로 가정 |
| 분량 | 미지정 시 "챕터 10개 이상" 기본값 |
| 시즌제 여부 | 미지정 시 단시즌 (`s01`) |
| 시즌 수 | 시즌제 미지정 시 `1` |
| 권/챕터 수 | 미지정 시 시즌당 20챕터 기본값 |
| 시점 | 미지정 시 "1인칭 주인공" 기본값 |
| 저자명 | 미지정 시 기본값 `AI-Author` |

**슬러그 생성:** 작품 핵심 키워드로 영문 슬러그를 만든다. 예: `회귀한 마검사` → `regression-swordmaster`.

**기존 산출물 확인:**
- `{slug}/` 미존재 → 초기 실행, Phase 1부터 순차 실행
- `{slug}/` 존재 + `이어서 진행` 요청 → `P00_meta/gate_status.md`를 읽고 마지막 통과 게이트 다음부터 재개
- `{slug}/` 존재 + 부분 수정 요청 → 해당 Phase만 재실행 (아래 "부분 재실행 규칙" 참조)
- `{slug}/` 존재 + 새 입력 → `{slug}_prev-{timestamp}/`로 이동 후 새 실행

추출 결과를 요청 해석 표로 15줄 이내에 제시하고 정지한다(**G1**). 사용자가 승인하면 `gate_status.md`에 통과를 기록하고 Phase 1로 진행한다.

---

## Phase 1: 소재/세계관 리서치

**실행 모드:** 서브 에이전트 (병렬 가능)

**목적:** 작품의 소재·배경과 관련된 실세계 자료(역사·신화·사회·과학·장르 관행 등)를 수집한다. 완전 창작 세계관이라면 같은 장르 독자 반응·선행 작품 트렌드 리서치로 대체한다.

- `web-researcher`와 `community-researcher`를 병렬 서브에이전트로 호출한다
- 논픽션 소재가 포함된 경우(역사물·SF·무협 등) `paper-researcher`를 추가 호출한다
- 순수 창작 세계관이고 사용자가 "리서치 없이 바로 진행"을 요청한 경우 이 Phase를 건너뛰고 빈 `P01_research/01_reference.md`를 생성한 뒤 Phase 2로 이동한다

**입력:** 장르, 핵심 아이디어, 배경 설정 키워드
**출력:** `{slug}/P01_research/01_reference.md` — 세계관·소재 레퍼런스 (섹션: 장르 관행, 배경 자료, 독자 기대, 유사 작품 분석, 참고문헌)

---

## Phase 2: 스토리 바이블 작성

**실행 모드:** 단일 서브 에이전트 → 오케스트레이터 중계 왕복 (생성-검증)

픽션의 기반 설정 전체를 이 Phase에서 확정한다.

> **범위 제한:** Phase 2는 챕터별 상세 플롯을 작성하지 않는다 (Phase 4). 시즌별 상세 아크도 작성하지 않는다 (Phase 3). "어떤 세계에서, 어떤 인물이, 어떤 갈등을 가지는가"만 다룬다.

**절차:**

1. `story-bible-planner`를 호출한다. 내부 절차를 통해 스토리 바이블을 작성하고 파일로 저장한다
2. `story-bible-reviewer`를 호출한다. 8개 검토 축으로 바이블을 평가해 `{slug}/P02_bible/02_story_bible_review.md`에 저장하고 결과를 반환한다
3. 오케스트레이터가 리뷰 결과를 읽어 `story-bible-planner`를 재호출한다 (피드백 내용을 프롬프트에 포함). 최대 2회 왕복
4. `story-bible-reviewer`의 최종 판정이 **Fail**이면 사용자에게 보고하고 재작업을 요청한다. **Pass** 또는 **Conditional Pass**면 Phase 3으로 진행한다
5. **G2 게이트:** 바이블 다이제스트를 제시하고 정지한다. 전문은 파일 경로만 안내한다. 피드백이 있으면 `story-bible-planner`를 한 번 더 호출해 반영하고, 승인 후 `gate_status.md`를 갱신한다

**출력:**
- `{slug}/P02_bible/02_story_bible.md` + `{slug}/P02_bible/02_story_bible.json`
- `{slug}/P02_bible/characters/*.md`
- `{slug}/P02_bible/voice_profile.md`
- `{slug}/P02_bible/glossary.md`
- `{slug}/P02_bible/worldbuilding/*.md`
- `{slug}/P02_bible/relationships.md`
- `{slug}/P02_bible/open_questions.md`
- `{slug}/P02_bible/season_seeds.md`
- `{slug}/P02_bible/02_story_bible_review.md`

---

## Phase 3: 시즌 구조 설계

**실행 모드:** 단일 서브 에이전트

`season-planner`를 호출한다. 시즌 씨앗을 시즌 아크로 확장하고, 피날레·후킹·복선 흐름을 정의한다.

- 단권 소설은 `s01`로 처리한다
- 시즌 1은 완전 상세로 작성하고, 시즌 2 이후는 사용자가 명시적으로 요청하지 않는 한 방향/씨앗 수준으로만 작성한다

**입력:** `{slug}/P02_bible/02_story_bible.md`, `{slug}/P02_bible/02_story_bible.json`, `{slug}/P02_bible/season_seeds.md`, `characters/README.md` 색인과 주인공·주요 인물·시즌 씨앗에 등장하는 조연 카드, 세계관 파일, 요청 시즌 수. 무관한 시즌의 `supporting_sNN.md`는 열지 않는다
**출력:**
- `{slug}/P03_planning/03_season_plan.md`
- `{slug}/P03_planning/s01/season_bible.md` (시즌 1 완전 상세)
- `{slug}/P03_planning/s02/season_bible.md` (시즌 2 존재 시, 방향 수준)
- 이후 시즌도 동일 패턴

---

## Phase 4: 챕터 플롯 작성

**실행 모드:** 단일 서브 에이전트 (시즌별 순차)

`chapter-plotter`를 호출해 각 시즌의 챕터별 플롯을 설계한다. 챕터 플랜은 Phase 6의 `chapter-novelist`가 직접 참조하는 저술 지도다.

**시즌 2+ 챕터 플롯 작성 시점:**
- Phase 4 최초 실행 시 시즌 1 챕터 플롯만 작성한다. 시즌 2+는 Phase 3에서 방향 수준으로만 존재한다
- 시즌 N의 집필(Phase 6)이 완료되고 Phase 7·8을 통과한 뒤, 다음 시즌으로 진행하기 전에 해당 시즌의 Phase 4를 재실행한다
- 다음 시즌의 Phase 3 또는 Phase 4를 시작하기 전에 **Phase 8.7 시즌 롤업과 G7.7 승인을 먼저 완료한다**
- 즉, 시즌 2 챕터 플롯은 시즌 1 집필 완료 후에 작성한다. 미리 작성하지 않는다
- 이 시점에 Phase 3의 시즌 2 씨앗이 `[DRAFT]`이면 `season-planner`를 먼저 호출해 시즌 2 바이블을 완전 상세로 확장한다

**각 챕터 플랜 필수 항목:**

| 항목 | 내용 |
|------|------|
| 챕터 목적 | 이 챕터에서 서사적으로 달성해야 하는 것 |
| 등장인물 | 이 챕터에 등장하는 인물과 각자의 역할 |
| 시작 상태 | 이 챕터 시작 시점의 주인공·세계 상태 |
| 주요 사건 | 반드시 일어나야 하는 사건 목록 (순서 아님) |
| 갈등 | 이 챕터에서 활성화되는 갈등 층위 |
| 감정 변화 | 시점 인물의 감정 이동 (시작 → 종료) |
| 복선 사용 | 이 챕터에서 심을 복선 |
| 복선 회수 | 이 챕터에서 회수할 복선 |
| 챕터 엔딩 | 훅 유형과 구체적 장치 |
| 분량 계획 | 시즌 바이블 챕터 규격 기준 목표 자수와 씬 수 |
| 리텐션 장치 | 1~3화에 한해 핵심 소재 도달·주인공 매력 시연·첫 보상 배치 |

**출력:**
- `{slug}/P03_planning/04_chapter_plan.md` — 전체 챕터 플랜 요약
- `{slug}/P03_planning/s01/chapter_plan.md`
- `{slug}/P03_planning/s02/chapter_plan.md` (시즌 2 이상 존재 시)

**G3 게이트:** 시즌 아크 요약과 챕터당 1줄 요약표(챕터 번호·제목·핵심 사건·훅 유형)를 제시하고 정지한다. 수정 요청은 `chapter-plotter` 재호출로 반영하고, 승인 후 `gate_status.md`를 갱신한다.

---

## Phase 5: 집필 전 종합 검증

**실행 모드:** 순차 서브 에이전트 4단계

Phase 2~4의 모든 산출물(스토리 바이블·시즌 구조·챕터 플랜)을 집필 전에 종합 검증한다. 이 Phase를 통과해야만 Phase 6 집필을 시작할 수 있다.

**단계 1 — 스토리 바이블 최종 점검 (`story-bible-reviewer`, Mode A)**

오케스트레이터가 `story-bible-reviewer`를 호출한다. 목적: Phase 2 이후 수정 사항이 바이블 전체 정합성을 훼손하지 않았는지 최종 확인. 섹션 1의 8개 검토 축 전체를 적용한다. 결과를 반환한다.

**단계 2 — 시즌 구조 서사 품질 점검 (`narrative-review` 스킬, 섹션 4)**

오케스트레이터가 단계 1 결과를 읽은 뒤 `narrative-review` 스킬의 **섹션 4 — 시즌 구조 검토**를 실행한다. `{slug}/P03_planning/s01/season_bible.md`를 대상으로 7개 축을 점검하고 판정을 반환한다.

**단계 3 — 챕터 플랜-바이블 정합성 점검 (`story-bible-reviewer`, Mode B)**

오케스트레이터가 단계 2 결과를 읽은 뒤 `story-bible-reviewer`를 재호출한다. 목적: `{slug}/P03_planning/s01/chapter_plan.md`와 스토리 바이블 간의 갈등 정합성·Canon 상태 준수·시즌 씨앗 연결 집중 점검. 결과를 반환한다.

**단계 4 — 복선·연속성 사전 점검 (`continuity-keeper`)**

오케스트레이터가 단계 3 결과를 읽은 뒤 `continuity-keeper`를 호출한다. 목적: 챕터 플랜에 선언된 복선 심기/회수 계획이 물리적으로 실현 가능한지, 캐릭터 상태 초기값이 바이블과 일치하는지 사전 확인. Critical 경고 목록을 반환한다.

**통합 판정 및 출력:**

- 네 단계 결과를 `{slug}/P00_meta/logs/05_review_log.md`에 통합 기록한다
- **G4 게이트:** Critical 문제가 하나라도 있으면 판정과 Critical 목록만 보고하고 정지한 뒤 해당 Phase(2, 3, 또는 4)를 재실행한다
- Should 이하는 리뷰 로그에 기록하고 Phase 6으로 진행한다
- 모든 단계 Pass 또는 Conditional Pass이면 판정 다이제스트를 보고하고 `gate_status.md`를 갱신한 뒤 Phase 6으로 진행한다

**출력:** `{slug}/P00_meta/logs/05_review_log.md`

---

## Phase 6: 챕터 집필

**실행 모드:** 오케스트레이터 주도 순환 (초안 작성 → 스타일 검수·퇴고 → 사용자 승인 → 최종본 확정)

가장 긴 Phase다. 시즌 단위로 진행하며, 한 시즌이 완료된 후 다음 시즌으로 넘어간다.

**챕터 번호 정책:** 챕터 번호(`{CCC}`)는 **시즌별로 리셋**한다. `s01/chapters/001`, `s02/chapters/001` 형태로 관리한다. 파일 경로에 시즌 정보가 포함되어 있으므로 전체 고유성이 보장된다.

**요약 절차:**

1. `chapter-novelist`가 챕터 초안을 쓴다
2. `novel-style-guardian`과 `chapter-prose-reviser`가 문체 검수와 퇴고를 처리한다
3. 사용자가 원고를 승인하면 오케스트레이터가 마지막 퇴고본을 내용 변경 없이 `{CCC}_final.md`로 저장하고 `continuity-keeper`가 연속성을 갱신한다

**내부 실행 상세:**

**단계 A — 파일럿 (시즌 첫 챕터, 필수):**

1. 시즌 첫 챕터 `001`을 초안 → 1차 검수 → 퇴고 → 2차 검수까지 통과시킨다. **여기서 `{CCC}_final.md`를 만들지 않는다.** 2차 검수가 깨끗해도 최종본은 사용자 승인 후에만 생성한다. 병렬 배치를 시작하지 않는다.
2. **G5 게이트:** `001_revised.md` 경로, 자수, 씬 수, 훅 유형, 핵심 소재 도달 여부, 검수 요약 3줄을 보고하고 정지한다. 본문은 채팅에 출력하지 않는다.
3. 사용자 피드백이 오면 사용자 퇴고 루프 절차를 따르고 승인까지 반복한다.
4. **사용자가 승인하면** 마지막 퇴고본(`{CCC}_revised.md` 또는 `{CCC}_revised{N}.md`)을 내용 변경 없이 `{CCC}_final.md`로 저장한다. 이후 `continuity-keeper`가 연속성을 갱신한다.
5. `gate_status.md`를 갱신하고 단계 B로 진행한다. 이후 모든 챕터 프롬프트에는 갱신된 `voice_profile.md`를 포함한다.

**단계 B — 배치 집필 (승인된 문체 기준):**

1. 작업 계획에 `002`화부터 시즌의 나머지 챕터를 등록한다.
2. 오케스트레이터가 최대 3개의 챕터를 `chapter-novelist`에게 병렬 호출한다. 인접 챕터는 같은 저술가에게 묶어 전환부 맥락을 보존한다.
3. 모든 병렬 초안이 완성되면 각 `{CCC}_draft.md`를 **순차적으로** `novel-style-guardian`에게 전달한다. 1차 피드백은 `{CCC}_review.md`와 현재 시즌의 `P00_meta/logs/style_log_sNN.md`에 저장한다.
4. `{CCC}_draft.md`와 `{CCC}_review.md`를 `chapter-prose-reviser`에게 전달해 `{CCC}_revised.md`를 만든다.
5. `{CCC}_revised.md`를 `novel-style-guardian`에게 전달해 2차 검수하고 `{CCC}_review2.md`를 만든다.
6. `{CCC}_revised.md`와 `{CCC}_review2.md`를 `chapter-prose-reviser`에게 전달한다. 2차 검수에 Critical/Should가 남아 있으면 해당 지적만 최소 수정해 `{CCC}_revised2.md`를 만든다. 잔존 지적이 없으면 `{CCC}_revised.md`를 그대로 둔다. **이 단계에서 `{CCC}_final.md`를 만들지 않는다.**
7. 배치의 모든 챕터가 위 상태에 도달하면 단계 C로 진행한다. 연속성 갱신은 G6 승인 이후에 수행한다.
8. Critical 경고는 문체 문제면 `chapter-prose-reviser`, 사건·연속성 문제면 `chapter-novelist`로 라우팅한다. 내부 자동 루프는 최대 2회이며 사용자 퇴고 라운드는 이 상한에 포함하지 않는다.

**단계 C — 배치 게이트:**

1. 3화 배치마다 **G6 게이트**에서 챕터·제목·자수·씬 수·1차 리뷰 Critical/Should 건수·최종 검수 상태·미해결 이슈를 표로 보고하고 정지한다. 시즌 끝의 남은 배치가 1~2화여도 완료 직후 같은 G6를 실행한다.
2. 직전 배치보다 1차 리뷰 지적 건수가 2배 이상 증가하거나 3개 배치 연속 상승하면 `품질 하락 추세 — 원인(피로 패턴/플랜 밀도 저하) 점검 권고`를 1줄 추가한다.
3. 사용자의 `계속`을 배치 승인으로 간주한다. 승인되면 각 챕터의 마지막 퇴고본(`{CCC}_revised.md` 또는 `{CCC}_revised{N}.md`)을 내용 변경 없이 `{CCC}_final.md`로 저장하고, `continuity-keeper`가 챕터 번호 순으로 연속성과 `glossary.md`를 갱신한다. 그 뒤 `gate_status.md`를 갱신하고 다음 배치로 진행한다. 수정 요청은 사용자 퇴고 루프를 따르며, 승인 전에는 어떤 챕터의 `final.md`도 만들지 않는다.
4. 전역 문체 피드백은 `voice_profile.md`에 추가해 이후 배치에 적용하며, 기존 확정 챕터 소급 여부는 사용자에게 확인한다.

**병렬 → 순차 혼합 이유:** 초안은 병렬로 빠르게 생성하고, 검수·퇴고·연속성 갱신은 순차로 처리해 충돌을 방지한다.

**문체 품질 전달 규칙:** Phase 6의 모든 `chapter-novelist` 프롬프트에는 `style-guides/lightnovel-style-guide.md`와 함께 아래 초점을 명시한다.

- 단문은 타이밍으로 살리고, 새 장소·인물·사물 묘사는 POV 감각 흐름으로 연결한다.
- `{slug}/P02_bible/voice_profile.md`가 있으면 작품 고유 화자의 사고방식·비유·문단 닫는 반응을 반영한다.
- `voice_profile.md`의 `## 사용자 피드백 보정`은 일반 스타일 가이드보다 우선한다. 충돌하면 사용자 보정을 따른다.
- 챕터 플랜의 주요 사건을 2~4개 씬 카드에 배정하고 실시간 장면으로 극화한다. 요약·몽타주는 시간 경과 처리에만 챕터당 1회 이내로 쓴다.
- `~고`, `~며`, `~자`로 이어 붙였어도 절의 중심이 계속 사물/공간이면 체크리스트 묘사로 본다. 위치/사물 주어가 3회 이상 이어지면 POV 동작을 연결축으로 삼는다.
- 장면 밀도 패스 후에는 묘사 연결 패스를 수행해, 감각을 더 넣는 데서 멈추지 않고 POV 인물의 몸·시선·판단으로 문단이 이어지는지 확인한다.

`novel-style-guardian` 호출 시에도 같은 초점을 전달해, 설명 나열용 단문, `있었다/였다/났다` 반복, 연결어로 붙인 감각 체크리스트, 위치 주어 반복, 작품 고유 화자 이탈(`[POV Voice]`)을 우선 검수하게 한다. 이때 감각 추가량보다 연결축 유무와 voice profile 반영 여부를 먼저 보게 한다.

`chapter-prose-reviser` 호출 시에는 `{CCC}_draft.md`의 저자 노트, `{CCC}_review.md` 또는 `{CCC}_review2.md`, `voice_profile.md`를 함께 전달한다. 퇴고자는 `퇴고 주의 지점`에 적힌 단문·복선·훅을 보존하고, 문장 리듬과 묘사 연결만 조정한다.

**주요 산출물:**
- `{slug}/P04_continuity/sNN/chapters/{CCC}_final.md`

**내부 산출물:**
- `{slug}/P04_continuity/sNN/chapters/{CCC}_draft.md` — 초안
- `{slug}/P04_continuity/sNN/chapters/{CCC}_review.md` — 1차 스타일 리뷰
- `{slug}/P04_continuity/sNN/chapters/{CCC}_revised.md` — 문장 퇴고본
- `{slug}/P04_continuity/sNN/chapters/{CCC}_review2.md` — 2차 스타일 리뷰

---

## Phase 7: 문체/대사/시점/연속성 검수

**실행 모드:** 순차 서브 에이전트 (시즌 전체 관점)

Phase 6에서 검수가 이미 챕터별로 이루어졌으나, 이 Phase에서는 **시즌 전체를 통으로 보는** 검수를 수행한다.

**절차:**
1. 오케스트레이터가 `novel-style-guardian`을 호출하고 `narrative-review` 스킬 **섹션 5 — 시즌 통독 검수**를 기준으로 시즌 원고 전체를 점검하도록 명시한다. 가디언은 축별 판정과 수정 필요 챕터 목록을 반환한다
2. 오케스트레이터가 `continuity-keeper`를 호출한다. 시즌 전체의 복선 회수 여부, 캐릭터 아크 완결성, 타임라인 충돌 최종 점검을 목적으로 명시한다. Critical 경고 목록을 반환한다
3. 오케스트레이터가 두 결과를 취합해 수정이 필요한 챕터를 식별한다. 문체·문장 리듬 문제는 `chapter-prose-reviser`, 사건·연속성·챕터 구조 문제는 `chapter-novelist`로 라우팅한다
4. 모든 Critical을 `{slug}/P00_meta/logs/critical_status.md`에 수렴한다. 원본 로그가 아카이브되어도 이 활성 파일은 유지하며 상태는 `open / resolved / user_accepted` 중 하나로 관리한다
5. `open` Critical이 있으면 **Phase 8(통합 편집)까지만 진행**하고, 오케스트레이터가 사용자에게 수동 확인을 요청할 때까지 **Phase 8.5 이후와 Phase 9(최종 EPUB 빌드)는 중단**한다
6. 수정 근거가 확인되면 `resolved`, 사용자가 문제를 이해한 상태에서 명시적으로 진행을 승인하면 승인 일시·게이트를 기록하고 `user_accepted`로 변경한다. 둘 중 하나가 되기 전에는 `open`을 제거하지 않는다
7. Critical 이슈가 해소되거나 사용자 수동 확인이 완료되면 건너뛰지 않고 정상 순서로 재개한다. Phase 8 미완료면 Phase 8부터, 완료 상태면 Phase 8.5부터 진행하며 시즌제 작품은 반드시 Phase 8.7과 G7.7을 거친 뒤에만 Phase 9 또는 다음 시즌으로 이동한다

**출력:**
- `{slug}/P00_meta/logs/style_log_sNN.md` (현재 시즌 리뷰만 append)
- `{slug}/P04_continuity/continuity_log.md`
- `{slug}/P04_continuity/timeline.md`
- `{slug}/P04_continuity/foreshadowing_tracker.md`
- `{slug}/P04_continuity/character_state_table.md`
- `{slug}/P00_meta/logs/critical_status.md` (아카이브되지 않는 활성 Critical 상태 SSOT)

`critical_status.md` 형식:

```markdown
| ID | 시즌 | 출처 | 요약 | 상태 | 해결·승인 근거 | 최종 갱신 |
|----|------|------|------|------|---------------|----------|
| CRIT-sNN-001 | sNN | continuity/style | | open / resolved / user_accepted | 파일·게이트·사용자 승인 일시 | |

## 시즌별 집계
| 시즌 | open | resolved | user_accepted | 상세 스냅샷 | 최종 재계산 |
|------|------|----------|---------------|---------------|---------------|
| sNN | 0 | 0 | 0 | P04_continuity/sNN/_archive/critical_status_sNN.md | |
```

항목은 근거 없이 삭제하지 않는다. 롤업 시 `resolved` 상세는 시즌 아카이브로 옮길 수 있지만 `open`과 `user_accepted` 항목 및 시즌별 건수·스냅샷 경로는 활성 파일에 남긴다. 집계는 원본 로그와 대조해 매번 재계산하며 기존 값을 누적 덧셈하지 않는다.

---

## Phase 8: 통합 편집

**실행 모드:** 단일 서브 에이전트

`novel-editor`를 호출한다. 모든 챕터 최종본을 시즌 원고와 전체 원고(`P05_manuscript/04_manuscript.md`)로 통합한다. 저자 노트 제거, 전환부 정리, `P02_bible/glossary.md` 기준 용어 통일, 서문·작가 후기 작성, `P05_manuscript/book_manifest.json` 생성을 수행한다.

통합 후 교열 전용 패스를 1회 수행한다. 맞춤법·띄어쓰기·비문·문장부호·숫자/단위 표기·용어집 대조만 수정하고 플롯·문체·인물 의도는 바꾸지 않는다. 수정 건수와 유형을 `P00_meta/logs/proofread_log.md`에 기록한다.

**출력:**
- `{slug}/P05_manuscript/sNN/season_manuscript.md`
- `{slug}/P05_manuscript/04_manuscript.md`
- `{slug}/P05_manuscript/book_manifest.json`
- `{slug}/P00_meta/logs/proofread_log.md`

**G7 게이트:** 시즌 통독 검수 요약, 교열 결과 1줄, 통합 원고 경로를 보고하고 정지한다. 수정 요청은 사용자 퇴고 루프를 적용하며, 승인 후 `gate_status.md`를 갱신한다.

---

## Phase 8.5: 본문 삽화 프롬프트/파일 계약

**실행 모드:** 서브 에이전트

`interior-illustrator`를 호출한다. 라노벨 본문 삽화의 장면 선정, 이미지 생성 프롬프트, 저장 파일 경로 계약을 담당한다. 세션에 이미지 생성 수단이 있으면 프롬프트 작성 후 직접 생성을 시도하고, 없거나 실패하면 외부 생성 계약으로 폴백한다.

챕터 플랜 기준의 예비 슬롯이 있더라도, Phase 6의 최종 원고와 Phase 8의 통합 원고를 우선해 장면 위치와 스포일러 강도를 보정한다.

**절차:**
1. `interior-illustrator`가 `novel-illustration` 스킬을 사용해 `{slug}/P06_publication/illustrations/illustration_plan.md`를 작성 또는 갱신한다
2. 단권 20챕터 기준 기본값은 컬러 프론트피스 1장 + 본문 삽화 6~10장이다. 사용자 지정이 있으면 그 수량을 따른다
3. 캐릭터 카드의 외형 키워드와 캐릭터 외형·의상·소품 일관성을 `{slug}/P06_publication/illustrations/style_sheet.md`에 기록하고 모든 슬롯 프롬프트에 반영한다
4. 각 이미지의 외부 생성 프롬프트를 `{slug}/P06_publication/illustrations/sNN/*_prompt.md`에 저장하고, 저장해야 할 PNG 경로를 명시한다
5. 이미지 생성 수단이 있으면 계약 경로에 PNG를 생성하고 상태를 `generated`로 갱신한다. 생성 수단이 없거나 실패하면 `prompt_ready` 또는 `image_missing`으로 둔다. 사용자가 배치한 이미지는 `user_provided`, 제외한 슬롯은 `excluded`로 기록한다
6. `novel-editor` 또는 오케스트레이터가 `P05_manuscript/04_manuscript.md`에 Markdown 이미지 마커를 삽입한다

**출력:**
- `{slug}/P06_publication/illustrations/illustration_plan.md`
- `{slug}/P06_publication/illustrations/style_sheet.md`
- `{slug}/P06_publication/illustrations/sNN/{CCC}_{scene_slug}_prompt.md`
- `{slug}/P06_publication/illustrations/sNN/{CCC}_{scene_slug}.png` (외부 도구가 저장해야 하는 대상 파일)
- 삽화가 포함되도록 갱신된 `{slug}/P05_manuscript/04_manuscript.md`

**G7.5 게이트 — 삽화 확인:**

아래 형식으로 보고하고 정지한다. 생성된 이미지에는 외형 일관성 육안 확인 필요 여부를 표시한다.

| 슬롯 | 챕터·장면 | 설명 요약 | 프롬프트 경로 | 이미지 상태 |
|------|-----------|-----------|-----------------|--------------|
| frontpiece | - | | `000_frontpiece_prompt.md` | generated / image_missing |
| 01 | 003화 첫 대면 | | `{CCC}_{scene_slug}_prompt.md` | prompt_ready / user_provided / excluded |

- 슬롯별 승인·수정·제외를 받는다. 장면 교체나 프롬프트 수정은 `interior-illustrator`를 재호출하고 사용자 퇴고 루프에 따라 반복한다.
- 자동 생성, 외부 생성 후 배치 대기, 삽화 생략 중 하나를 선택할 수 있게 한다.
- 일부 이미지만 있으면 누락 슬롯 제외 후 빌드할지 배치까지 기다릴지 확인한다.
- 모든 슬롯이 승인되고 이미지가 확보되거나 제외가 확정된 뒤 `gate_status.md`를 갱신한다. **시즌제 작품은 Phase 8.7로 진행하고, 단권(`s01` 단독) 작품만 G8로 진행한다.**

---

## Phase 8.7: 시즌 롤업

**실행 모드:** 순차 서브 에이전트 2단계

**실행 조건:** 시즌제 작품에서 시즌 N의 Phase 8과 Phase 8.5가 완료된 뒤 실행한다. 단권(`s01` 단독) 작품은 건너뛴다.

시즌을 닫고 다음 시즌 작업 공간을 준비한다. 누적된 추적 자료를 인물 카드와 시즌 요약으로 수렴시키고, 중간 산출물을 무손실 아카이브해 활성 파일 수와 에이전트 입력량을 되돌린다.

롤업 시작 전에 `P03_planning/03_season_plan.md`와 Phase 0의 계획 시즌 수를 대조해 **다음 계획 시즌 존재 여부**를 확정한다. 이 판정은 성장 방향 작성과 G7.7 이후 라우팅에 동일하게 사용한다.

**롤업 전체를 하나의 트랜잭션으로 처리한다.** 어떤 에이전트도 활성 파일을 바로 수정하지 않는다. 시작 시 `rollup_log.md`의 미완료 `pending` 저널을 먼저 검사하고, 있으면 새 롤업을 시작하지 말고 이전 스냅샷을 복원해 롤백부터 완료한다. 다음으로 `critical_status.md`를 원본 로그와 대조한다. 파일이 누락·오래되었거나 `open`이 있으면 **인물 카드 갱신을 포함한 어떤 쓰기도 시작하지 않는다.**

### 단계 1 — 카드 갱신 (`story-bible-planner`)

**입력:** `P03_planning/03_season_plan.md`, `character_state_table.md`, `continuity_log.md`의 시즌 N 구간, 시즌 N `season_manuscript.md`, `characters/README.md` 색인과 시즌 N에 등장한 인물 카드. 색인이 없으면 기존 `characters/*.md` 구조에서 등장 인물 카드를 찾는다

1. `continuity_log.md`의 `### 카드 미등재 인물` 후보를 확인하고 WP16 판정 기준에 맞는 인물 카드를 신설한다
2. 각 인물 카드의 `## 시즌별 상태 변화`에 `### sNN 종료 시점` 항목을 append한다. 기존 시즌 기록은 덮어쓰지 않는다
3. 다음 계획 시즌이 있을 때만 주요 인물 카드의 `## 성장 방향`에 `### s{N+1} 성장 방향` 초안을 append한다. 시즌 아크에 참여하는 조연도 포함한다. **마지막 계획 시즌이면 `s{N+1}` 성장 방향을 생성하지 않고**, `## 시즌별 상태 변화`의 종료 상태를 시리즈 완결 상태로 기록한다
4. `supporting.md`의 인물 항목이 12개를 초과하면 첫 등장 시즌 기준 `supporting_sNN.md`로 분리하고 `characters/README.md` 색인을 만든다
5. `relationships.md`를 시즌 N 종료 시점 기준으로 갱신한다
6. 신설·갱신·분리할 카드, `characters/README.md`, `relationships.md`를 원본 경로에 쓰지 말고 `P04_continuity/sNN/_archive/.staging/new-active/`에 **프로젝트 상대 경로를 보존**해 작성한다. 어떤 출력을 신설하고 어떤 파일을 교체할지 목록도 함께 반환한다

### 단계 2 — 추적 파일 압축 (`continuity-keeper`)

1. `{slug}/P03_planning/sNN/season_summary.md`를 아래 형식으로 생성한다. 목표 크기는 시즌 1 기준 **5KB 이내**다. 최종 경로에 바로 쓰지 말고 단계 1과 같은 스테이징 트리에 작성한다
2. `continuity_log.md`와 `style_log_sNN.md`의 Critical을 `P00_meta/logs/critical_status.md`와 다시 대조해 사전 판정이 아직 유효한지 확인한다. `open`이 1건이라도 있거나 원본 로그보다 상태 파일이 오래되었으면 스테이징을 폐기하고 아카이브를 시작하지 않는다
3. `continuity_log.md`, `timeline.md`, `foreshadowing_tracker.md`의 시즌 N 구간을 `{slug}/P04_continuity/sNN/_archive/`의 시즌별 원본 파일로 추출한다. 새 활성 `continuity_log.md`와 `timeline.md`에는 `season_summary.md` 링크를 남기고, `foreshadowing_tracker.md`에는 요약 링크와 **미회수·이월 복선 행 전체**를 다음 시즌 활성 상태로 보존한다
4. `character_state_table.md`를 `_archive/character_state_table_sNN_end.md`로 동결 복사한다. 다음 계획 시즌이 있으면 활성 본체의 행과 종료 상태는 유지하고 `최종 업데이트 챕터`만 다음 시즌 시작 상태로 리셋한다. **마지막 계획 시즌이면 최종 챕터 값을 유지하고 리셋하지 않는다**
5. `glossary.md`에서 본문·계획 어디에도 실제 사용되지 않은 항목과 중복 표기를 정리한 새 파일을 스테이징한다. 향후 시즌 계획에 있는 표기는 미사용으로 보지 않는다. 표준 표기 변경은 자동 적용하지 않고 파급 범위를 보고한다
6. 시즌 N의 챕터 배관·백업 파일을 아카이브한다. `chapters/{CCC}_draft*.md`, `{CCC}_review*.md`, `{CCC}_user_review*.md`, `{CCC}_revised*.md`, `{CCC}_final_v*.md`를 `chapters/_archive/`로 이동하고 현재 `{CCC}_final.md`만 `chapters/` 직하에 유지한다
7. `P00_meta/logs/style_log_sNN.md`와 해당 시즌의 `resolved` Critical 상세를 `P04_continuity/sNN/_archive/`로 이동한다. `critical_status.md`의 `open`·`user_accepted`와 시즌별 건수는 활성 상태로 유지한다

### 아카이브 트랜잭션 규칙

파일은 **삭제하거나 덮어쓰지 않는다.** 여러 파일을 바로 이동한 뒤 검증하지 말고 아래 순서로 처리한다.

1. **사전 검사:** 정확한 이동·신설·교체 대상과 목적지 목록을 만든다. 각 기존 대상이 일반 파일인지 확인하고, 심볼릭 링크·목적지 중복·기존 파일 충돌·예상 밖 경로가 하나라도 있으면 쓰기 전에 중단한다
2. **스테이징:** 추적 아카이브본, `season_summary.md`, `critical_status_sNN.md`, **새 활성 추적 파일 전체**와 `critical_status.md`, 갱신·신설할 인물 카드·색인·관계·용어집 파일을 모두 `sNN/_archive/.staging/new-active/`에 **프로젝트 상대 경로를 보존**해 작성한다. 원본 바이트·항목 수·이월 복선 수·Critical 상태별 수와 스테이징 결과를 대조한다
3. **이동 저널:** 각 조작 **전에** `rollup_log.md`의 `pending` 항목에 `원본 → 목적지`와 예상 바이트를 기록하고 저장을 확인한 뒤 한 파일씩 조작한다. 조작 후는 해당 항목만 `done`으로 바꾸며 기존 목적지 파일은 절대 교체하지 않는다
4. **커밋 준비:** 교체할 인물 카드·색인·관계·용어집 파일, 활성 추적 파일, `critical_status.md`를 모두 `sNN/_archive/pre_rollup_snapshot/`의 같은 프로젝트 상대 경로로 이동한다. 이어서 `new-active/`의 신규·갱신 파일을 최종 경로로, 챕터 배관·백업과 `style_log_sNN.md`를 아카이브 경로로 하나씩 승격한다. 신규 파일은 기존 스냅샷이 없음을 저널에 표시한다
5. **커밋 롤백:** 어느 조작에서든 실패하면 저널을 역순으로 실행한다. 승격한 새 파일은 프로젝트 경로에서 `new-active/`로 되돌리고, `pre_rollup_snapshot/`의 카드·색인·관계·용어집·추적·Critical 상태 파일을 원래 경로로 복원하며, 챕터 배관·백업과 스타일 로그도 활성 위치로 되돌린다. 완전 롤백 후에만 재시도할 수 있다
6. **커밋 완료:** 전 이동, 신규·교체 파일, 활성 미회수 복선, Critical 집계 검증이 끝난 뒤에만 `rollup_log.md` 상태를 `committed`로 바꾼다. `pre_rollup_snapshot/`은 삭제하지 않고 복구 감사 자료로 보존한다

### `season_summary.md` 형식

```markdown
# 시즌 N 요약

> 이 파일은 시즌 N 종료 후 다음 시즌 작업의 유일한 과거 참조원이다.
> 원본은 `P04_continuity/sNN/_archive/`에 보존된다.

## 사건 라인
{챕터 묶음 단위로 10줄 이내}

## 인물 변화
{인물당 1줄 — 시작 상태 → 종료 상태. 상세는 characters/ 카드 참조}

## 복선 상태
| 복선 | 심은 챕터 | 상태 | 회수 예정 |
|------|----------|------|----------|
{회수 완료는 1줄 요약, 이월 복선은 전부 나열}

## 타임라인
{서사 내 주요 시점만. 챕터 단위 상세는 아카이브 참조}

## 다음 시즌 이월 사항
{미해결 갈등, 인물이 모르는 사실, 열린 질문}

## 품질 게이트 상태
{Critical open 0건 / resolved N건 / user_accepted N건. 상세 SSOT는 P00_meta/logs/critical_status.md}
```

**출력:**
- 갱신된 `{slug}/P02_bible/characters/*.md`와 `{slug}/P02_bible/relationships.md`
- `{slug}/P03_planning/sNN/season_summary.md`
- `{slug}/P04_continuity/sNN/_archive/`와 `{slug}/P04_continuity/sNN/chapters/_archive/`
- `{slug}/P00_meta/logs/rollup_log.md` — 시즌, 아카이브 건수, 변경 전후 활성 파일 수, 원본/요약 바이트, 압축률, 카드 변경 건수 기록

**G7.7 게이트 — 시즌 롤업 확인:**

아래 항목을 포함한 **15줄 이내 다이제스트**를 보고하고 정지한다.

| 항목 | 값 |
|------|-----|
| 신규 등재 인물 | N명 (이름 나열) |
| 카드 갱신 | N건 |
| 활성 파일 수 | 변경 전 X개 → 변경 후 Y개 |
| 추적 파일 압축 | 원본 XKB → `season_summary.md` YKB |
| 다음 시즌 성장 방향 | 다음 시즌 있음: 주요 인물 N명 작성 완료 / 마지막 계획 시즌: 해당 없음 (`s{N+1}` 미생성) |
| Critical 상태 | open 0건 / resolved N건 / user_accepted N건 |

사용자는 신규 인물 카드와 성장 방향을 승인하거나 수정 요청한다. 수정 요청에는 사용자 퇴고 루프를 적용한다. 승인 전 다음 시즌 Phase 3·4를 시작하지 않으며, 승인 후 `gate_status.md`를 갱신한다. 남은 계획 시즌이 있으면 다음 시즌의 Phase 3 상세화 또는 Phase 4로 이동하고, 마지막 계획 시즌까지 완료했을 때만 G8로 진행한다.

---

## Phase 9: 표지 + EPUB 빌드

**실행 모드:** 서브 에이전트 (표지 먼저, 완료 후 EPUB 빌드)

기존 하네스의 `cover-designer`와 `epub-builder`를 그대로 재사용한다. 입력 포맷이 동일하므로 호환성 문제가 없다.

> **G8 게이트(강제):** 먼저 `P00_meta/logs/critical_status.md`를 읽는다. 파일이 없거나 최근 시즌 로그보다 오래되었거나 `open` 항목이 하나라도 있으면 Phase 9 실행을 금지한다. `user_accepted`는 승인 일시·게이트 근거가 있을 때만 통과로 인정한다. 롤업 전 단권은 활성 `continuity_log.md`와 `style_log_s01.md`도 함께 대조한다. 판정 다이제스트와 수동 확인 요청을 제시하고 승인·수정 완료 전까지 EPUB 빌드를 호출하지 않는다. 통과 시 `gate_status.md`를 갱신한다.

1. `cover-designer` → `{slug}/P06_publication/assets/cover.png` 생성 (이미지 생성 도구/스킬 > API > ImageMagick 폴백)
2. 본문 삽화 마커가 있으면 `P05_manuscript/04_manuscript.md`의 상대 이미지 경로와 실제 PNG 파일 존재 여부를 확인한다. PNG가 없으면 해당 마커를 빌드에서 제외하거나 사용자 확인 후 진행한다
3. 표지 생성 완료 후 `epub-builder` 호출 → `epub-build/scripts/build_epub.sh` 실행
4. `epub-builder`가 EPUB 빌드 직후 **책 소개 markdown**을 함께 산출

**EPUB 메타데이터:**
- 저자: Phase 0에서 추출한 값, 없으면 기본값 `AI-Author`
- 제목: Phase 2에서 확정된 작품 제목
- 버전: 초기 실행 `1.0.0`, 재실행 시 증가
- 언어: `ko`

**출력:**
- `{작품-제목}-v{version}.epub` (프로젝트 루트)
- `{작품-제목}-v{version}.md` (프로젝트 루트 — 책 소개 markdown)
- `{slug}/P06_publication/assets/cover.png`
- `{slug}/P00_meta/logs/build_log.md`

---

## 에러 핸들링

| 시나리오 | 대응 |
|---------|------|
| 리서치 에이전트 타임아웃 | 가용 결과만으로 `P01_research/01_reference.md` 작성, 누락 섹션 명시 후 진행 |
| `story-bible-reviewer` Fail 판정 | 사용자에게 보고, `story-bible-planner` 재작업 요청 |
| `continuity-keeper` Critical 경고 | 해당 챕터 finalizing 중단, 저술가에게 수정 지시 |
| 퇴고 루프 2회 후에도 스타일 이견이 남음 | 남은 문제를 현재 시즌의 `P00_meta/logs/style_log_sNN.md`에 미해결로 기록하고 현재 final 후보를 사용자 확인 대상으로 보고 |
| `[LOCKED]` Canon 위반 감지 | `continuity-keeper`가 차단, `story-bible-planner`에게 공식 개정 절차 요청 |
| 표지 생성 실패 | ImageMagick 폴백 → 단순 타이포그래피 표지. 폴백도 실패 시 사용자 알림 후 표지 없이 빌드 |
| EPUB 빌드 실패 | pandoc 에러 메시지 그대로 보고, `P05_manuscript/04_manuscript.md`는 보존 |
| 시즌 롤업 중 아카이브 누락·이름 충돌 | 이동을 중단하고 원본을 활성 위치에 보존한 뒤 누락·충돌 목록을 보고 |
| `season_summary.md`가 5KB를 초과하거나 이월 복선이 누락됨 | G7.7 통과 금지. 요약을 재작성하되 이월 복선은 축약·삭제하지 않음 |
| `critical_status.md` 누락·오래됨·open 존재 | Phase 8.7 아카이브와 G8 빌드를 중단하고 원본 로그와 대조해 상태 파일부터 복구 |

---

## 데이터 전달 규칙

| 방식 | 용도 |
|------|------|
| 파일 기반 (`{slug}/`) | 모든 Phase 간 산출물 전달, 감사 추적 |
| 반환값 + 오케스트레이터 중계 | 에이전트 간 피드백 전달 (Phase 2·5·6·7). 에이전트는 결과를 파일에 저장하고 반환하며, 오케스트레이터가 읽어 다음 에이전트 프롬프트에 포함한다 |
| 작업 계획 | Phase 6의 챕터 작업 분배·진행 추적 |
| 반환값 기반 | 서브 에이전트 모드(Phase 1·3·4·8·9)의 결과 수집 |
| `gate_status` (`P00_meta/gate_status.md`) | 게이트 통과 기록과 세션 간 재개 지점 |
| `critical_status` (`P00_meta/logs/critical_status.md`) | 아카이브와 무관하게 유지되는 Critical 상태·승인 근거 SSOT |

파일명 컨벤션:
- Phase 산출물: `{NN}_{artifact}.md` (NN = Phase 번호 2자리)
- 챕터: `{CCC}_draft.md` / `{CCC}_review.md` / `{CCC}_revised.md` / `{CCC}_review2.md` / `{CCC}_user_review{N}.md` / `{CCC}_revised{N}.md` / `{CCC}_final.md` (CCC = 시즌 내 3자리 제로 패딩, 시즌별 리셋. 사용자 피드백 N은 1부터, 대응 퇴고본 번호는 2부터 시작)
- 시즌 설계 경로: `P03_planning/s{NN}/`, 챕터 원고·연속성 경로: `P04_continuity/s{NN}/`, 시즌 통합 원고 경로: `P05_manuscript/s{NN}/` (NN = 2자리 제로 패딩)

---

## 부분 재실행 규칙

완성된 작품에 수정 요청이 생기면 해당 Phase만 재실행한다. 재실행 시 버전은 **마이너 증가** (`v1.0.0` → `v1.1.0`), 사용자가 명시하면 그 값을 사용한다.

| 요청 유형 | 재실행 Phase | 백업 규칙 |
|----------|------------|---------|
| 스토리 바이블 수정 | Phase 2 → 3 → 4 → 5 재실행 | `P02_bible/02_story_bible.md` → `02_story_bible_v{N}.md` |
| 시즌 구조 수정 | Phase 3 → 4 → 5 재실행 | `P03_planning/03_season_plan.md` → `03_season_plan_v{N}.md` |
| 인물 추가·카드 수정 | Phase 2 인물 카드만 갱신 (Phase 3~5 재실행 불필요). 단, 시즌 아크나 챕터 플랜에 영향이 있으면 해당 Phase도 재실행 | `supporting.md` 또는 `supporting_sNN.md` → 해당 파일 `_v{N}.md` |
| 단일 챕터 재작성 | Phase 6 (해당 챕터만) → Phase 7. 아카이브된 시즌이면 `_archive/`에서 해당 챕터 배관 파일을 먼저 복원 | `{CCC}_draft.md` → `{CCC}_draft_v{N}.md` |
| 문체 전역 보정 | `voice_profile.md` 갱신 → 이후 챕터 적용. 기존 챕터 소급은 사용자 선택 | `voice_profile.md` → `voice_profile_v{N}.md` |
| 본문 삽화 추가/교체 | Phase 8.5 재실행 → G7.5 재통과 | 기존 PNG → `{name}_v{N}.png` |
| 표지 교체 | Phase 9 (`cover-designer`만) | `P06_publication/assets/cover.png` → `cover_v{N}.png` |
| EPUB 재빌드 | Phase 9 (`epub-builder`만) | 기존 EPUB → `_prev/` 이동 |

---

## 실행 후 피드백

모든 Phase 완료 및 EPUB 산출 후:
1. 사용자에게 EPUB 경로 + 책 소개 markdown 경로 + 요약 보고
2. "개선할 부분이 있나요?"를 짧게 질문한다 (강요하지 않음)
3. 피드백이 오면 위 부분 재실행 규칙에 따라 해당 Phase만 재실행
