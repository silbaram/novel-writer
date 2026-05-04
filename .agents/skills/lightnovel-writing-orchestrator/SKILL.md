---
name: lightnovel-writing-orchestrator
description: Use for 소설/라노벨 Korean fiction workflows from premise to EPUB, including story bible, seasons, chapters, review, cover, and build.
---

# Lightnovel Writing Orchestrator

> Codex 변환 참고: Claude 전용 팀/메시지/태스크 명령은 Codex 부모 세션이 서브에이전트를 호출하고, 결과를 파일 경로와 반환값으로 받아 다음 에이전트 프롬프트에 전달하는 방식으로 해석한다.

장르·분위기·주인공 아이디어를 받아 스토리 바이블 → 시즌 구조 → 챕터 집필 → EPUB 빌드까지 전 과정을 조율한다. 각 Phase에서 전문 에이전트를 호출하고, 중간 산출물을 `{slug}/` 하위에 축적한 뒤 최종 EPUB을 프로젝트 루트에 만든다.

> **저작권 원칙:** 기존 저작물(소설·웹툰·게임·애니메이션 등)의 캐릭터·세계관·고유 설정·문장을 허가 없이 복사하거나 직접 전용하지 않는다. 오마주·패러디를 의도하더라도 독립적 설정으로 치환한다. 이 원칙은 모든 Phase의 에이전트에 공통 적용된다.

---

## 에이전트 통신 원칙

**모든 에이전트 간 통신은 오케스트레이터가 중계한다.** 서브에이전트는 다른 에이전트에게 직접 메시지를 보낼 수 없다. 에이전트는 결과를 파일에 저장하고 반환값(result)으로 오케스트레이터에게 돌려준다. 오케스트레이터가 그 결과를 다음 에이전트 프롬프트에 실어 순차적으로 호출한다.

```
[오케스트레이터] → Agent(A) → 파일 저장 + 반환
[오케스트레이터] → A의 반환값을 읽어 Agent(B) 프롬프트에 포함 → Agent(B) → 파일 저장 + 반환
```

에이전트 파일의 "팀 통신 프로토콜" 섹션이 직접 메시지 전달을 언급하더라도, 실제 실행에서는 이 원칙을 따른다. 오케스트레이터가 라우팅 책임을 전담한다.

---

## 실행 모드 요약

| Phase | 이름 | 실행 모드 |
|-------|------|----------|
| 0 | 소설 요청 분석 | 인라인 |
| 1 | 소재/세계관 리서치 | 서브 에이전트 (병렬 가능) |
| 2 | 스토리 바이블 작성 | 단일 서브 → 오케스트레이터 중계 왕복 (생성-검증) |
| 3 | 시즌 구조 설계 | 단일 서브 |
| 4 | 챕터 플롯 작성 | 단일 서브 (시즌 1 우선, 이후 시즌은 아래 규칙 참조) |
| 5 | 집필 전 종합 검증 | 순차 서브 에이전트 4단계 (바이블·시즌구조·챕터플랜·연속성) |
| 6 | 챕터 집필 | 오케스트레이터 주도 순환 (최대 3개 병렬 초안 → 순차 검수) |
| 7 | 문체/연속성 검수 | 순차 서브 에이전트 (시즌 전체 관점) |
| 8 | 통합 편집 | 단일 서브 |
| 8.5 | 본문 삽화 프롬프트/파일 계약 | 서브 에이전트 (삽화 슬롯 → 외부 생성용 프롬프트/경로) |
| 9 | 표지 + EPUB 빌드 | 서브 에이전트 (표지 먼저, 완료 후 EPUB) |

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
- `{slug}/` 존재 + 부분 수정 요청 → 해당 Phase만 재실행 (아래 "부분 재실행 규칙" 참조)
- `{slug}/` 존재 + 새 입력 → `{slug}_prev-{timestamp}/`로 이동 후 새 실행

---

## Phase 1: 소재/세계관 리서치

**실행 모드:** 서브 에이전트 (병렬 가능)

**목적:** 작품의 소재·배경과 관련된 실세계 자료(역사·신화·사회·과학·장르 관행 등)를 수집한다. 완전 창작 세계관이라면 같은 장르 독자 반응·선행 작품 트렌드 리서치로 대체한다.

- `web-researcher`와 `community-researcher`를 병렬 서브에이전트로 호출한다
- 논픽션 소재가 포함된 경우(역사물·SF·무협 등) `paper-researcher`를 추가 호출한다
- 순수 창작 세계관이고 사용자가 "리서치 없이 바로 진행"을 요청한 경우 이 Phase를 건너뛰고 빈 `01_reference.md`를 생성한 뒤 Phase 2로 이동한다

**입력:** 장르, 핵심 아이디어, 배경 설정 키워드
**출력:** `{slug}/01_reference.md` — 세계관·소재 레퍼런스 (섹션: 장르 관행, 배경 자료, 독자 기대, 유사 작품 분석, 참고문헌)

Codex 에이전트 파일은 기본 모델을 `gpt-5.5`로 설정한다. 계정에서 사용할 수 없으면 `gpt-5.4` 또는 부모 세션의 가용 모델을 따른다.

---

## Phase 2: 스토리 바이블 작성

**실행 모드:** 단일 서브 에이전트 → 오케스트레이터 중계 왕복 (생성-검증)

픽션의 기반 설정 전체를 이 Phase에서 확정한다.

> **범위 제한:** Phase 2는 챕터별 상세 플롯을 작성하지 않는다 (Phase 4). 시즌별 상세 아크도 작성하지 않는다 (Phase 3). "어떤 세계에서, 어떤 인물이, 어떤 갈등을 가지는가"만 다룬다.

**절차:**

1. `story-bible-planner`를 호출한다. 10단계 내부 절차를 통해 스토리 바이블을 작성하고 파일로 저장한다
2. `story-bible-reviewer`를 호출한다. 8개 검토 축으로 바이블을 평가해 `{slug}/02_story_bible_review.md`에 저장하고 결과를 반환한다
3. 오케스트레이터가 리뷰 결과를 읽어 `story-bible-planner`를 재호출한다 (피드백 내용을 프롬프트에 포함). 최대 2회 왕복
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

**시즌 2+ 챕터 플롯 작성 시점:**
- Phase 4 최초 실행 시 시즌 1 챕터 플롯만 작성한다. 시즌 2+는 Phase 3에서 방향 수준으로만 존재한다
- 시즌 N의 집필(Phase 6)이 완료되고 Phase 7·8을 통과한 뒤, 다음 시즌으로 진행하기 전에 해당 시즌의 Phase 4를 재실행한다
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

**출력:**
- `{slug}/04_chapter_plan.md` — 전체 챕터 플랜 요약
- `{slug}/seasons/s01/chapter_plan.md`
- `{slug}/seasons/s02/chapter_plan.md` (시즌 2 이상 존재 시)

---

## Phase 5: 집필 전 종합 검증

**실행 모드:** 순차 서브 에이전트 4단계

Phase 2~4의 모든 산출물(스토리 바이블·시즌 구조·챕터 플랜)을 집필 전에 종합 검증한다. 이 Phase를 통과해야만 Phase 6 집필을 시작할 수 있다.

**단계 1 — 스토리 바이블 최종 점검 (`story-bible-reviewer`, Mode A)**

오케스트레이터가 `story-bible-reviewer`를 호출한다. 목적: Phase 2 이후 수정 사항이 바이블 전체 정합성을 훼손하지 않았는지 최종 확인. 섹션 1의 8개 검토 축 전체를 적용한다. 결과를 반환한다.

**단계 2 — 시즌 구조 서사 품질 점검 (`narrative-review` 스킬, 섹션 4)**

오케스트레이터가 단계 1 결과를 읽은 뒤 `narrative-review` 스킬의 **섹션 4 — 시즌 구조 검토**를 실행한다. `{slug}/seasons/s01/season_bible.md`를 대상으로 7개 축을 점검하고 판정을 반환한다.

**단계 3 — 챕터 플랜-바이블 정합성 점검 (`story-bible-reviewer`, Mode B)**

오케스트레이터가 단계 2 결과를 읽은 뒤 `story-bible-reviewer`를 재호출한다. 목적: `{slug}/seasons/s01/chapter_plan.md`와 스토리 바이블 간의 갈등 정합성·Canon 상태 준수·시즌 씨앗 연결 집중 점검. 결과를 반환한다.

**단계 4 — 복선·연속성 사전 점검 (`continuity-keeper`)**

오케스트레이터가 단계 3 결과를 읽은 뒤 `continuity-keeper`를 호출한다. 목적: 챕터 플랜에 선언된 복선 심기/회수 계획이 물리적으로 실현 가능한지, 캐릭터 상태 초기값이 바이블과 일치하는지 사전 확인. Critical 경고 목록을 반환한다.

**통합 판정 및 출력:**

- 네 단계 결과를 `{slug}/05_review_log.md`에 통합 기록한다
- Critical 문제가 하나라도 있으면 사용자에게 보고하고 해당 Phase(2, 3, 또는 4)를 재실행한다
- Should 이하는 리뷰 로그에 기록하고 Phase 6으로 진행한다
- 모든 단계 Pass 또는 Conditional Pass이면 오케스트레이터가 사용자에게 "집필 전 종합 검증 완료 — Phase 6 집필을 시작합니다"를 보고한다

**출력:** `{slug}/05_review_log.md`

---

## Phase 6: 챕터 집필

**실행 모드:** 오케스트레이터 주도 순환 (최대 3개 병렬 초안 → 순차 검수)

가장 긴 Phase다. 시즌 단위로 진행하며, 한 시즌이 완료된 후 다음 시즌으로 넘어간다.

**챕터 번호 정책:** 챕터 번호(`{CCC}`)는 **시즌별로 리셋**한다. `s01/chapters/001`, `s02/chapters/001` 형태로 관리한다. 파일 경로에 시즌 정보가 포함되어 있으므로 전체 고유성이 보장된다.

**절차:**

1. Codex 작업 계획으로 해당 시즌의 챕터 목록을 태스크로 등록한다
2. 오케스트레이터가 최대 3개의 챕터를 `chapter-novelist`에게 병렬 호출한다 (병렬 서브에이전트 호출). 인접 챕터는 같은 저술가에게 묶어 전환부 맥락을 보존한다
3. 모든 병렬 초안이 완성되면, 오케스트레이터가 각 `{CCC}_draft.md`를 **순차적으로** `novel-style-guardian`에게 전달해 검수한다. 스타일 가디언은 피드백을 `{CCC}_review.md`(임시)와 `style_log.md`(누적)에 저장하고 결과를 반환한다
4. 오케스트레이터가 피드백을 읽어 해당 `chapter-novelist`를 재호출해 수정을 요청한다 (피드백 내용을 프롬프트에 포함). `chapter-novelist`가 `{CCC}_final.md`를 저장하고 반환한다
5. 오케스트레이터가 `continuity-keeper`를 호출한다 (`{CCC}_final.md` 경로 전달). `continuity-keeper`가 연속성 레코드를 갱신하고 결과를 반환한다
6. Critical 경고가 반환되면 오케스트레이터가 해당 `chapter-novelist`를 재호출해 수정을 지시한다
7. 해당 챕터 완료 후 다음 배치(3개)로 넘어간다. 시즌 내 모든 챕터 완료 후 다음 Phase로 진행한다

**병렬 → 순차 혼합 이유:** 초안은 병렬로 빠르게 생성하고, 검수·연속성 갱신은 순차로 처리해 충돌을 방지한다.

**출력:**
- `{slug}/seasons/sNN/chapters/{CCC}_draft.md`
- `{slug}/seasons/sNN/chapters/{CCC}_review.md` (스타일 가디언 피드백, 임시)
- `{slug}/seasons/sNN/chapters/{CCC}_final.md`

---

## Phase 7: 문체/대사/시점/연속성 검수

**실행 모드:** 순차 서브 에이전트 (시즌 전체 관점)

Phase 6에서 검수가 이미 챕터별로 이루어졌으나, 이 Phase에서는 **시즌 전체를 통으로 보는** 검수를 수행한다.

**절차:**
1. 오케스트레이터가 `novel-style-guardian`을 호출한다. 시즌 원고 전체의 톤 일관성 점검을 목적으로 명시한다 (챕터별 피드백이 아닌 전체 흐름 관점). 가디언은 문제 목록을 반환한다
2. 오케스트레이터가 `continuity-keeper`를 호출한다. 시즌 전체의 복선 회수 여부, 캐릭터 아크 완결성, 타임라인 충돌 최종 점검을 목적으로 명시한다. Critical 경고 목록을 반환한다
3. 오케스트레이터가 두 결과를 취합해 수정이 필요한 챕터를 식별하고, 해당 `chapter-novelist`를 재호출해 수정을 지시한다
4. Critical 미해결 항목이 있으면 **Phase 8(통합 편집)까지만 진행**하고, 오케스트레이터가 사용자에게 수동 확인을 요청할 때까지 **Phase 9(최종 EPUB 빌드)는 중단**한다
5. Critical 이슈가 해소되거나 사용자 수동 확인이 완료되면 Phase 9로 진행한다

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

## Phase 8.5: 본문 삽화 프롬프트/파일 계약

**실행 모드:** 서브 에이전트

`interior-illustrator`를 호출한다. 표지가 아니라 라노벨 본문 중간 삽화의 장면 선정, 외부 이미지 생성용 프롬프트, 저장 파일 경로 계약을 담당한다. 이미지는 Codex/Claude가 직접 생성하지 않는다. 사용자가 OpenAI API, Claude, 웹 LLM, Midjourney, Stable Diffusion, NovelAI 등에서 프롬프트로 이미지를 생성한 뒤 약속된 경로에 PNG로 저장하면 삽화가 포함된다.

챕터 플랜 기준의 예비 슬롯이 있더라도, Phase 6의 최종 원고와 Phase 8의 통합 원고를 우선해 장면 위치와 스포일러 강도를 보정한다.

**절차:**
1. `interior-illustrator`가 `novel-illustration` 스킬을 사용해 `{slug}/illustrations/illustration_plan.md`를 작성 또는 갱신한다
2. 단권 20챕터 기준 기본값은 컬러 프론트피스 1장 + 본문 삽화 6~10장이다. 사용자 지정이 있으면 그 수량을 따른다
3. 캐릭터 외형·의상·소품 일관성을 `{slug}/illustrations/style_sheet.md`에 기록한다
4. 각 이미지의 외부 생성 프롬프트를 `{slug}/illustrations/sNN/*_prompt.md`에 저장하고, 저장해야 할 PNG 경로를 명시한다
5. PNG 파일이 아직 없으면 상태를 `prompt_ready` 또는 `image_missing`으로 표시한다. Phase 9 전에 사용자가 해당 경로에 PNG를 저장하면 EPUB에 포함한다
6. `novel-editor` 또는 오케스트레이터가 `04_manuscript.md`에 Markdown 이미지 마커를 삽입한다

**출력:**
- `{slug}/illustrations/illustration_plan.md`
- `{slug}/illustrations/style_sheet.md`
- `{slug}/illustrations/sNN/{CCC}_{scene_slug}_prompt.md`
- `{slug}/illustrations/sNN/{CCC}_{scene_slug}.png` (외부 도구가 저장해야 하는 대상 파일)
- 삽화가 포함되도록 갱신된 `{slug}/04_manuscript.md`

---

## Phase 9: 표지 + EPUB 빌드

**실행 모드:** 서브 에이전트 (표지 먼저, 완료 후 EPUB 빌드)

기존 하네스의 `cover-designer`와 `epub-builder`를 그대로 재사용한다. 입력 포맷이 동일하므로 호환성 문제가 없다.

> **게이트 규칙(강제):** `continuity/continuity_log.md`에 Critical 미해결 항목이 하나라도 남아 있으면 Phase 9 실행을 금지한다. 오케스트레이터는 수동 확인 요청을 사용자에게 전달하고, 승인/수정 완료 전까지 EPUB 빌드를 호출하지 않는다.

1. `cover-designer` → `{slug}/cover.png` 생성 (Codex 이미지 생성 도구/스킬 > API > ImageMagick 폴백)
2. 본문 삽화 마커가 있으면 `04_manuscript.md`의 상대 이미지 경로와 실제 PNG 파일 존재 여부를 확인한다. PNG가 없으면 해당 마커를 빌드에서 제외하거나 사용자 확인 후 진행한다
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
| 반환값 + 오케스트레이터 중계 | 에이전트 간 피드백 전달 (Phase 2·5·6·7). 에이전트는 결과를 파일에 저장하고 반환하며, 오케스트레이터가 읽어 다음 에이전트 프롬프트에 포함한다 |
| `Codex 작업 계획` | Phase 6의 챕터 작업 분배·진행 추적 |
| 반환값 기반 | 서브 에이전트 모드(Phase 1·3·4·8·9)의 결과 수집 |

파일명 컨벤션:
- Phase 산출물: `{NN}_{artifact}.md` (NN = Phase 번호 2자리)
- 챕터: `{CCC}_draft.md` / `{CCC}_review.md` / `{CCC}_final.md` (CCC = 시즌 내 3자리 제로 패딩, 시즌별 리셋)
- 시즌 경로: `seasons/s{NN}/` (NN = 2자리 제로 패딩)

---

## 부분 재실행 규칙

완성된 작품에 수정 요청이 생기면 해당 Phase만 재실행한다. 재실행 시 버전은 **마이너 증가** (`v1.0.0` → `v1.1.0`), 사용자가 명시하면 그 값을 사용한다.

| 요청 유형 | 재실행 Phase | 백업 규칙 |
|----------|------------|---------|
| 스토리 바이블 수정 | Phase 2 → 3 → 4 → 5 재실행 | `02_story_bible.md` → `02_story_bible_v{N}.md` |
| 시즌 구조 수정 | Phase 3 → 4 → 5 재실행 | `03_season_plan.md` → `03_season_plan_v{N}.md` |
| 단일 챕터 재작성 | Phase 6 (해당 챕터만) → Phase 7 | `{CCC}_draft.md` → `{CCC}_draft_v{N}.md` |
| 본문 삽화 추가/교체 | Phase 8.5 | 기존 PNG → `{name}_v{N}.png` |
| 표지 교체 | Phase 9 (`cover-designer`만) | `cover.png` → `cover_v{N}.png` |
| EPUB 재빌드 | Phase 9 (`epub-builder`만) | 기존 EPUB → `_prev/` 이동 |

---

## 실행 후 피드백

모든 Phase 완료 및 EPUB 산출 후:
1. 사용자에게 EPUB 경로 + 책 소개 markdown 경로 + 요약 보고
2. "개선할 부분이 있나요?"를 짧게 질문한다 (강요하지 않음)
3. 피드백이 오면 위 부분 재실행 규칙에 따라 해당 Phase만 재실행
