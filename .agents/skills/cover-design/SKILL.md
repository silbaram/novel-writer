---
name: cover-design
description: Use to design or generate a 1600x2560 book cover PNG and cover_prompt.md from title, mood, audience, and author metadata.
---

# Cover Design

책의 표지 이미지를 설계·생성한다. 결과는 `{slug}/cover.png` (1600×2560 권장) + 재생성용 프롬프트 기록.

## 절차

1. **입력 확인** — 책 제목, 부제(있으면), 주제 분위기, 대상 독자
   - `{slug}/02_story_bible.md`가 있으면 라노벨/소설 모드로 처리한다
   - `{slug}/02_plan.md`만 있으면 기술서/논픽션 모드로 처리한다
2. **콘셉트 3안 구상**
   - 라노벨/소설: 주인공 중심 캐릭터 일러스트, 핵심 갈등 장면, 세계관 상징
   - 기술서/논픽션: 미니멀리즘, 주제 메타포 이미지, 타이포그래피 중심
3. **추천안 선택** — 주제 톤·대상 독자에 가장 맞는 1안
4. **프롬프트 작성** — 영어 프롬프트 권장 (이미지 모델 대부분 영어 최적화)
5. **이미지 생성** — 사용 가능한 도구 순서로 시도
6. **결과 검증** — 해상도, 구도, 제목 가독성 확인
7. **저장** — `cover.png` + `cover_prompt.md`

## 콘셉트 선택 가이드

| 주제 톤 | 추천 콘셉트 |
|---------|------------|
| 라노벨·웹소설 | 캐릭터 중심 일러스트. 주인공, 핵심 소품, 배경 세계의 무드를 선명하게 드러낸다 |
| 판타지·이세계 | 주인공 + 세계관 상징 + 장르적 조명. 기술서식 미니멀 표지를 적용하지 않는다 |
| 로맨스 판타지 | 인물 관계와 의상·배경 분위기 중심. 과한 비즈니스/전문서적 톤 금지 |
| 차분한 기술서 | A (미니멀리즘, 차분한 색조) |
| 철학·에세이형 | C (타이포그래피, 따뜻한 색) |
| 실전 튜토리얼 | B (일러스트, 선명한 색) |
| 심화·이론서 | A (미니멀, 깊이 있는 색) |

## 프롬프트 작성 원칙

- 스타일 지정: "minimalist book cover", "editorial illustration", "modernist typography"
- 라노벨/소설 모드에서는 "light novel cover illustration", "character-focused", "anime-inspired but original character design", "dramatic fantasy background"처럼 캐릭터와 장르 무드를 우선한다
- 색상 톤: "warm muted palette", "deep blue and gold"
- 분위기: "contemplative", "bold", "serene"
- 구도: "title prominent in upper third, small author attribution at bottom"
- 제외: "no cheesy stock photo aesthetic", "no generic tech gradient"
- 라노벨/소설 제외: "no business book layout", "no generic technical book minimalism", "no essay cover typography-only design"
- 해상도·비율: "portrait orientation, 1.6:1 aspect ratio"

**예시 프롬프트:**
```
A minimalist book cover in portrait format (1600x2560). 
Title "효과적인 SQL 쿼리 튜닝" in bold modern sans-serif 
occupying the top third. Center: a single abstract symbol 
resembling an interconnected graph in deep indigo. 
Background: warm off-white. Bottom-right: "{저자명}" 
in small elegant serif. Editorial, calm, confident. 
No stock photography. No generic tech gradient.
```

## 이미지 생성 도구 우선순위

1. **Codex 이미지 생성 도구/`imagegen` 스킬** (사용 가능하면) — 가장 선호
2. **외부 API** — OpenAI 이미지 생성 API, Stability SDXL 등 (사용자 API 키 필요)
3. **ImageMagick 폴백** — 단순 타이포그래피 플레이스홀더

## ImageMagick 폴백 명령

```bash
convert -size 1600x2560 \
  -gradient '#1a1a2e-#2d1b4e' \
  -gravity center -font 'Apple-SD-Gothic-Neo' -pointsize 120 -fill white \
  -annotate +0-400 "{책 제목}" \
  -pointsize 70 -fill '#c9b8d8' -annotate +0+600 "{부제}" \
  -pointsize 50 -fill white -annotate +0+1000 "{저자명}" \
  {slug}/cover.png
```

폰트가 없으면 `-font Helvetica` 또는 시스템 기본 폰트 사용.

## 검증 체크

- [ ] 해상도 ≥ 1600×2560
- [ ] 썸네일(200×320)로 축소해도 제목 읽힘
- [ ] 저자 표기 존재 (오케스트레이터·매니페스트 저자명 사용. 기술서 기본값은 `Toby-AI`, 라노벨/소설 기본값은 `AI-Author`)
- [ ] 클리셰 회피 (기본 그라데이션, 스톡사진 느낌 없음)

## 프롬프트 기록

`cover_prompt.md`:

```markdown
# Cover Design Log

## Version 1 (YYYY-MM-DD)
- Concept: {A/B/C}
- Tool: {mcp / api / imagemagick}
- Prompt:
  ```
  ...
  ```
- Result: cover.png
- Notes: {성공/조정 필요 부분}

## Version 2 ...
```

## 실패 대응

- 이미지 API 실패 → ImageMagick 폴백
- ImageMagick 미설치 → 오케스트레이터에 `brew install imagemagick` 지시 요청, 임시로 단색 PNG 생성
- 생성 결과가 클리셰이거나 제목이 잘 안 보임 → 프롬프트 구체화 (색상·구도 강화) 후 재시도

## 재생성 시

- 이전 `cover.png`를 `cover_v{N}.png`로 백업
- `cover_prompt.md`에 새 버전 append
- 콘셉트 변경 요청 → 3안부터 다시
