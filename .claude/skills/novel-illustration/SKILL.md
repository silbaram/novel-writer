---
name: novel-illustration
description: Use to plan interior illustrations for Korean light novels or web novels, including chapter scene selection, external image-generation prompts, required asset paths, manuscript insertion markers, and EPUB-ready illustration metadata.
---

# Novel Illustration

라노벨/웹소설 본문 중간 삽화를 설계하고, 외부 이미지 생성 도구에서 사용할 프롬프트와 파일 저장 계약을 만든다. 표지는 `cover-design`이 담당하고, 이 스킬은 챕터 사이 또는 챕터 내부에 들어가는 본문 삽화만 다룬다.

중요: 이 스킬은 이미지를 직접 생성하지 않는다. OpenAI API, Claude, 웹 LLM, Midjourney, Stable Diffusion, NovelAI 같은 전문 이미지 생성 도구에서 프롬프트를 사용해 이미지를 만든 뒤, 약속된 경로와 파일명으로 저장하면 원고/EPUB에 포함되는 방식이다.

## 산출물

- `{slug}/illustrations/illustration_plan.md`
- `{slug}/illustrations/sNN/{CCC}_{scene_slug}_prompt.md`
- `{slug}/illustrations/sNN/{CCC}_{scene_slug}.png` (외부 도구가 저장해야 하는 대상 파일)
- 필요 시 `{slug}/illustrations/style_sheet.md`

## 절차

1. **입력 확인**
   - `bible/02_story_bible.md`, `bible/characters/*.md`, `bible/worldbuilding/*.md`, `seasons/sNN/chapter_plan.md`를 읽는다.
   - 챕터 본문이 있으면 `{CCC}_final.md`를 우선하고, 없으면 챕터 플랜 기준으로 후보 장면을 잡는다.
2. **삽화 슬롯 선정**
   - 단권 20챕터 기준 권장: 컬러 프론트피스 1장, 본문 흑백/단색 삽화 6~10장.
   - 장면 기준: 캐릭터 첫 등장, 코믹 오해가 한 컷으로 보이는 순간, 감정 전환점, 클라이맥스.
   - 텍스트만으로 더 강한 장면, 스포일러가 과한 장면, 캐릭터 디자인을 불필요하게 확정하는 장면은 제외한다.
3. **시각 일관성 정의**
   - 주인공/주요 인물 외형 키워드, 의상, 금지 요소, 반복 소품을 `style_sheet.md`에 정리한다.
   - 기존 canon을 침범하지 않는다. 외형이 [DRAFT]인 항목은 "prompt-only visual proposal"로 표시한다.
4. **프롬프트 작성**
   - 영어 이미지 프롬프트를 기본으로 작성한다.
   - "anime-inspired original light novel interior illustration", "black-and-white manga-style insert", "clean line art", "no copyrighted character resemblance"를 필요에 따라 사용한다.
   - 텍스트 렌더링은 피한다. 표지 외 삽화에는 글자·말풍선·로고를 넣지 않는다.
5. **파일 계약 작성**
   - 각 슬롯마다 저장해야 할 PNG 경로를 확정한다.
   - `_prompt.md`에 권장 도구, 프롬프트, 네거티브 프롬프트, 비율/해상도, 저장 파일명을 기록한다.
   - 이미지 파일이 아직 없으면 상태를 `prompt_ready` 또는 `image_missing`으로 둔다.
6. **원고 삽입 준비**
   - `manuscript/04_manuscript.md` 또는 시즌 원고에 다음 형태의 마커를 넣을 수 있게 기록한다.

```markdown
![삽화 설명](illustrations/s01/001_guild_registration.png)
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
| s01-001-a | 1화 후반 | 계측기 폭발 직후 길드 등록소 | 세계관 룰 첫인상 | illustrations/s01/001_guild_registration.png | prompt_ready |
```

## 프롬프트 파일 형식

각 슬롯은 같은 basename의 `_prompt.md`를 가진다.

```markdown
# Illustration Prompt — s01-001-a

- Target file: `illustrations/s01/001_guild_registration.png`
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

Generate the image externally and save the final PNG exactly here:

`{slug}/illustrations/s01/001_guild_registration.png`
```

## 검증 체크

- [ ] 각 삽화가 해당 챕터의 실제 장면과 충돌하지 않는다.
- [ ] 스포일러 강도가 해당 삽입 위치보다 앞서가지 않는다.
- [ ] 주요 인물 외형이 캐릭터 카드와 모순되지 않는다.
- [ ] 이미지 파일명은 소문자 영문·숫자·언더스코어만 사용한다.
- [ ] EPUB 상대 경로가 `{slug}/manuscript/04_manuscript.md` 기준으로 맞다.
- [ ] `illustration_plan.md`의 파일 경로와 실제 저장된 PNG 경로가 일치한다.

## 재생성 규칙

- 기존 PNG가 있으면 `{name}_v1.png`로 백업한 뒤 새 파일을 만든다.
- 프롬프트 변경 이력은 같은 `_prompt.md`에 append한다.
- 본문 변경으로 장면이 사라지면 상태를 `deprecated`로 바꾸고 파일은 삭제하지 않는다.
