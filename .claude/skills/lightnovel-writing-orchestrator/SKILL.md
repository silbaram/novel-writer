---
name: lightnovel-writing-orchestrator
description: |
  Orchestrates a Korean light novel or fiction writing workflow from premise to finished EPUB. Use when the user asks to write a 라노벨, 소설, 웹소설, 판타지, 로맨스 판타지, 이세계물, 회귀물, 학원물, 시즌제 소설, serialized fiction, or EPUB fiction project. Supports single-volume and multi-season structures.
---

# Lightnovel Writing Orchestrator

장르·분위기·주인공 아이디어를 받아 스토리 바이블 → 시즌 구조 → 챕터 집필 → EPUB 빌드까지 전 과정을 조율한다. 각 Phase에서 전문 에이전트를 호출하고, 중간 산출물을 `{slug}/` 하위에 축적한 뒤 최종 EPUB을 프로젝트 루트에 만든다.

> **저작권 원칙:** 기존 저작물(소설·웹툰·게임·애니메이션 등)의 캐릭터·세계관·고유 설정·문장을 허가 없이 복사하거나 직접 전용하지 않는다. 오마주·패러디를 의도하더라도 독립적 설정으로 치환한다. 이 원칙은 모든 Phase의 에이전트에 공통 적용된다.

---

## 실행 모드 요약

| Phase | 이름 | 실행 모드 |
|-------|------|----------|
| 0 | 소설 요청 분석 | 인라인 |
| 1 | 소재/세계관 리서치 | 서브 에이전트 (병렬 가능) |
| 2 | 스토리 바이블 작성 | 단일 서브 → 팀 (생성-검증) |
| 3 | 시즌 구조 설계 | 단일 서브 |
| 4 | 챕터 플롯 작성 | 단일 서브 (시즌별 순차) |
| 5 | 플롯/시즌 리뷰 | 에이전트 팀 (검증) |
| 6 | 챕터 집필 | 에이전트 팀 (최대 3개 동시 챕터) |
| 7 | 문체/연속성 검수 | 에이전트 팀 (챕터별 병렬 처리 가능) |
| 8 | 통합 편집 | 단일 서브 |
| 9 | 표지 + EPUB 빌드 | 서브 에이전트 (병렬 후 순차) |

---

## Phase 0: 소설 요청 분석

**실행 모드:** 인라인

사용자 입력에서 다음 항목을 추출한다. 항목이 불명확하거나 누락된 경우 `AskUserQuestion`으로 짧게 확인한다. 핵심 항목(장르·핵심 아이디어·주인공)이 없으면 Phase 1로 진행하지 않는다.

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
| 저자명 | 미지정 시 기본값 `Toby-AI` |

**슬러그 생성:** 작품 핵심 키워드로 영문 슬러그를 만든다. 예: `회귀한 마검사` → `regression-swordmaster`.

**기존 산출물 확인:**
- `{slug}/` 미존재 → 초기 실행, Phase 1부터 순차 실행
- `{slug}/` 존재 + 부분 수정 요청 → 해당 Phase만 재실행 (아래 "부분 재실행 규칙" 참조)
- `{slug}/` 존재 + 새 입력 → `{slug}_prev-{timestamp}/`로 이동 후 새 실행

---

## Phase 1: 소재/세계관 리서치

**실행 모드:** 서브 에이전트 (병렬 가능)

**목적:** 작품의 소재·배경과 관련된 실세계 자료(역사·신화·사회·과학·장르 관행 등)를 수집한다. 완전 창작 세계관이라면 같은 장르 독자 반응·선행 작품 트렌드 리서치로 대체한다.

- `web-researcher`와 `community-researcher`를 `run_in_background: true`로 병렬 호출한다
- 논픽션 소재가 포함된 경우(역사물·SF·무협 등) `paper-researcher`를 추가 호출한다
- 순수 창작 세계관이고 사용자가 "리서치 없이 바로 진행"을 요청한 경우 이 Phase를 건너뛰고 빈 `01_reference.md`를 생성한 뒤 Phase 2로 이동한다

**입력:** 장르, 핵심 아이디어, 배경 설정 키워드
**출력:** `{slug}/01_reference.md` — 세계관·소재 레퍼런스 (섹션: 장르 관행, 배경 자료, 독자 기대, 유사 작품 분석, 참고문헌)

Agent 도구 호출 시 반드시 `model: "opus"`를 명시한다.

---

## Phase 2: 스토리 바이블 작성

**실행 모드:** 단일 서브 에이전트 → 에이전트 팀 (생성-검증)

픽션의 기반 설정 전체를 이 Phase에서 확정한다.

> **범위 제한:** Phase 2는 챕터별 상세 플롯을 작성하지 않는다 (Phase 4). 시즌별 상세 아크도 작성하지 않는다 (Phase 3). "어떤 세계에서, 어떤 인물이, 어떤 갈등을 가지는가"만 다룬다.

**절차:**

1. `story-bible-planner`를 호출한다. 10단계 내부 절차를 통해 스토리 바이블을 작성한다
2. `story-bible-reviewer`를 호출한다. 8개 검토 축으로 바이블을 평가하고 `SendMessage`로 피드백을 전달한다
3. `story-bible-planner`가 피드백을 반영해 바이블을 갱신한다. 최대 2회 왕복
4. `story-bible-reviewer`의 최종 판정이 **Fail**이면 사용자에게 보고하고 재작업을 요청한다. **Pass** 또는 **Conditional Pass**면 Phase 3으로 진행한다
5. 사용자에게 스토리 바이블을 제시하고 승인을 받는다. 피드백이 있으면 `story-bible-planner`를 한 번 더 호출해 반영한다

**출력:**
- `{slug}/02_story_bible.md` + `{slug}/02_story_bible.json`
- `{slug}/characters/*.md`
- `{slug}/worldbuilding/*.md`
- `{slug}/relationships.md`
- `{slug}/open_questions.md`
- `{slug}/season_seeds.md`
- `{slug}/02_story_bible_review.md`

---

## Phase 3: 시즌 구조 설계

**실행 모드:** 단일 서브 에이전트

`season-planner`를 호출한다. 시즌 씨앗을 시즌 아크로 확장하고, 피날레·후킹·복선 흐름을 정의한다.

- 단권 소설은 `s01`로 처리한다
- 시즌 1은 완전 상세로 작성하고, 시즌 2 이후는 사용자가 명시적으로 요청하지 않는 한 방향/씨앗 수준으로만 작성한다

**입력:** `{slug}/02_story_bible.md`, `{slug}/02_story_bible.json`, `{slug}/season_seeds.md`, 캐릭터·세계관 파일 전체, 요청 시즌 수
**출력:**
- `{slug}/03_season_plan.md`
- `{slug}/seasons/s01/season_bible.md` (시즌 1 완전 상세)
- `{slug}/seasons/s02/season_bible.md` (시즌 2 존재 시, 방향 수준)
- 이후 시즌도 동일 패턴

---

## Phase 4: 챕터 플롯 작성

**실행 모드:** 단일 서브 에이전트 (시즌별 순차)

`chapter-plotter`를 호출해 각 시즌의 챕터별 플롯을 설계한다. 챕터 플랜은 Phase 6의 `chapter-novelist`가 직접 참조하는 저술 지도다.

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

**출력:**
- `{slug}/04_chapter_plan.md` — 전체 챕터 플랜 요약
- `{slug}/seasons/s01/chapter_plan.md`
- `{slug}/seasons/s02/chapter_plan.md` (시즌 2 이상 존재 시)

---

## Phase 5: 플롯/시즌 리뷰

**실행 모드:** 에이전트 팀 (검증)

Phase 3·4의 산출물을 검토해 Phase 6 집필 전에 구조적 문제를 잡는다.

- `story-bible-reviewer`가 챕터 플랜이 스토리 바이블과 충돌하지 않는지 점검한다
- `continuity-keeper`가 챕터 플랜 수준의 복선 흐름과 캐릭터 상태 연속성을 미리 확인한다
- 리뷰 결과를 `{slug}/05_review_log.md`에 기록한다
- Critical 문제가 있으면 사용자에게 보고하고 해당 Phase(3 또는 4)를 재실행한다. Should 이하는 리뷰 로그에 기록하고 진행한다

**출력:** `{slug}/05_review_log.md`

---

## Phase 6: 챕터 집필

**실행 모드:** 에이전트 팀 (최대 3개 동시 챕터)

가장 긴 Phase다. 시즌 단위로 진행하며, 한 시즌이 완료된 후 다음 시즌으로 넘어간다.

**팀 구성:**
- `chapter-novelist` × 최대 3 — 챕터별 집필
- `novel-style-guardian` × 1 — 실시간 스타일 검수
- `continuity-keeper` × 1 — 챕터 완료마다 연속성 갱신

**절차:**

1. `TaskCreate`로 해당 시즌의 챕터들을 task로 등록한다
2. 최대 3개의 챕터를 동시에 할당한다. 인접 챕터를 같은 저술가에게 주어 전환부 조율 부담을 줄인다
3. 각 `chapter-novelist`는 초안 완성 후 `SendMessage`로 `novel-style-guardian`에게 리뷰 요청
4. `novel-style-guardian`은 `lightnovel-style-guide.md` 기준 8개 항목으로 검수하고 피드백 전달
5. `chapter-novelist`가 수정 후 `{CCC}_final.md` 저장, `continuity-keeper`에게 완료 보고
6. `continuity-keeper`가 연속성 레코드 갱신. Critical 경고 시 해당 챕터 집필 중단 후 수정 요청
7. 시즌 내 모든 챕터 완료 후 다음 Phase로 진행

**동시 챕터 수 제한 이유:** 너무 많은 저술가가 동시에 작업하면 연속성 충돌이 급격히 늘어난다. 3명이 상한선이다.

**출력:**
- `{slug}/seasons/sNN/chapters/{CCC}_draft.md`
- `{slug}/seasons/sNN/chapters/{CCC}_final.md`

---

## Phase 7: 문체/대사/시점/연속성 검수

**실행 모드:** 에이전트 팀 (챕터별 병렬 처리 가능)

Phase 6에서 검수가 이미 챕터별로 이루어졌으나, 이 Phase에서는 **시즌 전체를 통으로 보는** 검수를 수행한다.

- `novel-style-guardian`이 시즌 원고 전체의 톤 일관성을 점검한다 (챕터별 피드백과 달리 전체 흐름 관점)
- `continuity-keeper`가 시즌 전체의 복선 회수 여부, 캐릭터 아크 완결성, 타임라인 충돌을 최종 점검한다
- 발견된 문제는 `novel-style-guardian` 또는 `continuity-keeper`가 해당 챕터의 `chapter-novelist`에게 수정 요청을 보낸다
- 모든 Critical 문제가 해소되면 Phase 8로 진행한다

**출력:**
- `{slug}/style_log.md` (누적 append)
- `{slug}/continuity/continuity_log.md`
- `{slug}/continuity/timeline.md`
- `{slug}/continuity/foreshadowing_tracker.md`
- `{slug}/continuity/character_state_table.md`

---

## Phase 8: 통합 편집

**실행 모드:** 단일 서브 에이전트

`novel-editor`를 호출한다. 모든 챕터 최종본을 시즌 원고로, 전체 원고(`04_manuscript.md`)로 통합한다. 저자 노트 제거, 전환부 정리, 용어 통일, 서문·작가 후기 작성, `book_manifest.json` 생성을 수행한다.

**출력:**
- `{slug}/seasons/sNN/season_manuscript.md`
- `{slug}/04_manuscript.md`
- `{slug}/book_manifest.json`

---

## Phase 9: 표지 + EPUB 빌드

**실행 모드:** 서브 에이전트 (표지 먼저, 완료 후 EPUB 빌드)

기존 하네스의 `cover-designer`와 `epub-builder`를 그대로 재사용한다. 입력 포맷이 동일하므로 호환성 문제가 없다.

1. `cover-designer` → `{slug}/cover.png` 생성 (MCP > API > ImageMagick 폴백)
2. 표지 생성 완료 후 `epub-builder` 호출 → `epub-build/scripts/build_epub.sh` 실행
3. `epub-builder`가 EPUB 빌드 직후 **책 소개 markdown**을 함께 산출

**EPUB 메타데이터:**
- 저자: Phase 0에서 추출한 값, 없으면 기본값 `Toby-AI`
- 제목: Phase 2에서 확정된 작품 제목
- 버전: 초기 실행 `1.0.0`, 재실행 시 증가
- 언어: `ko`

**출력:**
- `{작품-제목}-v{version}.epub` (프로젝트 루트)
- `{작품-제목}-v{version}.md` (프로젝트 루트 — 책 소개 markdown)
- `{slug}/cover.png`
- `{slug}/build_log.md`

---

## 에러 핸들링

| 시나리오 | 대응 |
|---------|------|
| 리서치 에이전트 타임아웃 | 가용 결과만으로 `01_reference.md` 작성, 누락 섹션 명시 후 진행 |
| `story-bible-reviewer` Fail 판정 | 사용자에게 보고, `story-bible-planner` 재작업 요청 |
| `continuity-keeper` Critical 경고 | 해당 챕터 finalizing 중단, 저술가에게 수정 지시 |
| 스타일 가디언과 3회 왕복 합의 실패 | 저술가 최종본 채택, `style_log.md`에 "합의 실패" 기록 |
| `[LOCKED]` Canon 위반 감지 | `continuity-keeper`가 차단, `story-bible-planner`에게 공식 개정 절차 요청 |
| 표지 생성 실패 | ImageMagick 폴백 → 단순 타이포그래피 표지. 폴백도 실패 시 사용자 알림 후 표지 없이 빌드 |
| EPUB 빌드 실패 | pandoc 에러 메시지 그대로 보고, `04_manuscript.md`는 보존 |

---

## 데이터 전달 규칙

| 방식 | 용도 |
|------|------|
| 파일 기반 (`{slug}/`) | 모든 Phase 간 산출물 전달, 감사 추적 |
| 메시지 기반 (`SendMessage`) | Phase 2·5의 생성-검증 왕복, Phase 6·7의 팀 내 검수 피드백 |
| 태스크 기반 (`TaskCreate`) | Phase 6의 챕터 작업 분배·진행 추적 |
| 반환값 기반 | 서브 에이전트 모드(Phase 1·3·4·8·9)의 결과 수집 |

파일명 컨벤션:
- Phase 산출물: `{NN}_{artifact}.md` (NN = Phase 번호 2자리)
- 챕터: `{CCC}_draft.md` / `{CCC}_final.md` (CCC = 3자리 제로 패딩)
- 시즌 경로: `seasons/s{NN}/` (NN = 2자리 제로 패딩)

---

## 부분 재실행 규칙

완성된 작품에 수정 요청이 생기면 해당 Phase만 재실행한다. 재실행 시 버전은 **마이너 증가** (`v1.0.0` → `v1.1.0`), 사용자가 명시하면 그 값을 사용한다.

| 요청 유형 | 재실행 Phase | 백업 규칙 |
|----------|------------|---------|
| 스토리 바이블 수정 | Phase 2 → 3 → 4 → 5 재실행 | `02_story_bible.md` → `02_story_bible_v{N}.md` |
| 시즌 구조 수정 | Phase 3 → 4 → 5 재실행 | `03_season_plan.md` → `03_season_plan_v{N}.md` |
| 단일 챕터 재작성 | Phase 6 (해당 챕터만) → Phase 7 | `{CCC}_draft.md` → `{CCC}_draft_v{N}.md` |
| 표지 교체 | Phase 9 (`cover-designer`만) | `cover.png` → `cover_v{N}.png` |
| EPUB 재빌드 | Phase 9 (`epub-builder`만) | 기존 EPUB → `_prev/` 이동 |

---

## 실행 후 피드백

모든 Phase 완료 및 EPUB 산출 후:
1. 사용자에게 EPUB 경로 + 책 소개 markdown 경로 + 요약 보고
2. "개선할 부분이 있나요?"를 짧게 질문한다 (강요하지 않음)
3. 피드백이 오면 위 부분 재실행 규칙에 따라 해당 Phase만 재실행
