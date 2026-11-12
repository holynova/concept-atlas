"""Build web derivatives, a curated public index, and delivery archives."""
import argparse
import json
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = ROOT / "output"
QA = ROOT / "qa"

parser = argparse.ArgumentParser()
parser.add_argument("--partial", action="store_true")
args = parser.parse_args()

rows = []
for manifest in sorted((ROOT / "source").glob("manifest-*.json")):
    rows.extend(json.loads(manifest.read_text()))
rows.sort(key=lambda row: int(row["id"]))
ids = [int(row["id"]) for row in rows]
assert ids == list(range(1, 132)), "Expected 131 unique ordered concepts"

curation = json.loads((ROOT / "source/publication.json").read_text())
unpublished_ids = {int(value) for value in curation["unpublishedIds"]}
assert unpublished_ids == {21, 22, 23, 24, 25, 51, 52, 53, 54, 55}
public_rows = [row for row in rows if int(row["id"]) not in unpublished_ids]
assert len(public_rows) == 121

for layer in ("thumbs", "detail"):
    (DIST / "assets" / layer).mkdir(exist_ok=True)
QA.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

missing, assets = [], []
for row in rows:
    for key in ("title", "english", "hook", "summary", "explanation", "pitfall", "sourceTitle", "sourceUrl", "prompt"):
        assert row.get(key), f"Missing {key} for {row['id']}"

    source = DIST / row["image"]
    if int(row["id"]) in unpublished_ids and not source.is_file():
        source = ROOT / "source/archive/unpublished" / Path(row["image"]).name
    if not source.is_file():
        missing.append(int(row["id"]))
        continue

    with Image.open(source) as original:
        original.load()
        width, height = original.size
        assert abs(width / height - 0.75) < 0.003, f"Incorrect aspect ratio: {source.name} {original.size}"
        assert width >= 1000 and height >= 1300, f"Source too small: {source}"
        image = original.convert("RGB")
        basename = f"{int(row['id']):02}-{row['slug']}.webp"
        thumb = DIST / "assets/thumbs" / basename
        detail = DIST / "assets/detail" / basename
        if int(row["id"]) not in unpublished_ids:
            if not thumb.exists() or thumb.stat().st_mtime < source.stat().st_mtime:
                small = image.copy()
                small.thumbnail((600, 800), Image.Resampling.LANCZOS)
                small.save(thumb, "WEBP", quality=86, method=6)
            if not detail.exists() or detail.stat().st_mtime < source.stat().st_mtime:
                image.save(detail, "WEBP", quality=92, method=6)

    row["width"], row["height"] = width, height
    assets.append({
        "id": int(row["id"]),
        "title": row["title"],
        "published": int(row["id"]) not in unpublished_ids,
        "width": width,
        "height": height,
        "originalBytes": source.stat().st_size,
        "thumbnailBytes": thumb.stat().st_size if thumb.is_file() else 0,
        "detailBytes": detail.stat().st_size if detail.is_file() else 0,
    })

public_keys = (
    "id", "slug", "title", "english", "category", "hook", "summary", "explanation", "pitfall",
    "tags", "sourceTitle", "sourceUrl", "image", "width", "height",
)
public_index = [
    {key: row[key] for key in public_keys if key in row}
    for row in public_rows
]
(DIST / "concepts.json").write_text(json.dumps(public_index, ensure_ascii=False, indent=2) + "\n")

if missing and not args.partial:
    raise SystemExit(f"Incomplete collection: missing concepts {missing}")

(QA / "asset-report.json").write_text(json.dumps({
    "allConcepts": len(rows),
    "publishedConcepts": len(public_rows),
    "unpublishedIds": sorted(unpublished_ids),
    "missing": missing,
    "assets": assets,
}, ensure_ascii=False, indent=2) + "\n")

if not missing:
    for obsolete in ("concept-atlas-60.zip", "concept-atlas-new-30.zip"):
        (OUTPUT / obsolete).unlink(missing_ok=True)

    def captions_for(concepts):
        return [
            f"## {int(row['id']):02} {row['title']}\n\n{row['hook']}\n\n{row['explanation']}\n\n"
            f"记住这句：{row['summary']}\n\n再多懂一点：{row['pitfall']}\n\n"
            f"参考来源：[{row['sourceTitle']}]({row['sourceUrl']})\n\n"
            f"#概念探险队 #一图搞懂 #知识漫画 #{row['category']} #{row['title']}\n"
            for row in concepts
        ]

    captions = captions_for(public_rows)
    copy = "# 概念探险队 · 121 张配套图文文案\n\n" + "\n---\n\n".join(captions)
    (OUTPUT / "图文文案.md").write_text(copy)
    (DIST / "captions.md").write_text(copy)
    (OUTPUT / "generation-prompts.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")

    with zipfile.ZipFile(OUTPUT / "concept-atlas-121.zip", "w", compression=zipfile.ZIP_STORED) as bundle:
        for row in public_rows:
            bundle.write(DIST / row["image"], f"{int(row['id']):02}-{row['title']}.png")
        bundle.writestr("图文文案.md", copy)
        bundle.writestr(
            "阅读说明.txt",
            "概念探险队 · 一图搞懂一个概念\n121 张3:4竖版知识漫画，原始PNG。每张一个概念。\n"
            "AI生成插画，示意图不按真实比例；知识边界及来源见配套文案。\n",
        )

    new_rows = [row for row in public_rows if int(row["id"]) >= 61]
    new_captions = captions_for(new_rows)
    with zipfile.ZipFile(OUTPUT / "concept-atlas-new-71.zip", "w", compression=zipfile.ZIP_STORED) as bundle:
        for row in new_rows:
            bundle.write(DIST / row["image"], f"{int(row['id']):02}-{row['title']}.png")
        bundle.writestr("图文文案.md", "\n---\n".join(new_captions))

    sheet = Image.new("RGB", (1200, 27 * 342), "#faf7ef")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(rows):
        poster_path = DIST / row["image"]
        if int(row["id"]) in unpublished_ids:
            poster_path = ROOT / "source/archive/unpublished" / Path(row["image"]).name
        with Image.open(poster_path) as poster:
            tile = ImageOps.contain(poster.convert("RGB"), (216, 288), Image.Resampling.LANCZOS)
            x, y = (index % 5) * 240 + 12, (index // 5) * 342 + 8
            sheet.paste(tile, (x, y))
            suffix = "（已收起）" if int(row["id"]) in unpublished_ids else ""
            draw.text((x, y + 296), f"{int(row['id']):02} / {row['slug']}{suffix}", fill="#17324a")
    sheet.save(QA / "contact-sheet.jpg", quality=90)

print(json.dumps({
    "all": len(assets),
    "published": len(public_rows),
    "unpublished": len(unpublished_ids),
    "missing": missing,
    "bytes": {key: sum(asset[key] for asset in assets) for key in ("originalBytes", "thumbnailBytes", "detailBytes")},
}, ensure_ascii=False))
