import json, re, collections, sys

A = re.compile(r'large language models?|\bLLMs?\b', re.I)
B = re.compile(r'refusal|abstention', re.I)


def norm(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())


ax = json.load(open('arxiv_hits.json'))
acl = json.load(open('acl_hits.json'))
s2raw = json.load(open('s2_raw.json'))
late = ('2026 Conference on Empirical Methods', 'EMNLP 2026', 'Eleventh Conference on Machine Translation',
        'GroundLM 2026', '9th BlackboxNLP')
acl_in = [x for x in acl if not any(k in x['venue'] for k in late)]
s2 = [x for x in s2raw if x.get('title') and A.search(x['title']) and B.search(x['title'])]
print('arXiv:', len(ax), '| ACL:', len(acl_in), '| S2:', len(s2), '| soma:', len(ax) + len(acl_in) + len(s2), flush=True)

recs = []
for x in ax:
    recs.append({'src': 'arXiv', 'title': x['title'], 'arxiv': x['arxiv'], 'doi': '',
                 'venue': (x['jref'] or x['comment'] or ''), 'date': x['date'], 'abstract': x['abstract'], 'url': 'https://arxiv.org/abs/' + x['arxiv']})
for x in acl_in:
    recs.append({'src': 'ACL', 'title': x['title'], 'arxiv': '', 'doi': x['doi'], 'venue': x['venue'],
                 'date': str(x['year']), 'abstract': x['abstract'], 'url': x['url']})
for x in s2:
    e = x.get('externalIds') or {}
    recs.append({'src': 'S2', 'title': x['title'], 'arxiv': (e.get('ArXiv') or ''), 'doi': (e.get('DOI') or ''),
                 'venue': x.get('venue') or '', 'date': x.get('publicationDate') or str(x.get('year')),
                 'abstract': x.get('abstract') or '', 'url': ''})

parent = list(range(len(recs)))


def find(i):
    root = i
    while parent[root] != root:
        root = parent[root]
    while parent[i] != root:
        parent[i], i = root, parent[i]
    return root


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra


keys = collections.defaultdict(list)
for i, r in enumerate(recs):
    keys['t:' + norm(r['title'])].append(i)
    if r['arxiv']:
        keys['a:' + r['arxiv'].lower()].append(i)
    d = (r['doi'] or '').lower()
    if d.startswith('10.48550/arxiv.'):
        keys['a:' + d.split('arxiv.')[1]].append(i)
    elif d:
        keys['d:' + d].append(i)
for ids in keys.values():
    for j in ids[1:]:
        union(ids[0], j)

groups = collections.defaultdict(list)
for i in range(len(recs)):
    groups[find(i)].append(i)

uniq = []
for ids in groups.values():
    rs = [recs[i] for i in ids]
    best = max(rs, key=lambda r: len(r['abstract'] or ''))
    uniq.append({'title': best['title'], 'sources': sorted(set(r['src'] for r in rs)),
                 'arxiv': next((r['arxiv'] for r in rs if r['arxiv']), ''),
                 'doi': next((r['doi'] for r in rs if r['doi']), ''),
                 'venues': [r['venue'] for r in rs if r['venue']],
                 'date': min(r['date'] for r in rs), 'abstract': best['abstract'],
                 'url': next((r['url'] for r in rs if r['url']), '')})
uniq.sort(key=lambda r: (r['date'], r['title']))
for k, r in enumerate(uniq, 1):
    r['id'] = f'R{k:03d}'
print('únicos:', len(uniq), '| duplicatas removidas:', len(recs) - len(uniq))
print(collections.Counter(tuple(r['sources']) for r in uniq))
json.dump(uniq, open('unique.json', 'w'), indent=0, ensure_ascii=False)
