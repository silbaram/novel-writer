# Book Writer Project

주제·주요 내용·대상 독자가 주어지면 완성된 EPUB을 산출하는 자동화 하네스가 구축되어 있다. 기술서/논픽션 하네스와 라노벨/소설 하네스 두 가지가 공존한다. 아래 라우팅 규칙에 따라 요청을 분기한다.

---

## 라우팅 규칙

| 요청 유형 | 사용할 스킬 |
|----------|-----------|
| 기술서, 논픽션, 실용서, 에세이형 기술서, SQL/개발/AI/비즈니스 등 비소설 | `book-writing-orchestrator` |
| 라노벨, 소설, 웹소설, 판타지, 로맨스 판타지, 이세계물, 회귀물, 학원물, 시즌제 소설, serialized fiction, fiction EPUB | `lightnovel-writing-orchestrator` |

요청이 어느 쪽인지 불분명하면 사용자에게 짧게 확인한다.

---

## 하네스: 책 저술 자동화 (기술서/논픽션)

**목표:** 주제가 주어지면 리서치 → 저술 계획 → 계획 리뷰 → 챕터 저술(Toby 스타일) → EPUB 빌드까지 자동 수행한다. 저자는 항상 `Toby-AI`로 고정한다.

**트리거:** 기술서·논픽션·실용서 저술 관련 작업 요청 시 `book-writing-orchestrator` 스킬을 사용하라. 특정 Phase만 재실행하거나 챕터 수정 요청도 동일 스킬이 처리한다. 단순 질문(예: "책 저술이 뭐야?")은 직접 응답 가능. **라노벨·소설·웹소설 요청은 이 스킬이 아니라 아래 `lightnovel-writing-orchestrator`가 처리한다.**

**스타일 가이드:** 프로젝트 루트의 `style-guides/toby-book-writing-style.md`가 기술서/논픽션 챕터 저술의 기본 문체 기준이고, `.claude/skills/chapter-writing/references/toby-style-guide.md`가 확장 체크리스트다. 챕터 저술가와 스타일 가디언은 반드시 둘 다 준수한다.

**산출 경로:**
- 중간 산출물: `{book-slug}/`
- 최종 산출물(프로젝트 루트, 같은 폴더에 짝으로 산출):
  - `{책-제목}-v{version}.epub` — 본문 EPUB
  - `{책-제목}-v{version}.md` — 외부 독자용 책 소개 markdown (logline·대상 독자·차례·저자 소개)

---

## 하네스: 라노벨/소설 저술 자동화

**목표:** 소설 아이디어가 주어지면 소재 리서치 → 스토리 바이블 → 시즌 계획 → 챕터 계획 → 챕터 집필 → 문체/연속성 검수 → EPUB 빌드까지 자동 수행한다.

**트리거:** 라노벨, 소설, 웹소설, 판타지, 로맨스 판타지, 이세계물, 회귀물, 학원물, 시즌제 소설, serialized fiction, fiction EPUB 요청 시 `lightnovel-writing-orchestrator` 스킬을 사용하라. 특정 Phase만 재실행하거나 챕터/시즌 수정 요청도 동일 스킬이 처리한다. 단순 질문(예: "소설 쓰는 방법이 뭐야?")은 직접 응답 가능.

**스타일 가이드:** 프로젝트 루트의 `style-guides/lightnovel-style-guide.md`가 모든 챕터 집필의 제약 조건이다. `chapter-novelist`와 `novel-style-guardian`은 반드시 이를 준수한다.

**산출 경로:**
- 중간 산출물: `{novel-slug}/`
  - 시즌별: `{novel-slug}/seasons/sNN/`
- 최종 산출물(프로젝트 루트, 같은 폴더에 짝으로 산출):
  - `{작품-제목}-v{version}.epub` — 본문 EPUB
  - `{작품-제목}-v{version}.md` — 외부 독자용 책 소개 markdown
