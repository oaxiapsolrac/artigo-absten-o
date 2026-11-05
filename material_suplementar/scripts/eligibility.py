import json, re, os, collections

u = json.load(open('fulltext2.json'))
VEN = re.compile(r'NeurIPS|Neural Information Processing Systems|\bICML\b|International Conference on Machine Learning|\bICLR\b|'
                 r'International Conference on Learning Representations|\bNAACL\b|North American Chapter|'
                 r'Annual Meeting of the Association for Computational Linguistics|\bACL ?20\d\d\b|\bACL\b ?(main|findings|\(main|\(findings)|'
                 r'Findings of (the )?ACL|Association for Computational Linguistics: ACL', re.I)
NOT_ACCEPTED = re.compile(r'under review|submitted to|in submission|under submission|preprint|workshop', re.I)
RETRACTED = {'R012', 'R060'}
NO_TEXT = {'R053', 'R058', 'R062', 'R090', 'R112', 'R113', 'R117', 'R137', 'R143'}

for r in u:
    if r['triagem1'] != 'I':
        r['elegibilidade'] = ''
        continue
    if r['id'] == 'R035':
        r['fulltext_ok'] = True
        r['code_links'] = []
    vtxt = ' | '.join([r.get('arxiv_comment') or '', r.get('arxiv_jref') or ''] + (r.get('venues') or []))
    hits = []
    for part in re.split(r'\|', vtxt):
        if VEN.search(part) and not NOT_ACCEPTED.search(part):
            hits.append(part.strip()[:120])
    r['venue_listed'] = hits
    if r['id'] in RETRACTED:
        r['elegibilidade'] = 'E-RET'
    elif r['id'] in NO_TEXT or not r.get('fulltext_ok'):
        r['elegibilidade'] = 'E-TXT'
    elif hits or r.get('code_links'):
        r['elegibilidade'] = 'INCLUIDO'
    else:
        r['elegibilidade'] = 'E-CI1'
json.dump(u, open('eligibility.json', 'w'), indent=0, ensure_ascii=False)
c = [r for r in u if r['triagem1'] == 'I']
print(collections.Counter(r['elegibilidade'] for r in c))
print('--- incluídos por venue (sem código):')
for r in c:
    if r['elegibilidade'] == 'INCLUIDO' and not r.get('code_links'):
        print(r['id'], r['title'][:60], '||', r['venue_listed'][:2])
print('--- E-CI1 (verificar venue):')
for r in c:
    if r['elegibilidade'] == 'E-CI1':
        print(r['id'], r['title'][:60], '||', (r.get('arxiv_comment') or '')[:60], '||', [v[:50] for v in r.get('venues') or []][:2])
