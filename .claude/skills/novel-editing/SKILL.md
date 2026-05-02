---
name: novel-editing
description: Use to integrate finalized fiction chapters into season/full manuscripts and EPUB-ready 04_manuscript.md plus book_manifest.json.
---

# Novel Editing

라이트노벨/웹소설의 챕터 최종본을 시즌 원고와 전체 EPUB 원고로 통합하는 절차 가이드다. `novel-editor`가 이 스킬을 참조한다.

> **호환성 원칙:** 이 스킬의 최종 산출물(`{slug}/04_manuscript.md` + `{slug}/book_manifest.json`)은 기술서 하네스와 **동일한** `epub-builder` → `epub-build/scripts/build_epub.sh` 파이프라인으로 처리된다. 포맷 호환성을 항상 유지한다.

---

## 편집 전 준비

다음 파일을 모두 확인한 뒤 작업을 시작한다.

| 파일 | 확인 내용 |
|------|----------|
| `{slug}/seasons/sNN/chapters/{CCC}_final.md` (전체) | 모든 챕터 최종본이 존재하는지 확인 |
| `{slug}/continuity/continuity_log.md` | 미해결 Critical 경고가 있는지 확인 |
| `{slug}/continuity/character_state_table.md` | 최신 인물 상태 확인 |
| `{slug}/continuity/foreshadowing_tracker.md` | 미회수 복선은 내부 트래커용으로만 유지하고, 독자 노출 대상이 아님을 확인 |
| `{slug}/02_story_bible.md` | 작품 제목 후보, 저자, 언어 확인 |
| `{slug}/seasons/sNN/season_bible.md` (전체 시즌) | 시즌 제목, 시즌 역할 확인 |

---

## 절차 1 — 챕터 수집 및 저자 노트 제거

1. 각 시즌의 `{CCC}_final.md`를 챕터 번호 순서대로 수집한다
2. 각 파일에서 `<!-- author-note -->` 태그부터 파일 끝까지를 제거한다 — 저자 노트는 독자에게 노출되지 않는 내부 메타데이터다
3. 저자 노트를 제거한 본문만 남긴다

**주의:** 저자 노트 제거는 원본 `_final.md`를 수정하지 않는다. 통합 원고를 생성할 때 메모리상에서 제거하거나 별도 임시 파일을 사용한다.

---

## 절차 2 — 챕터 간 전환부 점검

시즌 내 챕터를 순서대로 읽으며 다음을 점검한다.

**전환 품질 체크리스트:**
- [ ] 이전 챕터의 마지막 감정 상태와 다음 챕터의 첫 감정 상태가 자연스럽게 이어지는가?
- [ ] 시간 경과 표지 ("며칠 뒤", "그날 밤")가 챕터 초반에 명시되어 있는가?
- [ ] 직전 챕터의 훅이 다음 챕터에서 회수되거나 긴장이 유지되는가?

수정이 필요한 경우 `{slug}/editor_notes.md`에 전환부 수정 제안을 기록하고 결과에 명시한다. 오케스트레이터가 이를 읽어 해당 `chapter-novelist`를 재호출한다. 에디터가 직접 본문을 재서술하지 않는다.

---

## 절차 3 — 용어 일관성 확인

시즌 전체를 읽으며 동일 개념을 지칭하는 다양한 표기를 찾는다.

**흔한 불일치 유형:**
- 능력/기술 이름 (예: `마나` vs `마력` vs `에너지`)
- 지명 (예: `왕성` vs `왕궁` vs `성`)
- 인물 호칭 (예: `길드마스터` vs `마스터` vs `길드장`)
- 세력 명칭 (예: `제국` vs `황국` vs `제국군`)

**처리 원칙:**
- 결정 가능한 경우: 더 자주 쓰인 표기로 통일
- 결정 불가능한 경우: 서문에 "이 작품에서는 {개념}을 {표기}로 쓴다" 정의 삽입
- 변경 내용은 `{slug}/editor_notes.md`에 기록

**내용 변경 금지:** 용어 표기 통일 외에 문장 재서술이나 플롯 수정을 하지 않는다. 구조·내용 수정 제안은 `editor_notes.md`에 메모만 한다.

---

## 절차 4 — 시즌 원고 생성

각 시즌마다 `{slug}/seasons/sNN/season_manuscript.md`를 생성한다.

```markdown
# {시즌 제목}
## 시즌 {N}

{001화 본문 (저자 노트 제거됨)}

---

{002화 본문}

...

{마지막 챕터 본문}
```

챕터 사이 구분자: `---` (pandoc이 인식하는 수평선)

---

## 절차 5 — 전체 통합 원고 생성 (`04_manuscript.md`)

`epub-builder`가 직접 소비하는 파일이다. 기술서 하네스의 `04_manuscript.md`와 동일한 최상위 구조를 따른다.

```markdown
# {작품 제목}

## 저자
{author}

## 서문
{독자 초대장 — 이 작품이 무엇인지, 어떤 여정이 펼쳐지는지를 스포일러 없이 소개.
소설이므로 기술적 내용 요약이 아닌 분위기·감정 초대로 작성한다.}

## 목차
{시즌별·챕터별 목록}

---

# 시즌 1. {시즌 1 제목}

{시즌 1 챕터 본문 전체}

---

# 시즌 2. {시즌 2 제목}

{시즌 2 챕터 본문 전체}

...

## 작가 후기
{시리즈 완결 또는 이번 시즌을 마치며. 인물과 세계에 대한 애정을 담은 짧은 글.
필요 시 다음 시즌에 대한 힌트를 조심스럽게 남길 수 있으나, 내부 복선 추적 내역을 직접 노출하지 않는다.}
```

**서문 작성 원칙:**
- 독자가 아직 책을 펴지 않은 상태를 가정한다
- 세계관·플롯 설명이 아닌 분위기·감정으로 초대한다
- 스포일러를 포함하지 않는다

**단권 소설의 경우:** 시즌 구분 헤딩 없이 챕터 본문을 바로 이어 쓴다.

---

## 절차 6 — `book_manifest.json` 생성

`build_epub.sh`가 직접 파싱하는 메타데이터 파일이다.

### 필수 필드 (build_epub.sh 호환 — 빠지면 빌드 실패)

| 필드 | 내용 | 주의 |
|------|------|------|
| `title` | 확정된 작품 제목 | 비어 있으면 슬러그로 대체 |
| `subtitle` | 부제 (없으면 빈 문자열) | |
| `author` | 저자명 (기본값 `AI-Author`) | Phase 0 지정값 우선 |
| `language` | `"ko"` | 고정 |
| `pub_date` | `"YYYY-MM-DD"` | 생성일 기준 |
| `identifier` | `"urn:uuid:{UUID}"` | 재빌드 시 동일 UUID 유지 |
| `description` | 한 문단 소개 | 책 소개 markdown과 연동 |
| `cover_image` | `"cover.png"` | 고정 경로 |
| `version` | `"1.0.0"` | 재빌드 시 증가 |

### 선택 필드 (소설 전용 — build_epub.sh는 무시, 호환성 영향 없음)

```json
{
  "genre": "이세계 판타지",
  "series": {
    "name": "시리즈 이름",
    "volume": 1,
    "total_volumes_planned": 3
  },
  "structure": {
    "type": "light_novel",
    "season_count": 1,
    "chapter_count": 20
  }
}
```

### 완전한 `book_manifest.json` 예시

```json
{
  "title": "시스템 로그를 읽는 자",
  "subtitle": "이세계에서 버그를 고치는 개발자",
  "author": "상진",
  "language": "ko",
  "pub_date": "2026-04-29",
  "identifier": "urn:uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "description": "현실의 서버 개발자였던 주인공이 이세계에 이전되어 마법 시스템의 버그를 수정하는 이야기.",
  "cover_image": "cover.png",
  "version": "1.0.0",
  "genre": "이세계 판타지",
  "series": {
    "name": "시스템 로그를 읽는 자",
    "volume": 1,
    "total_volumes_planned": 3
  },
  "structure": {
    "type": "light_novel",
    "season_count": 1,
    "chapter_count": 20
  }
}
```

---

## 절차 7 — 최종 연속성 확인

`novel-editor`가 통합 원고를 생성한 뒤 `continuity-keeper`의 최종 요약을 참조해 다음을 확인한다.

- `continuity_log.md`에 미해결 Critical 경고가 없는지 확인
- `foreshadowing_tracker.md`에서 이번 시즌 회수 예정 복선이 모두 `회수 완료`인지 확인
- Critical 미해결 항목이 있으면 `season_manuscript.md`와 `04_manuscript.md` **초안 생성은 허용**한다
- 같은 경우 `build_log.md`에 경고를 명시하고 오케스트레이터에 **수동 확인 또는 수정 완료 확인**을 요청한다
- **최종 EPUB 빌드(Phase 9)는 금지**하며, Critical 해소 또는 사용자 수동 승인 전에는 `epub-builder`를 호출하지 않는다

---

## 에러 처리

| 상황 | 처리 |
|------|------|
| 챕터 `_final.md`가 누락됨 | `[미완성 — {CCC}화]` 플레이스홀더 삽입, 오케스트레이터에 보고. EPUB 빌드 보류 |
| 용어 충돌 결정 불가 | 서문에 용어 정의 삽입 |
| `identifier`가 비어 있음 | Python `uuid.uuid4()`로 새 UUID 생성 |
| `title`이 비어 있음 | 슬러그를 사용하고 경고 기록 |
| `version`이 비어 있음 | `"1.0.0"` 기본값 적용 |
| `author`가 비어 있음 | `"AI-Author"` 기본값 적용 |

---

## 재빌드 규칙

| 요청 | 처리 |
|------|------|
| 일부 챕터 갱신 | 해당 챕터 섹션만 교체, 시즌 원고 동기화, `04_manuscript.md` 전체 재저장 |
| 서문·작가 후기 수정 | 해당 섹션만 수정 |
| 버전 업 | `book_manifest.json`의 `version` 증가 (패치: `1.0.1`, 마이너: `1.1.0`) |
| 기존 EPUB 보존 | `build_epub.sh`가 자동으로 `_prev/`에 이동 처리 |
