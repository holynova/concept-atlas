"""Create web derivatives and deterministic delivery files; keep PNG originals intact."""
import argparse
import json
import zipfile
from collections import Counter
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
(ROOT / 'qa').mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--partial', action='store_true')
args = parser.parse_args()
rows = []
for manifest in sorted((ROOT / 'source').glob('manifest-*.json')):
    rows.extend(json.loads(manifest.read_text()))
rows.sort(key=lambda row: int(row['id']))
assert [int(row['id']) for row in rows] == list(range(1, 61)), 'Expected 60 unique ordered concepts'
assert sorted(Counter(row['category'] for row in rows).values()) == [10] * 6
for layer in ('thumbs', 'detail'):
    (DIST / 'assets' / layer).mkdir(exist_ok=True)
missing, assets = [], []
for row in rows:
    for key in ('title','english','hook','summary','explanation','pitfall','sourceTitle','sourceUrl','prompt'):
        assert row.get(key), f"Missing {key} for {row['id']}"
    source = DIST / row['image']
    if not source.is_file():
        missing.append(row['id'])
        continue
    with Image.open(source) as image:
        image.load()
        width, height = image.size
        assert abs(width / height - .75) < .003, f'Incorrect aspect ratio: {source.name} {image.size}'
        assert width >= 1000 and height >= 1300, f'Source too small: {source}'
        image = image.convert('RGB')
        thumb = DIST / 'assets/thumbs' / f"{int(row['id']):02}-{row['slug']}.webp"
        detail = DIST / 'assets/detail' / thumb.name
        if not thumb.exists() or thumb.stat().st_mtime < source.stat().st_mtime:
            small = image.copy()
            small.thumbnail((600, 800), Image.Resampling.LANCZOS)
            small.save(thumb, 'WEBP', quality=86, method=6)
        if not detail.exists() or detail.stat().st_mtime < source.stat().st_mtime:
            image.save(detail, 'WEBP', quality=92, method=6)
        row['width'], row['height'] = width, height
        assets.append({'id':row['id'],'title':row['title'],'width':width,'height':height,
                       'originalBytes':source.stat().st_size,'thumbnailBytes':thumb.stat().st_size,'detailBytes':detail.stat().st_size})
public_keys = ('id','slug','title','english','category','hook','summary','explanation','pitfall','tags','sourceTitle','sourceUrl','image','width','height')
public = [{key:row[key] for key in public_keys if key in row} for row in rows]
(DIST / 'concepts.json').write_text(json.dumps(public, ensure_ascii=False, indent=2))
if missing and not args.partial:
    raise SystemExit(f'Incomplete collection: missing concepts {missing}')
(ROOT / 'qa/asset-report.json').write_text(json.dumps({'count':len(assets),'missing':missing,'assets':assets}, ensure_ascii=False, indent=2))
if not missing:
    output = ROOT / 'output'
    output.mkdir(exist_ok=True)
    captions = []
    for row in rows:
        captions.append(f"## {int(row['id']):02} {row['title']}\n\n{row['hook']}\n\n{row['explanation']}\n\n记住这句：{row['summary']}\n\n再多懂一点：{row['pitfall']}\n\n参考来源：[{row['sourceTitle']}]({row['sourceUrl']})\n\n#概念探险队 #一图搞懂 #知识漫画 #{row['category']} #{row['title']}\n")
    copy = '# 概念探险队 · 60张配套图文文案\n\n' + '\n---\n\n'.join(captions)
    (output / '图文文案.md').write_text(copy)
    (DIST / 'captions.md').write_text(copy)
    (output / 'generation-prompts.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(output / 'concept-atlas-60.zip', 'w', compression=zipfile.ZIP_STORED) as bundle:
        for row in rows:
            bundle.write(DIST / row['image'], f"{int(row['id']):02}-{row['title']}.png")
        bundle.writestr('图文文案.md', copy)
        bundle.writestr('阅读说明.txt', '概念探险队 · 一图搞懂一个概念\n60张3:4竖版知识漫画，原始PNG。每张一个概念。\nAI生成插画，示意图不按真实比例；知识边界及来源见配套文案。\n')
    with zipfile.ZipFile(output / 'concept-atlas-new-30.zip', 'w', compression=zipfile.ZIP_STORED) as bundle:
        for row in rows:
            if int(row['id']) >= 31:
                bundle.write(DIST / row['image'], f"{int(row['id']):02}-{row['title']}.png")
        bundle.writestr('图文文案.md', '\n---\n'.join(captions[30:]))
    sheet = Image.new('RGB', (1200, 12 * 342), '#faf7ef')
    draw = ImageDraw.Draw(sheet)
    for index,row in enumerate(rows):
        with Image.open(DIST / row['image']) as poster:
            tile = ImageOps.contain(poster.convert('RGB'), (216,288), Image.Resampling.LANCZOS)
            x, y = (index % 5)*240+12, (index//5)*342+8
            sheet.paste(tile,(x,y))
            draw.text((x,y+296), f"{int(row['id']):02} / {row['slug']}", fill='#17324a')
    sheet.save(ROOT / 'qa/contact-sheet.jpg', quality=90)
print(json.dumps({'ready':len(assets),'missing':missing,'bytes':{key:sum(a[key] for a in assets) for key in ('originalBytes','thumbnailBytes','detailBytes')}}, ensure_ascii=False))
