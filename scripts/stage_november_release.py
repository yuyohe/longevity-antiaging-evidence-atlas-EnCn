"""Rebase existing November outputs onto the current remote without regenerating them."""
from __future__ import annotations
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess

import build_november_cards as builder

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'build/private-content/maintenance-2026-11-01'
STAGE = PRIVATE / 'public-staging'


def remote(path, parent):
    return subprocess.check_output(['git', 'show', parent + ':' + path], cwd=ROOT)


def save(path, content):
    target = STAGE / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))


def main():
    parent = subprocess.check_output(['git', 'rev-parse', 'origin/main'], cwd=ROOT).decode().strip()
    expected = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=ROOT).decode().split()[0]
    assert parent == expected, 'Refresh the remote ref before staging'
    previous = json.loads((PRIVATE / 'public_manifest.json').read_text(encoding='utf-8'))
    backup = PRIVATE / 'pre-sync-backup'
    for item in previous:
        source = STAGE / item['path']
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == item['sha256'], item['path']
        target = backup / item['path']
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    metadata = json.loads((STAGE / 'data/maintenance_2026_11/source_metadata.json').read_text(encoding='utf-8'))
    cards = json.loads((STAGE / 'data/maintenance_2026_11/ingredient_cards.json').read_text(encoding='utf-8'))['cards']
    used = {p for c in cards for p in c['sources']}
    corrections = []
    for path in ['data/candidate_sources.csv', 'data/literature_library.csv', 'data/evidence_findings.csv',
                 'data/skin_beauty_findings.csv', 'data/supplement_matrix.csv']:
        base = remote(path, parent)
        corrected = builder.corrections(base, path, corrections)
        save(path, corrected)
        if path in ('data/candidate_sources.csv', 'data/literature_library.csv'):
            save('data/maintenance_2026_11/' + Path(path).stem + '_merged.csv',
                 builder.candidate_merge(corrected, metadata, path))
    ledger = remote('data/sources.json', parent)
    save('data/sources.json', ledger)
    save('data/maintenance_2026_11/source_ledger_merged.json', builder.ledger_merge(ledger, metadata, used))
    for path in ['README.md', 'README.zh-CN.md', 'content/public-reader/start-here.md', 'content/public-reader/index.md']:
        text = remote(path, parent).decode('utf-8')
        link = 'content/cards/ingredients-2026-11/index.md' if path.startswith('README') else '../cards/ingredients-2026-11/index.md'
        addition = '\n\n[抗衰成分推荐｜外用10项、口服10项（2026-11-01）](' + link + ')\n\n'
        if 'ingredients-2026-11' not in text:
            text = text.split('\n', 1)[0] + addition + text.split('\n', 1)[1]
        save(path, text)
    text = remote('CHANGELOG.md', parent).decode('utf-8')
    entry = '\n\n## 2026-11-01\n\n发布外用10项、口服10项成分资料卡、独立editorial-v1规则和11月初有界维护记录。新来源保留为候选，合并目录与10月30日正式快照分开；不自动提升旧库评级。\n'
    if '## 2026-11-01' not in text:
        text = text.split('\n', 1)[0] + entry + text.split('\n', 1)[1]
    save('CHANGELOG.md', text)
    path = 'docs/research-heatmap-2026-10.html'
    text = remote(path, parent).decode('utf-8')
    lead = base64.b64encode((STAGE / 'docs/assets/ingredients-2026-11/00-ingredient-guide.png').read_bytes()).decode('ascii')
    entry = '<section><h2>抗衰成分推荐｜按当前研究证据强度分级</h2><p>外用10项、口服10项。证据等级表示具体结论的把握，高等级也可能对应未见获益。</p><img src="data:image/png;base64,' + lead + '" alt="外用10项、口服10项成分索引" style="display:block;width:100%;max-width:720px;height:auto;margin:20px auto"><p><a href="../content/cards/ingredients-2026-11/index.md">打开20张成分卡</a> · <a href="ingredient-guide-2026-11.html">图文阅读页</a> · <a href="../methodology/ingredient-card-grading-v1.md">本次A–D定义</a></p></section>'
    if 'ingredients-2026-11' not in text:
        assert '<main>' in text
        text = text.replace('<main>', '<main>' + entry, 1)
    save(path, text)
    for path in ['scripts/build_november_cards.py', 'scripts/sync_november_feishu.py', 'scripts/stage_november_release.py', 'tests/test_november_cards.py']:
        save(path, (ROOT / path).read_bytes())
    candidates = builder.load_rows((STAGE / 'data/maintenance_2026_11/candidate_sources_merged.csv').read_bytes())[0]
    baseline_candidates = builder.load_rows(remote('data/candidate_sources.csv', parent))[0]
    sources = json.loads((STAGE / 'data/maintenance_2026_11/source_ledger_merged.json').read_text(encoding='utf-8'))
    summary = {'parent': parent, 'candidate_before': len(baseline_candidates), 'candidate_after': len(candidates),
               'new_candidate_records': len(candidates) - len(baseline_candidates),
               'source_ledger_before': len(json.loads(ledger)), 'source_ledger_after': len(sources),
               'legacy_formal_snapshot_preserved': True, 'existing_field_repairs': corrections,
               'images_regenerated': False, 'research_rerun': False}
    save('data/maintenance_2026_11/integration_summary.json', json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    path = 'docs/november-maintenance-2026-11.md'
    notes = (STAGE / path).read_text(encoding='utf-8')
    if '## 本次发布与正式快照' not in notes:
        notes += f"\n\n## 本次发布与正式快照\n\n本次以远端提交`{parent}`为基线，保留10月30日正式快照与全部历史。本批84条来源中，{summary['new_candidate_records']}条尚未在当前候选目录；补入后的候选合并目录共{len(candidates):,}条。它们不自动成为旧矩阵入选证据。\n\n公开合并目录见`data/maintenance_2026_11/candidate_sources_merged.csv`、`literature_library_merged.csv`及`source_ledger_merged.json`。原飞书候选和来源表按稳定ID增量接收本批元数据；旧正式入选表保持原数量和评级。\n"
    save(path, notes)
    save('data/maintenance_2026_11/published_field_corrections.json', json.dumps(corrections, ensure_ascii=False, indent=2) + '\n')
    files = sorted(p for p in STAGE.rglob('*') if p.is_file())
    manifest = [{'path': p.relative_to(STAGE).as_posix(), 'bytes': p.stat().st_size,
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    assert all(not any(x in r['path'].lower() for x in ('private-content', '.env', 'raw_pdf', 'raw_html', 'checkpoint')) for r in manifest)
    (PRIVATE / 'public_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    (PRIVATE / 'integration_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (PRIVATE / 'publication_parent.json').write_text(json.dumps({'sha': parent}, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
