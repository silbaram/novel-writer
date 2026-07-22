---
name: novel-illustration
description: Use to plan and, when tools are available, generate interior illustrations for Korean light novels or web novels, including scene selection, prompts, asset paths, manuscript markers, and EPUB-ready metadata.
---

# Novel Illustration

라노벨/웹소설 본문 중간 삽화를 설계하고 프롬프트와 파일 저장 계약을 만든다. 표지는 `cover-design`이 담당하고, 이 스킬은 챕터 사이 또는 챕터 내부에 들어가는 본문 삽화만 다룬다.

세션에 이미지 생성 도구·스킬 또는 API가 있으면 직접 생성해 약속된 경로에 저장한다. 사용할 수 없거나 생성에 실패하면 프롬프트만 산출하고 외부 생성 계약으로 폴백한다.

## 산출물

- `{slug}/P06_publication/illustrations/illustration_plan.md`
- `{slug}/P06_publication/illustrations/sNN/{CCC}_{scene_slug}_prompt.md`
- `{slug}/P06_publication/illustrations/sNN/{CCC}_{scene_slug}.png` (외부 도구가 저장해야 하는 대상 파일)
- 필요 시 `{slug}/P06_publication/illustrations/style_sheet.md`

## 절차

1. **입력 확인**
   - `P02_bible/02_story_bible.md`, `P02_bible/characters/*.md`, `P02_bible/worldbuilding/*.md`, `P03_planning/sNN/chapter_plan.md`를 읽는다.
   - 챕터 본문이 있으면 `{CCC}_final.md`를 우선하고, 없으면 챕터 플랜 기준으로 후보 장면을 잡는다.
2. **삽화 슬롯 선정**
   - 단권 20챕터 기준 권장: 컬러 프론트피스 1장, 본문 흑백/단색 삽화 6~10장.
   - 장면 기준: 캐릭터 첫 등장, 코믹 오해가 한 컷으로 보이는 순간, 감정 전환점, 클라이맥스.
   - 텍스트만으로 더 강한 장면, 스포일러가 과한 장면, 캐릭터 디자인을 불필요하게 확정하는 장면은 제외한다.
3. **시각 일관성 정의**
   - 주인공/주요 인물 카드의 외형 키워드·의상·금지 요소·반복 소품을 `style_sheet.md`에 정리한다.
   - 기존 canon을 침범하지 않는다. 외형이 [DRAFT]인 항목은 "prompt-only visual proposal"로 표시한다.
4. **프롬프트 작성**
   - 영어 이미지 프롬프트를 기본으로 작성한다.
   - "anime-inspired original light novel interior illustration", "black-and-white manga-style insert", "clean line art", "no copyrighted character resemblance"를 필요에 따라 사용한다.
   - 텍스트 렌더링은 피한다. 표지 외 삽화에는 글자·말풍선·로고를 넣지 않는다.
5. **파일 계약 작성**
   - 각 슬롯마다 저장해야 할 PNG 경로를 확정한다.
   - `_prompt.md`에 권장 도구, 프롬프트, 네거티브 프롬프트, 비율/해상도, 저장 파일명을 기록한다.
   - 상태는 `prompt_ready` / `image_missing` / `generated` / `user_provided` / `excluded` 중 하나만 사용한다.
6. **이미지 생성 또는 폴백**
   - 이미지 생성 수단이 있으면 슬롯 프롬프트와 `style_sheet.md`를 함께 사용해 계약 경로에 PNG를 생성하고 상태를 `generated`로 바꾼다.
   - 사용자가 이미지를 배치하면 `user_provided`, 생성 수단이 없거나 실패하면 `image_missing`, 제외가 확정되면 `excluded`로 기록한다.
7. **원고 삽입 준비**
   - `P05_manuscript/04_manuscript.md` 또는 시즌 원고에 다음 형태의 마커를 넣을 수 있게 기록한다.

```markdown
![삽화 설명](../P06_publication/illustrations/s01/001_guild_registration.png)
```

## 삽화 계획 형식

```markdown
# Interior Illustration Plan

## Style Sheet Summary
- Visual mode:
- Character consistency:
- Negative constraints:

## Slots
| ID | 위치 | 장면 | 목적 | 파일 | 상태 |
|----|------|------|------|------|------|
| s01-001-a | 1화 후반 | 계측기 폭발 직후 길드 등록소 | 세계관 룰 첫인상 | P06_publication/illustrations/s01/001_guild_registration.png | prompt_ready |
```

## 프롬프트 파일 형식

각 슬롯은 같은 basename의 `_prompt.md`를 가진다.

```markdown
# Illustration Prompt — s01-001-a

- Target file: `P06_publication/illustrations/s01/001_guild_registration.png`
- Status: prompt_ready
- Recommended tools: Midjourney / Stable Diffusion / NovelAI / OpenAI image model / other web image tool
- Aspect ratio: 2:3 or 3:4
- Minimum size: 1200px on the long side
- Placement: 1화 후반, 계측기 폭발 장면 직후

## Prompt

English prompt goes here.

## Negative Prompt

no speech bubbles, no readable text, no logos, no copyrighted character resemblance

## Save Contract

Generate or place the final PNG exactly here:

`{slug}/P06_publication/illustrations/s01/001_guild_registration.png`
```

## 검증 체크

- [ ] 각 삽화가 해당 챕터의 실제 장면과 충돌하지 않는다.
- [ ] 스포일러 강도가 해당 삽입 위치보다 앞서가지 않는다.
- [ ] 주요 인물 외형이 캐릭터 카드와 모순되지 않는다.
- [ ] 이미지 파일명은 소문자 영문·숫자·언더스코어만 사용한다.
- [ ] EPUB 상대 경로가 `{slug}/P05_manuscript/04_manuscript.md` 기준으로 맞다.
- [ ] `illustration_plan.md`의 파일 경로와 실제 저장된 PNG 경로가 일치한다.

## 재생성 규칙

- 기존 PNG가 있으면 `{name}_v1.png`로 백업한 뒤 새 파일을 만든다.
- 프롬프트 변경 이력은 같은 `_prompt.md`에 append한다.
- 본문 변경으로 장면이 사라지면 상태를 `excluded`로 바꾸고 파일은 삭제하지 않는다.
