좋습니다. **분리하는 게 맞습니다.**
정확히 말하면 지금 구조에는 “검수자”는 있는데, **실제로 문장을 다시 다듬는 퇴고자**가 없습니다. 그래서 `chapter-novelist`가 초안 작성도 하고, 피드백 반영도 하고, 최종본도 저장합니다. 이러면 작가가 자기 글을 자기가 객관적으로 퇴고하는 꼴이라, 인간 세계에서도 망하는 흔한 패턴입니다. AI라고 다를 리가요.

## 결론

추천 구조는 이겁니다.

```text
chapter-drafter / chapter-novelist
        ↓ 초안 작성
novel-style-guardian
        ↓ 문제 진단만 함
chapter-prose-reviser
        ↓ 실제 문장 퇴고
novel-style-guardian
        ↓ 짧은 2차 검수
continuity-keeper
        ↓ 연속성 갱신
{CCC}_final.md
```

현재 저장소에서는 `chapter-novelist`가 챕터 계획을 읽고 `style-guides/lightnovel-style-guide.md` 기준으로 초안을 작성한 뒤, 피드백을 받아 `{CCC}_final.md`까지 저장하는 역할을 맡고 있습니다. 즉 “초안 작성자”와 “수정 반영자”가 한 에이전트 안에 섞여 있습니다. ([GitHub][1])

반면 `novel-style-guardian`은 초안을 읽고 스타일 기준으로 평가하고, 원문 인용과 수정 제안을 만드는 검수자입니다. 직접 본문 전체를 퇴고하는 역할은 아닙니다. ([GitHub][2])

또 `novel-editor`는 최종 챕터들을 시즌 원고와 EPUB 원고로 통합하는 역할이고, 원칙상 챕터 본문을 재서술하지 않는다고 되어 있습니다. 그러니까 최종 통합 단계에서도 문장 퇴고가 크게 일어나지 않습니다. ([GitHub][3])

그래서 지금 구조의 빈칸은 명확합니다.

> **초안 작성자와 스타일 검수자 사이에는 있는데, 스타일 검수자와 최종본 사이에 “실제 퇴고자”가 없다.**

이걸 추가하는 게 좋습니다.

---

## 왜 분리하는 게 좋은가

Claude Code 공식 문서 기준으로도 subagent는 특정 작업에 특화된 별도 컨텍스트에서 작동하고, 각자 다른 시스템 프롬프트와 도구 권한을 가질 수 있습니다. 컨텍스트 보존, 제약 조건 적용, 동작 특화, 비용 제어 같은 장점도 문서에 명시되어 있습니다. ([Claude][4])

이 문체 문제에는 그 장점이 딱 맞습니다.

초안 작성자는 이런 일을 잘해야 합니다.

```text
플롯 진행
씬 구성
캐릭터 대사
사건 전개
챕터 훅
감정선
복선 사용
```

퇴고자는 이런 일을 잘해야 합니다.

```text
있었다/였다/했다 반복 제거
묘사 문단 연결
POV 감각 흐름 강화
문장 호흡 조절
단문과 중문 배치
대사 사이 행동 삽입
도윤식 화자 목소리 보강
```

이 둘은 능력이 겹치긴 하지만, 집중점이 다릅니다.
한 에이전트에게 둘 다 시키면 초안 작성 중에는 플롯을 챙기느라 문장 리듬을 놓치고, 수정 중에는 자기 초안을 보존하려고 소극적으로 고칩니다. 자식 사진 보정하는 부모처럼 객관성이 녹아내립니다.

---

## 단, “작성자 2명”으로 만들면 안 됩니다

분리할 때 조심해야 합니다.

나쁜 구조는 이겁니다.

```text
초안 작성 에이전트 A
퇴고 작성 에이전트 B
```

이렇게만 해두면 B가 퇴고가 아니라 **재창작**을 할 수 있습니다. 그러면 사건 순서, 대사 의도, 캐릭터 감정선, 복선 위치가 슬쩍 바뀝니다. 문장은 부드러워졌는데 이야기가 다른 물건이 되는 거죠. 아주 세련된 사고입니다.

좋은 구조는 이겁니다.

```text
초안 작성자 = 이야기 생성
검수자 = 문제 진단
퇴고자 = 진단된 문제를 기준으로 문장만 개선
연속성 관리자 = 바뀐 내용이 Canon을 깨지 않았는지 확인
```

즉, **퇴고자는 작가가 아니라 문장 수리공**이어야 합니다.

---

## 추천 에이전트 구성

### 1. `chapter-novelist` 또는 `chapter-drafter`

현재 `chapter-novelist`를 그대로 써도 됩니다.
다만 역할을 바꾸는 게 좋습니다.

현재:

```text
초안 작성 → 스타일 피드백 반영 → final 저장
```

추천:

```text
초안 작성 → draft 저장
```

이 에이전트는 더 이상 `{CCC}_final.md`를 만들지 않게 하는 편이 깔끔합니다. 최종본은 퇴고자가 만들거나, 퇴고 후 오케스트레이터가 승격시키면 됩니다.

역할:

```text
- 챕터 플랜을 본문으로 변환
- 사건 순서와 감정선을 살림
- 대사와 장면 진행을 우선
- 문체는 기본 가이드만 지킴
- 과도한 윤문은 하지 않음
```

출력:

```text
{slug}/P04_continuity/sNN/chapters/{CCC}_draft.md
```

저자 노트에는 지금처럼 장면 밀도 패스 항목을 유지하되, 하나를 추가하면 좋습니다.

```markdown
### 퇴고 주의 지점
- 새 장소/인물/사물 묘사가 딱딱할 수 있는 문단
- 의도적으로 단문을 유지한 구간
- 바꾸면 안 되는 대사/복선/훅
```

이게 있어야 퇴고자가 쓸데없이 개그 타이밍까지 합쳐버리지 않습니다.

---

### 2. `novel-style-guardian`

현재 역할 유지가 좋습니다.

이 에이전트는 직접 고치지 말고 **진단만** 해야 합니다.
현재 파일도 원문 인용과 구체적 수정 제안을 하도록 되어 있고, 과교정을 막기 위해 챕터당 수정 제안을 5~10건으로 제한합니다. ([GitHub][2])

다만 `chapter-prose-reviser`가 생기면 출력 형식을 조금 바꾸는 게 좋습니다.

기존:

```markdown
[원문] ...
[제안] ...
```

추천:

```markdown
## 퇴고 지시용 리뷰

### Must Fix
- 원문:
- 문제:
- 퇴고 방향:
- 보존해야 할 것:

### Should Fix
...

### Keep
- 유지해야 할 단문/대사/개그 타이밍
```

특히 `Keep`가 중요합니다.
퇴고자는 고치는 데 취한 나머지 좋은 단문까지 갈아버릴 수 있습니다. 인간 편집자도 가끔 그러는데, AI라고 자비가 있겠습니까.

---

### 3. 새 에이전트: `chapter-prose-reviser`

이게 핵심입니다.

이 에이전트는 **초안을 새로 쓰는 게 아니라, 스타일 리뷰를 반영해 문장 흐름을 퇴고**합니다.

역할:

```text
- draft.md 본문을 읽는다
- style_review.md를 읽는다
- lightnovel-style-guide.md를 읽는다
- 캐릭터 voice profile을 읽는다
- 플롯, 사건 순서, Canon은 바꾸지 않는다
- 문장 리듬과 묘사 흐름만 개선한다
- revised 또는 final 파일을 저장한다
```

출력은 둘 중 하나를 추천합니다.

안전한 방식:

```text
{CCC}_revised.md
```

그 후 2차 검수 통과 시:

```text
{CCC}_final.md
```

간단한 방식:

```text
{CCC}_final.md
```

개인적으로는 안전한 방식이 낫습니다.
AI에게 바로 최종본을 맡기는 건, 신입에게 운영 DB 권한 주는 것과 비슷합니다. 언젠가 울게 됩니다.

---

## 추천 워크플로우

현재 라노벨 워크플로우는 README에서 챕터 집필 단계가 `chapter-novelist × 3 병렬 → novel-style-guardian → continuity-keeper` 식으로 설명되어 있습니다. ([GitHub][5])

이걸 이렇게 바꾸는 게 좋습니다.

```text
6. 챕터 초안
   chapter-novelist × 3 병렬
   → {CCC}_draft.md

7. 스타일 리뷰
   novel-style-guardian
   → {CCC}_review.md

8. 문장 퇴고
   chapter-prose-reviser
   → {CCC}_revised.md

9. 2차 스타일 확인
   novel-style-guardian
   → 합격 시 {CCC}_final.md 승격
   → 불합격 시 prose-reviser 1회 재수정

10. 연속성 갱신
   continuity-keeper
   → continuity_log.md / timeline.md / character_state_table.md 갱신
```

공식 문서에서도 다단계 워크플로우는 subagent를 순차적으로 체인하는 방식으로 구성할 수 있다고 설명합니다. 다만 subagent는 다른 subagent를 직접 생성할 수 없으므로, 오케스트레이터가 체인을 중계해야 합니다. ([Claude][4])

그러니 `novel-style-guardian`이 직접 `chapter-prose-reviser`를 호출하게 만들지 말고, **오케스트레이터가 순서를 관리**하게 해야 합니다.

---

## 새 에이전트 예시

`.claude/agents/chapter-prose-reviser.md`를 추가한다면 이런 식이 좋습니다.

````markdown
---
name: chapter-prose-reviser
description: Revises Korean light novel chapter drafts after style review. Use after novel-style-guardian has produced a review. Improves prose rhythm, POV sensory flow, sentence transitions, and readability without changing plot, canon, scene order, or character intent.
model: opus
skills:
  - novel-prose-revision
---

# Chapter Prose Reviser

라이트노벨/웹소설 챕터 초안을 실제로 퇴고한다.

이 에이전트는 새 이야기를 쓰는 작가가 아니다.  
이미 작성된 초안을 기준으로 문장 흐름, 묘사 연결, 단문 리듬, POV 감각 흐름을 개선하는 문장 퇴고자다.

---

## 핵심 역할

1. `{CCC}_draft.md` 본문과 저자 노트를 읽는다.
2. `{CCC}_review.md`의 스타일 리뷰를 읽는다.
3. `style-guides/lightnovel-style-guide.md`를 기준으로 문장 리듬을 조정한다.
4. 캐릭터 파일과 voice profile이 있으면 서술자 어조를 유지한다.
5. 플롯, 사건 순서, Canon, 복선 위치를 바꾸지 않고 문장만 다듬는다.
6. `{CCC}_revised.md`를 저장한다.
7. 수정 요약을 저자 노트에 추가한다.

---

## 입력 프로토콜

- `{slug}/P04_continuity/sNN/chapters/{CCC}_draft.md`
- `{slug}/P04_continuity/sNN/chapters/{CCC}_review.md`
- `style-guides/lightnovel-style-guide.md`
- `{slug}/P02_bible/02_story_bible.md`
- `{slug}/P02_bible/characters/*.md`
- `{slug}/P02_bible/worldbuilding/*.md`
- `{slug}/P03_planning/sNN/season_bible.md`
- `{slug}/P04_continuity/character_state_table.md`
- `{slug}/P04_continuity/foreshadowing_tracker.md`
- `{slug}/P02_bible/voice_profile.md`가 있으면 반드시 읽는다.

---

## 수정 허용 범위

### 허용

- `있었다/였다/했다/났다` 반복 완화
- 정보 나열형 묘사를 POV 감각 흐름으로 재구성
- 같은 공간/사물 정보 한두 문장으로 묶기
- 문단 마지막에 POV 인물의 반응, 농담, 불편함 추가
- 대화 사이에 손, 시선, 자세, 주변 소리 삽입
- 어색한 연결어미 조정
- 단문-중문-단문 리듬 조정

### 제한적으로 허용

- 문단 내부 문장 순서 조정
- 같은 의미의 짧은 행동 추가
- 이미 암시된 감각을 구체화

### 금지

- 사건 순서 변경
- 새 설정 추가
- 새 인물 추가
- 대사의 의미 변경
- 복선 위치 변경
- 챕터 훅 변경
- 캐릭터의 감정 결론 변경
- `[LOCKED]` Canon 변경
- `[CANDIDATE]` 설정 확정 서술
- 초안을 다른 문체로 전면 재작성

---

## 퇴고 핵심 규칙

### 1. 정보 단문을 인식 단문으로 바꾼다

나쁜 방향:

```text
먼지 냄새가 있었다.
유리등이 있었다.
배지가 달려 있었다.
````

좋은 방향:

```text
먼지 냄새가 코끝을 찔렀다.
고개를 들자 유리등이 눈에 들어왔다.
깃펜이 움직일 때마다 배지가 희미하게 빛났다.
```

### 2. 새 장소 묘사는 몸의 흐름으로 연결한다

권장 흐름:

```text
코끝 → 발밑/손 → 귀 → 시선 → 기억/농담
```

### 3. 단문은 전부 없애지 않는다

유지할 단문:

* 개그 타이밍
* 충격
* 당황한 인식
* 깨달음
* 대사 핑퐁

수정할 단문:

* 배경 정보 나열
* 외형 항목 나열
* 사물 배치 설명

### 4. 퇴고 후 반드시 보존 검사를 한다

아래 항목이 초안과 달라지면 안 된다.

* 챕터 목표
* 사건 순서
* 등장인물의 선택
* 복선의 위치와 의미
* 마지막 훅
* 캐릭터 관계 변화
* Canon 설정

---

## 출력 프로토콜

### `{slug}/P04_continuity/sNN/chapters/{CCC}_revised.md`

```markdown
# {CCC}화. {챕터 제목}

{퇴고된 본문}

---

## 저자 노트 (내부용)

{기존 저자 노트 유지}

### 퇴고 요약
- 수정한 주요 문체 문제:
- 유지한 단문 타이밍:
- 보존한 사건/복선:
- 연속성 변경 여부: 없음 / 있음
- 재검수 필요 지점:
```

---

## 에러 핸들링

* `{CCC}_review.md`가 없으면 전체 퇴고하지 않고, 오케스트레이터에 스타일 리뷰 선행 필요를 보고한다.
* Canon 변경이 필요해 보이면 수정하지 말고 `(설정 확인 필요)`로 표시한다.
* 리뷰 지시와 Canon이 충돌하면 Canon을 우선한다.
* 초안의 의도된 단문인지 판단이 어려우면 유지하고 저자 노트에 기록한다.

````

공식 문서상 subagent 파일은 YAML frontmatter 뒤에 Markdown 시스템 프롬프트를 두는 방식이고, `name`과 `description`이 필수입니다. 또한 `tools`, `model`, `skills` 같은 필드도 사용할 수 있습니다. :contentReference[oaicite:7]{index=7}

여기서는 `skills: novel-prose-revision`을 넣는 걸 추천합니다. 공식 문서에 따르면 `skills` 필드는 subagent 시작 시 특정 skill 내용을 컨텍스트에 주입할 수 있습니다. :contentReference[oaicite:8]{index=8}

---

## 새 스킬도 분리하는 게 좋음

에이전트만 추가하면 지시가 너무 길어집니다.  
퇴고용 스킬을 따로 두는 게 좋습니다.

추가 파일:

```text
.claude/skills/novel-prose-revision/SKILL.md
````

예시:

````markdown
---
name: novel-prose-revision
description: Use to revise Korean light novel prose after a style review, focusing on sentence rhythm, POV sensory flow, description continuity, and readability without changing plot or canon.
---

# Novel Prose Revision

라이트노벨/웹소설 초안을 퇴고하는 절차 가이드다.

---

## 퇴고 순서

### 단계 1 — 보존 대상 확인

먼저 다음을 읽고 바꾸면 안 되는 요소를 표시한다.

- 챕터 목표
- 사건 순서
- 감정 변화
- 복선
- 엔딩 훅
- Canon
- 의도된 단문 타이밍

### 단계 2 — 딱딱한 묘사 문단 탐지

다음 패턴이 있는 문단을 찾는다.

- `있었다/였다/했다/났다` 계열 종결이 3회 이상 반복
- `A에는`, `B에서는`, `C는`, `머리 위에는`, `그 안에서`처럼 위치 주어가 3회 이상 바뀜
- 냄새, 소리, 빛, 촉감이 목록처럼 순서대로 제출됨
- 새 인물 묘사가 외형 항목 나열로만 구성됨
- 문단 안에 POV 인물의 신체 반응, 기억, 농담이 없음

### 단계 3 — 정보 단문을 POV 인식 흐름으로 변환

상태 설명을 동작/감각/반응으로 바꾼다.

```text
A가 있었다 → A가 코끝에 닿았다 / 손바닥에 걸렸다 / 시야에 들어왔다
B는 C였다 → B를 본 순간 C라는 생각이 들었다
D가 달려 있었다 → D가 움직임에 맞춰 흔들렸다
````

### 단계 4 — 묘사 문단 재구성

새 장소는 가능하면 아래 흐름으로 묶는다.

```text
냄새 → 발밑/손 → 소리 → 시선 → 주인공의 기억/농담
```

새 인물은 아래 흐름으로 묶는다.

```text
행동 → 외형 일부 → 태도/시선 → POV 판단
```

핵심 사물은 아래 흐름으로 묶는다.

```text
접촉/시선 → 질감/무게/소리 → 기능 → POV 반응
```

### 단계 5 — 단문 보존 검사

아래 단문은 유지한다.

* 개그 타이밍
* 충격
* 당황한 인식
* 깨달음
* 대사 핑퐁
* 효과음의 결정적 박자

아래 단문은 수정한다.

* 배경 정보 나열
* 외형 항목 나열
* 사물 배치 설명
* 기능 설명만 하는 문장

### 단계 6 — 변경 안전 검사

퇴고 후 아래가 바뀌지 않았는지 확인한다.

* 사건 순서
* 대사 의미
* 캐릭터 감정 결론
* 복선 위치
* 엔딩 훅
* Canon 상태

### 단계 7 — 퇴고 요약 작성

저자 노트에 다음을 추가한다.

```markdown
### 퇴고 요약
- 주요 수정:
- 유지한 단문:
- 보존한 복선:
- Canon 변경 여부:
- 재검수 요청 지점:
```

````

---

## 기존 `chapter-novelist`는 어떻게 바꾸면 좋은가

현재 `chapter-novelist`에는 “오케스트레이터로부터 피드백을 받아 수정 후 `{CCC}_final.md`를 저장”한다는 역할이 들어 있습니다. :contentReference[oaicite:9]{index=9}

이걸 이렇게 바꾸는 게 좋습니다.

기존:

```markdown
4. `{CCC}_draft.md`에 저장하고 결과를 반환한다.
5. 오케스트레이터로부터 피드백을 받아 수정 후 `{CCC}_final.md`를 저장한다.
````

수정:

```markdown
4. `{CCC}_draft.md`에 저장하고 결과를 반환한다.
5. 스타일 리뷰 이후의 문장 퇴고와 최종본 생성은 `chapter-prose-reviser`가 담당한다.
6. `chapter-novelist`는 초안의 플롯, 감정선, 대사 의도, 복선 사용, 엔딩 훅을 저자 노트에 명확히 남긴다.
```

그리고 작업 원칙에 추가하면 좋습니다.

```markdown
- **퇴고 위임 원칙:** 이 에이전트는 초안 작성자다. 초안 작성 중 문장 품질을 기본 수준 이상으로 유지하되, 스타일 리뷰 이후의 세부 윤문은 `chapter-prose-reviser`에게 넘긴다.
- **보존 지점 기록:** 의도적으로 짧게 둔 문장, 개그 타이밍, 복선 문장, 바꾸면 안 되는 대사는 저자 노트의 `퇴고 주의 지점`에 기록한다.
```

---

## `novel-style-guardian`도 살짝 바꾸기

현재 `novel-style-guardian`은 스타일 검수 항목이 꽤 잘 정리되어 있습니다. 특히 장면성 항목에서 새 장소·인물·사물이 POV 인물의 감각 흐름을 타는지, 상태문 나열이 있는지, 감각이 흩어지는지 확인합니다. ([GitHub][2])

여기에 퇴고자 전달용 항목을 추가하면 됩니다.

```markdown
## 퇴고자 전달 규칙

리뷰는 `chapter-prose-reviser`가 바로 사용할 수 있는 형태로 작성한다.

각 지적에는 다음 4개를 포함한다.

1. 원문
2. 문제 유형
3. 보존해야 할 의도
4. 수정 방향

특히 아래 항목은 `Keep`으로 명시한다.

- 개그 타이밍용 단문
- 충격 연출용 효과음
- 대사 핑퐁
- 복선 문장
- 챕터 훅
```

리뷰 형식도 이렇게 바꾸면 좋습니다.

```markdown
### Should
- **원문:** "..."
- **문제:** 상태문 나열 / 위치 주어 반복 / 감각 체크리스트
- **보존:** 도윤이 야근을 떠올리는 회사식 농담
- **퇴고 방향:** 코끝 → 발밑 → 귀 → 시선 흐름으로 재구성

### Keep
- "공짜는 무섭다."
  - 개그 타이밍용 단문이므로 유지
```

---

## `lightnovel-writing-orchestrator` 변경

오케스트레이터가 체인을 명확히 관리해야 합니다.
Claude Code 문서에서도 자동 위임은 `description` 필드와 현재 작업 문맥을 기준으로 일어나며, 필요하면 subagent를 명시적으로 호출할 수 있다고 설명합니다. ([Claude][4])

오케스트레이터에 아래 순서를 박아두는 게 좋습니다.

```markdown
### 챕터 집필 체인

1. `chapter-novelist`
   - 입력: 챕터 플랜, 바이블, 캐릭터, 세계관, 연속성 파일
   - 출력: `{CCC}_draft.md`

2. `novel-style-guardian`
   - 입력: `{CCC}_draft.md`
   - 출력: `{CCC}_review.md`

3. `chapter-prose-reviser`
   - 입력: `{CCC}_draft.md`, `{CCC}_review.md`
   - 출력: `{CCC}_revised.md`

4. `novel-style-guardian` 2차 확인
   - 입력: `{CCC}_revised.md`
   - 출력: 합격 / 재수정 요청

5. 합격 시
   - `{CCC}_revised.md`를 `{CCC}_final.md`로 저장

6. `continuity-keeper`
   - 입력: `{CCC}_final.md`
   - 출력: continuity 갱신
```

재수정 루프는 제한해야 합니다.

```markdown
- 스타일 리뷰 ↔ 퇴고 루프는 최대 2회.
- 2회 후에도 해결되지 않으면 `P00_meta/logs/style_log.md`에 미해결 지점을 기록하고 현재 revised를 final 후보로 채택한다.
```

루프를 제한하지 않으면 AI 둘이 “좀 더 부드럽게”와 “너무 많이 바꿨다”를 영원히 주고받습니다. 인간 회의와 다를 게 없습니다. 굳이 그런 지옥을 자동화할 필요는 없습니다.

---

## 파일 이름 추천

가장 안전한 산출물 구조는 이겁니다.

```text
{slug}/P04_continuity/sNN/chapters/
├── 001_draft.md
├── 001_review.md
├── 001_revised.md
├── 001_review2.md
└── 001_final.md
```

조금 더 단순하게 가면:

```text
001_draft.md
001_review.md
001_final.md
```

하지만 상진님처럼 문체 실험을 계속할 생각이면 `revised.md`를 남기는 편이 훨씬 좋습니다. 나중에 “퇴고자가 어디서 망쳤는지” 볼 수 있으니까요. 디버깅 로그 없는 자동화는 그냥 기도입니다.

---

## 이 구조가 상진님 원고 문제에 특히 잘 맞는 이유

업로드한 1화 원고에서 문제는 전체 문체가 아니라, 새 장소·새 인물·새 사물을 처음 보여줄 때 묘사가 `있었다/였다/났다` 중심으로 항목화되는 부분이었습니다. 예를 들어 길드 등록소 묘사는 냄새, 바닥, 깃펜, 유리등, 먼지가 차례대로 나오면서 장면이 정보 목록처럼 끊겼습니다. 

현재 스타일 가이드도 이 문제를 이미 잡고 있습니다. “단문은 타이밍 장치이며 배경 정보를 항목별로 제출하기 위해 쓰지 말라”, “새 정보를 보여줄 때 사물이 있었다고 선언하기보다 POV 인물의 몸을 통과시키라”, “감각 묘사는 코끝의 냄새 → 발밑의 삐걱임 → 귀에 들어오는 소리 → 고개를 들며 보이는 빛 → 기억/농담처럼 연결하라”는 규칙이 들어 있습니다. ([GitHub][6])

그런데 이 규칙은 초안 작성자에게만 맡기면 누락될 수 있습니다.
초안 작성자는 사건을 진행하느라 바쁩니다. 그러니 퇴고자는 아예 이 문제만 물고 늘어지는 편이 낫습니다.

---

## 최종 추천

저는 이렇게 하겠습니다.

```text
기존 chapter-novelist
→ 초안 작성 전용으로 축소

기존 novel-style-guardian
→ 검수 전용 유지

신규 chapter-prose-reviser
→ 실제 문장 퇴고 전용 추가

기존 continuity-keeper
→ final 이후 검수 유지
```

우선순위는 이렇습니다.

1. **`chapter-prose-reviser` 추가**
2. **`novel-prose-revision` 스킬 추가**
3. **`chapter-novelist`에서 final 작성 책임 제거**
4. **오케스트레이터 체인 변경**
5. **`novel-style-guardian` 리뷰 형식을 퇴고자 전달용으로 변경**
6. **`.codex` 쪽도 같은 구조로 동기화**

한 줄로 정리하면:

> **초안 작성자는 이야기를 밀고, 스타일 가디언은 문제를 찍고, 퇴고자는 문장을 고치게 하세요.**

이렇게 나누면 `있었다/였다` 문제를 훨씬 안정적으로 잡을 수 있습니다. 그리고 무엇보다 좋은 점은, 나중에 결과가 마음에 안 들 때 누구 책임인지 알 수 있습니다. 자동화에서도 책임 소재는 중요합니다. 인간 회사가 남긴 몇 안 되는 유용한 발명품이죠.

[1]: https://raw.githubusercontent.com/silbaram/novel-writer/main/.claude/agents/chapter-novelist.md "raw.githubusercontent.com"
[2]: https://raw.githubusercontent.com/silbaram/novel-writer/main/.claude/agents/novel-style-guardian.md "raw.githubusercontent.com"
[3]: https://raw.githubusercontent.com/silbaram/novel-writer/main/.claude/agents/novel-editor.md "raw.githubusercontent.com"
[4]: https://code.claude.com/docs/ko/sub-agents "사용자 정의 subagent 만들기 - Claude Code Docs"
[5]: https://github.com/silbaram/novel-writer "GitHub - silbaram/novel-writer: Automated book-writing harness · GitHub"
[6]: https://raw.githubusercontent.com/silbaram/novel-writer/main/style-guides/lightnovel-style-guide.md "raw.githubusercontent.com"
