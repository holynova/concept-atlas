# 概念探险队 · 60 张一图科普

## Output contract

- One concept per standalone PNG image. Portrait 3:4, request 1200×1600 px or another exact 3:4 resolution.
- Final files: `dist/assets/posters/NN-slug.png`. Never use an SVG or code-rendered illustration as an image-generation substitute.
- All Chinese text must be readable on a phone, use very large dark-ink sans serif Chinese. Keep total prose around 100–150 Chinese characters per poster; diagrams may have a few short labels.
- Safe margins at least 7% on every side. Thin navy outer rectangular frame, no rounded corners.
- Background warm paper ivory #FFF7E7. Main ink #17324A. Flat cobalt #3879B8, muted coral #D85C43, mustard #E8B751, jade #4F8D78. Do not use 3D, watercolor, photorealism, gradients, paper distress or dense hatching.
- Art style explicitly requested by user: The Adventures of Tintin / 丁丁历险记, Hergé-inspired European ligne claire comics: confident clean even-weight ink outlines, flat unshaded color, precise readable spatial diagrams, lightly humorous adventure atmosphere. Use ORIGINAL recurring characters, not actual Tintin characters: young East Asian explorer with short dark hair, mustard-yellow sweater over white shirt, cobalt trousers; optional companion short-haired woman wearing coral jacket.

## Fixed poster structure

1. Small top navy uppercase line: `概念探险队  /  一图搞懂一个概念`.
2. Two-digit issue number plus category in small type.
3. Large dark navy Chinese concept title, max 2 lines.
4. One plain-language hook of 15–28 Chinese characters.
5. Central clear main diagram or 2–3 comic panels explaining exactly this concept, occupying ~55% of the poster.
6. Bottom light mustard summary band, with prefix `记住这句` and a one-sentence accurate takeaway. One short misconception note if needed.
7. Small footer: `CONCEPT ATLAS · NN` (new posters omit a denominator; preserve the original first-series artwork).

## Quality

Make each visual explain a mechanism via position, sequence, direction or causality, beyond a decorative metaphor. Use simple arrows that do not cross and 2–4 word labels. Distinguish an illustrative example from universal rules. Never claim guaranteed investment returns or that a heuristic has no exceptions.

Store exact final generation prompts, readable copy and source links in `source/manifest-XX.json`. Manifest shape is an array of objects: `{id,slug,title,english,category,hook,summary,explanation,pitfall,scene,tags:[...],sourceTitle,sourceUrl,image:"assets/posters/NN-slug.png",prompt}`. Categories in order: 体育运动, 电影摄影, 金融经济, 物理科学, 计算机技术, 心理与生活. All explanations in Chinese, around 80–130 characters. Source links must be real primary sources checked with browsing.
