---
name: novel-prose-revision
description: Use to revise Korean light novel prose after a style review, focusing on sentence rhythm, POV sensory flow, description continuity, and readability without changing plot or canon.
---

# Novel Prose Revision

라이트노벨/웹소설 초안을 스타일 리뷰 이후 실제 문장 단위로 퇴고하는 절차 가이드다. `chapter-prose-reviser`가 이 스킬을 참조한다.

---

## 입력 원칙

퇴고자는 새 이야기를 쓰지 않는다. 아래 파일을 읽고, 초안의 사건·감정·복선·훅을 보존한 상태에서 문장 흐름만 다듬는다.

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

## 퇴고 순서

### 단계 1 — 보존 대상 표시

먼저 초안과 저자 노트에서 바꾸면 안 되는 요소를 확인한다.

- 챕터 목표
- 사건 순서
- 감정 변화
- 대사 의도
- 복선 위치와 의미
- 엔딩 훅
- Canon 상태
- 의도된 단문 타이밍

`### 퇴고 주의 지점`에 적힌 단문, 개그 타이밍, 복선 문장, 바꾸면 안 되는 대사는 원칙적으로 유지한다.

### 단계 2 — 리뷰 지시 분해

`{CCC}_review.md`의 Critical과 Should를 우선 반영한다. Nice는 문체를 해치지 않고 자연스럽게 들어갈 때만 반영한다.

각 지적은 아래처럼 해석한다.

- 문제 유형: 상태문 나열, 위치 주어 반복, 감각 체크리스트, POV Voice 이탈, 대사 리듬 문제
- 보존 의도: 개그, 충격, 복선, 훅, 캐릭터 어조
- 퇴고 방향: 문장을 늘리는 것이 아니라 POV 몸·시선·판단으로 연결하는 것

### 단계 3 — 딱딱한 묘사 문단 탐지

다음 패턴이 있는 문단을 우선 수정한다.

- `있었다/였다/했다/났다` 계열 종결이 3회 이상 반복된다.
- `바닥은`, `앞쪽에서는`, `머리 위에는`, `창구 너머에는`, `벽에는`, `그 안에서`처럼 위치/사물 주어가 3회 이상 바뀐다.
- 냄새, 소리, 빛, 촉감, 온도 같은 감각 정보가 목록처럼 제출된다.
- `~고`, `~며`, `~자`로 이어 붙였지만 각 절의 중심이 계속 사물/공간이다.
- 새 인물 묘사가 외형 항목 나열로만 구성된다.
- 문단 안에 POV 인물의 몸동작, 기억, 판단, 농담, 불편함이 없다.

### 단계 4 — 정보 단문을 POV 인식 흐름으로 변환

상태 설명을 시점 인물의 인식과 움직임으로 바꾼다.

```text
A가 있었다 → A가 코끝에 닿았다 / 손바닥에 걸렸다 / 시야에 들어왔다
B는 C였다 → B를 본 순간 C라는 생각이 들었다
D가 달려 있었다 → D가 움직임에 맞춰 흔들렸다
```

새 장소는 가능하면 아래 흐름으로 묶는다.

```text
코끝 → 발밑/손 → 귀 → 시선 → 기억/농담/불편함
```

새 인물은 아래 흐름으로 묶는다.

```text
행동 → 외형 일부 → 태도/시선 → POV 판단
```

핵심 사물은 아래 흐름으로 묶는다.

```text
접촉/시선 → 질감/무게/소리 → 기능 → POV 반응
```

### 단계 5 — 작품 고유 화자 유지

`voice_profile.md`가 있으면 묘사 문단의 마지막 반응과 1인칭 내레이션에 반영한다. 외부 사건 설명만 길어지고 화자 고유의 해석이 사라지면 실패다.

도윤형 화자처럼 회사·행정·민원·결재·야근 비유가 프로필에 정의되어 있다면, 비상식적 사건을 감각만으로 닫지 말고 실무자식 판단이나 건조한 농담으로 닫는다.

### 단계 6 — 단문 보존 검사

아래 단문은 유지한다.

- 개그 타이밍
- 충격
- 당황한 인식
- 깨달음
- 대사 핑퐁
- 효과음의 결정적 박자

아래 단문은 수정한다.

- 배경 정보 나열
- 외형 항목 나열
- 사물 배치 설명
- 기능 설명만 하는 문장

### 단계 7 — 변경 안전 검사

퇴고 후 아래가 초안과 달라지지 않았는지 확인한다.

- 사건 순서
- 대사 의미
- 캐릭터 감정 결론
- 복선 위치
- 엔딩 훅
- Canon 상태
- 챕터 플랜의 필수 사건

---

## 출력 원칙

### 1차 퇴고

1차 스타일 리뷰(`{CCC}_review.md`)를 반영해 아래 파일을 작성한다.

- `{slug}/P04_continuity/sNN/chapters/{CCC}_revised.md`

저자 노트는 유지하고, 끝에 `### 퇴고 요약`을 추가한다.

```markdown
### 퇴고 요약
- 수정한 주요 문체 문제:
- 유지한 단문 타이밍:
- 보존한 사건/복선:
- Canon 변경 여부: 없음
- 재검수 필요 지점:
```

### 최종화

2차 스타일 리뷰(`{CCC}_review2.md`) 이후 오케스트레이터가 최종화를 요청하면 아래 규칙을 따른다.

- Critical/Should가 없으면 `{CCC}_revised.md`를 내용 변경 없이 `{CCC}_final.md`로 저장한다.
- Critical/Should가 있으면 해당 지적만 최소 수정하고 `{CCC}_final.md`로 저장한다.
- 해결하지 못한 지점은 `P00_meta/logs/style_log.md`에 남기도록 오케스트레이터에 보고한다.
- `{CCC}_final.md`에도 저자 노트는 유지한다. `continuity-keeper`와 `novel-editor`가 참조한다.

---

## 금지

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
