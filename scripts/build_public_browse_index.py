"""Build small GitHub-readable pages from the published full-data snapshot."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REPO = 'https://github.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn'
RAW = 'https://raw.githubusercontent.com/yuyohe/longevity-antiaging-evidence-atlas-EnCn/main'
PAGE_SIZE = 100


def cell(value: str) -> str:
    return re.sub(r'\s+', ' ', str(value)).replace('|', '&#124;').replace('[', '&#91;').replace(']', '&#93;').replace('<', '&lt;').replace('>', '&gt;').replace('`', '&#96;')


def build(output: Path, ref: str | None = None) -> dict:
    def read(path: str) -> bytes:
        if ref:
            return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=ROOT)
        return (ROOT / path).read_bytes()

    def save(path: str, value: str):
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding='utf-8', newline='\n')

    config = json.loads(read('data/current_release.json'))
    month = config['EVIDENCE_ATLAS_ASSET_MONTH']
    date = config['EVIDENCE_ATLAS_UPDATE_DATE']
    specs = [('literature-library', '全量文献目录', 'library_id', 'tblIPdcBJPH6UkAE'),
             ('candidate-sources', '检索来源原始表', 'id', 'tblWoc9k5UIsKq4J'),
             ('shortlist-sources', '优先复核名单', 'candidate_id', 'tblhZtMqsgCxFq0v'),
             ('evidence-findings', '研究笔记（待全文复核）', 'finding_id', 'tblgAIsjA1UR4jLr'),
             ('evidence-matrix', '证据对照表', 'paper_id', 'tblLnS2g439w9pir')]
    datasets = {}
    hashes = {}
    for stem, _, key, _ in specs:
        content = read(f'public-data/{stem}-{month}.csv')
        rows = list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'))))
        assert rows and len({r[key] for r in rows}) == len(rows), stem
        datasets[stem] = rows
        hashes[stem] = hashlib.sha256(content).hexdigest()
    library = datasets['literature-library']
    pmids = {r['pmid'] for r in library if r.get('pmid')}
    sources = dict(sorted(Counter(r.get('source', 'unknown') for r in library).items()))
    counts = {k: len(v) for k, v in datasets.items()}
    library_by_id = {r['library_id']: r for r in library}
    if ref:
        existing = set(subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', ref], cwd=ROOT).decode('utf-8').splitlines())
    else:
        existing = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'content/papers').rglob('*.md')}
    browse_root = f'public-data/browse-{month}'
    for kind in ['literature-library', 'shortlist-sources']:
        rows = datasets[kind]
        selected = kind == 'shortlist-sources'
        label = '优先复核名单' if selected else '全量文献目录'
        pages = (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE
        index = [f'# {label} / '+('Review Shortlist' if selected else 'Full Source Catalog'), '',
                 f'宇多Yul细胞/yulcell · 资料快照 {date} · {len(rows):,} 条记录 · {pages} 页', '',
                 '[全部公开资料](../../../docs/full-library.md) · [完整 CSV]('+RAW+f'/public-data/{kind}-{month}.csv)', '',
                 '目录保留原始题名。入选表示优先复核，草稿等级不能当作功效已经确认。', '',
                 '| 页 / Page | 记录范围 / Rows |', '| --- | ---: |']
        for i in range(pages):
            start, end = i * PAGE_SIZE, min((i + 1) * PAGE_SIZE, len(rows))
            filename = f'{i + 1:03}.md'
            index.append(f'| [第 {i + 1} 页]({filename}) | {start + 1:,}–{end:,} |')
            links = ['[目录](README.md)', '[全部资料](../../../docs/full-library.md)']
            if i:
                links.append(f'[上一页]({i:03}.md)')
            if i + 1 < pages:
                links.append(f'[下一页]({i + 2:03}.md)')
            lines = [f'# {label} · {i + 1}/{pages}', '', ' · '.join(links), '',
                     f'资料快照 {date}。第 {start + 1:,}–{end:,} 条，共 {len(rows):,} 条。', '',
                     '| 序号 | 年份 | 题名 / Original title | 来源 | 状态 | 原文与笔记 |',
                     '| ---: | --- | --- | --- | --- | --- |']
            for n, row in enumerate(rows[start:end], start + 1):
                key = row.get('candidate_id') or row.get('library_id', '')
                source = library_by_id.get(key, row)
                title = row.get('title_zh') or row.get('title_en') or key
                refs = []
                if row.get('pmid'):
                    assert row['pmid'].isdigit()
                    refs.append(f"[PubMed](https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/)")
                if row.get('doi'):
                    refs.append('[DOI](https://doi.org/' + quote(row['doi'], safe='/.:') + ')')
                if not refs and source.get('url', '').startswith('https://'):
                    refs.append('[来源](' + quote(source['url'], safe=':/?=&%') + ')')
                paper = 'content/papers/' + key + '.md'
                if paper in existing:
                    refs.append('[研究笔记](../../../' + paper + ')')
                status = '优先复核' if selected else ('已有研究笔记' if paper in existing else '候选，待复核')
                lines.append('| ' + ' | '.join([str(n), cell(row.get('year', '')), cell(title),
                                              cell(row.get('source') or source.get('source', '')),
                                              status, ' · '.join(refs)]) + ' |')
            lines += ['', ' · '.join(links), '']
            page_text = '\n'.join(lines)
            assert len(page_text.encode('utf-8')) < 200_000
            save(f'{browse_root}/{kind}/{filename}', page_text)
        save(f'{browse_root}/{kind}/README.md', '\n'.join(index) + '\n')
    doc = ['# 全部公开资料 / Full Public Library', '', '宇多Yul细胞/yulcell', '',
           f'资料快照：{date}。这里包含底层文献目录和入选资料，不只展示卡片。', '',
           '## 文献与入选资料 / Sources and Selected Records', '',
           '| 资料 | 记录数 | 在线阅读 | 完整数据 |', '| --- | ---: | --- | --- |']
    for stem, label, _, _ in specs:
        if stem in ('literature-library', 'shortlist-sources'):
            view = f'[分页浏览](../{browse_root}/{stem}/README.md)'
        elif stem == 'evidence-findings':
            view = f'[按文献找研究笔记](../{browse_root}/shortlist-sources/README.md)'
        else:
            view = f'[查看文件](../public-data/{stem}-{month}.csv)'
        doc.append(f'| {label} | {counts[stem]:,} | {view} | [下载 CSV]({RAW}/public-data/{stem}-{month}.csv) |')
    doc += ['', f"文献目录中有 {len(pmids):,} 个不同的 PMID。另有试验注册等来源；候选记录数不等于已确认有效的论文数。五表会重复引用同一文献，不能相加当作论文总数。", '',
            '大 CSV 可能超过 GitHub 的在线预览范围，分页目录和完整下载均保留全部记录。研究笔记保留原草稿状态，本次整理不提升证据等级。', '',
            'The catalog contains source metadata, including trial registrations. The five processing layers overlap. Inclusion and draft grades do not establish efficacy. Large CSV previews may be unavailable; pagination and downloads are complete.', '',
            '## 卡片、图表和方法 / Cards, Charts and Methods', '',
            '- [50种成分卡片](../content/public-reader/ingredient-cards-top-50.md)',
            '- [研究热力图与图例](../content/public-reader/research-heatmap.md)',
            '- [普通读者版：证据权重与筛选标准](../content/public-reader/evidence-weight.md)',
            '- [0.5评分方法](../content/overview/evidence-scoring-v0-5.md) · [分项规则](../data/scoring_policy_v0_4.csv) · [方法学表](../data/methodology_scoring.csv)',
            '- [撤稿解释](../content/public-reader/retractions.md) · [撤稿记录](../data/retracted_publications_20y.csv) · [检索口径](../data/retraction_risk_queries_20y.csv)',
            '- [主题、补剂、护肤与全部当前入口](asset-catalog.md)', '',
            '## 历史版本也公开 / Public Archives', '',
            '- [全部历史五表数据包](../archive/public-data/README.md)',
            '- [2026年6月完整快照：含14,273条候选来源](../archive/public-data/public-data-2026-06.zip)',
            '- [退出当前集合的记录和原因](../data/archive/)',
            '- [历史卡片、热力图与阅读文件](../archive/README.md)', '',
            '历史记录没有删除。当前集合与早期快照的数量不同，退出当前集合不等于论文被撤稿；对应原因保存在退出记录中。', '',
            '## 阅读权限 / Access', '',
            'GitHub资料可免登录阅读和下载，普通访客不能修改主仓库。飞书的文件分享已改为链接只读，但匿名访客仍未能看到当前资料表；修复完成前，请对外分享本页。内部报告、口播脚本和账号密钥不在公开范围内。', '',
            '[项目首页](../README.md) · [完整字段与数据说明](../public-data/README.md)', '']
    save('docs/full-library.md', '\n'.join(doc))
    result = {'snapshot': date, 'asset_month': month, 'source_ref': ref, 'row_counts': counts,
              'unique_pmids': len(pmids), 'source_counts': sources, 'source_sha256': hashes,
              'page_size': PAGE_SIZE, 'status': 'generated_from_published_snapshot'}
    save(f'{browse_root}/manifest.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT)
    parser.add_argument('--ref', default=None)
    args = parser.parse_args()
    print(json.dumps(build(args.output.resolve(), args.ref), ensure_ascii=False, indent=2))
