# Novel Writer — 투트랙 저술 자동화 하네스

소설 아이디어 또는 기술서 주제가 주어지면 리서치 → 기획 → 집필 → EPUB 빌드까지 자동 수행하는 에이전트 하네스다. **라노벨/소설**과 **기술서/논픽션** 두 트랙이 독립적으로 공존한다.

---

## 라우팅 규칙

| 요청 유형 | 사용할 스킬 |
|----------|-----------|
| 기술서, 논픽션, 실용서, 에세이형 기술서, SQL/개발/AI/비즈니스 등 비소설 | `book-writing-orchestrator` |
| 라노벨, 소설, 웹소설, 판타지, 로맨스 판타지, 이세계물, 회귀물, 학원물, 시즌제 소설, serialized fiction, fiction EPUB | `lightnovel-writing-orchestrator` |

요청이 어느 쪽인지 불분명하면 사용자에게 짧게 확인한다.

---

## 트랙 A: 기술서/논픽션

**트리거:** 기술서·논픽션·실용서 저술 관련 작업 요청 시 `book-writing-orchestrator` 스킬을 사용하라. 단순 질문(예: "책 저술이 뭐야?")은 직접 응답 가능.

**스타일 가이드:** `style-guides/toby-book-writing-style.md`가 기본 문체 기준이고, `.claude/skills/chapter-writing/references/toby-style-guide.md`가 확장 체크리스트다. `chapter-writer`와 `style-guardian`은 반드시 둘 다 준수한다.

**산출 경로:**
- 중간 산출물: `{book-slug}/`
- 최종 산출물(프로젝트 루트):
  - `{책-제목}-v{version}.epub`
  - `{책-제목}-v{version}.md` — 외부 독자용 책 소개 markdown

---

## 트랙 B: 라노벨/소설

**트리거:** 라노벨, 소설, 웹소설, 판타지, 이세계물, 회귀물 등 픽션 저술 요청 시 `lightnovel-writing-orchestrator` 스킬을 사용하라. 단순 질문(예: "소설 쓰는 방법이 뭐야?")은 직접 응답 가능.

**스타일 가이드:** `style-guides/lightnovel-style-guide.md`가 모든 챕터 집필과 퇴고의 제약 조건이다. 챕터 집필·검수·퇴고 에이전트는 단문을 개그·충격·깨달음 타이밍으로 살리고, 새 장소·인물·사물 묘사는 POV 감각 흐름으로 연결한다.

**산출 경로:**
- 중간 산출물: `{novel-slug}/`, 시즌 설계: `{novel-slug}/P03_planning/sNN/`, 챕터 원고: `{novel-slug}/P04_continuity/sNN/chapters/`
- 최종 산출물(프로젝트 루트):
  - `{작품-제목}-v{version}.epub`
  - `{작품-제목}-v{version}.md` — 외부 독자용 책 소개 markdown
