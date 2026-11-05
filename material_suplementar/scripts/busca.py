"""Reexecução da busca (04/11/2026), recorte 01/01/2023 a 03/09/2026, somente no título.

Gera arxiv_superset.json, arxiv_hits.json, acl.bib.gz, acl_hits.json e s2_raw.json no diretório atual.
Depois, rode merge.py, screen1.py, fulltext.py, code_check.py, eligibility.py, extract.py e export.py.
"""
import gzip, json, re, subprocess, time, urllib.parse
import xml.etree.ElementTree as ET

A = re.compile(r'large language models?|\bLLMs?\b', re.I)          # "large language model" OR "LLM" (com plurais)
B = re.compile(r'refusal|abstention', re.I)                         # "refusal" OR "abstention" OR "over-refusal"
NS = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}


def curl(url):
    return subprocess.run(['curl', '-s', '--max-time', '60', url], capture_output=True).stdout


# 1) arXiv: superconjunto pelos termos de recusa no título; o filtro "LLM" é aplicado localmente
q = ('(ti:refusal OR ti:refusals OR ti:abstention OR ti:abstentions OR ti:abstentionbench OR ti:"over-refusal" '
     'OR ti:"over-refusals" OR ti:overrefusal) AND submittedDate:[202301010000 TO 202609032359]')
out, start = [], 0
while True:
    url = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode(
        {'search_query': q, 'start': start, 'max_results': 200, 'sortBy': 'submittedDate', 'sortOrder': 'ascending'})
    data = None
    for _ in range(5):
        data = curl(url)
        if b'<feed' in data:
            break
        time.sleep(6)
    root = ET.fromstring(data)
    total = int(root.find('{http://a9.com/-/spec/opensearch/1.1/}totalResults').text)
    entries = root.findall('a:entry', NS)
    for e in entries:
        aid = re.sub(r'v\d+$', '', e.find('a:id', NS).text.split('/abs/')[-1])
        c, j = e.find('x:comment', NS), e.find('x:journal_ref', NS)
        out.append({'source': 'arXiv', 'arxiv': aid, 'title': ' '.join(e.find('a:title', NS).text.split()),
                    'abstract': ' '.join(e.find('a:summary', NS).text.split()), 'date': e.find('a:published', NS).text[:10],
                    'comment': c.text if c is not None else '', 'jref': j.text if j is not None else '',
                    'authors': [a.find('a:name', NS).text for a in e.findall('a:author', NS)]})
    start += 200
    if start >= total or not entries:
        break
    time.sleep(3.5)
json.dump(out, open('arxiv_superset.json', 'w'))
json.dump([x for x in out if A.search(x['title']) and B.search(x['title'])], open('arxiv_hits.json', 'w'))

# 2) ACL Anthology: exportação completa; eventos de 2026 posteriores a 03/09/2026 são descartados em merge.py
subprocess.run(['curl', '-sL', '-o', 'acl.bib.gz', 'https://aclanthology.org/anthology+abstracts.bib.gz'])
txt = gzip.open('acl.bib.gz', 'rt', encoding='utf-8', errors='ignore').read()
months = {m: i for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                      'september', 'october', 'november', 'december'], 1)}


def field(e, n):
    m = re.search(r'\b' + n + r'\s*=\s*"(.*?)",?\s*\n', e, re.S) or re.search(r'\b' + n + r'\s*=\s*\{(.*?)\},?\s*\n', e, re.S)
    return ' '.join(m.group(1).replace('{', '').replace('}', '').split()) if m else ''


hits = []
for e in re.split(r'\n@', txt):
    y = re.search(r'\byear\s*=\s*"?\{?(\d{4})', e)
    if not y or not 2023 <= int(y.group(1)) <= 2026:
        continue
    mo = re.search(r'\bmonth\s*=\s*"?\{?([A-Za-z]+)', e)
    mo = months.get(mo.group(1).lower(), 0) if mo else 0
    if int(y.group(1)) == 2026 and mo > 9:
        continue
    ti = field(e, 'title')
    if A.search(ti) and B.search(ti):
        hits.append({'source': 'ACL', 'title': ti, 'year': int(y.group(1)), 'month': mo,
                     'venue': field(e, 'booktitle') or field(e, 'journal'), 'url': field(e, 'url'), 'doi': field(e, 'doi'),
                     'abstract': field(e, 'abstract'), 'authors': field(e, 'author')})
json.dump(hits, open('acl_hits.json', 'w'))

# 3) Semantic Scholar: busca em lote (título + resumo); o filtro de título é aplicado em merge.py
base = 'https://api.semanticscholar.org/graph/v1/paper/search/bulk'
params = {'query': '(refusal | refusals | abstention | "over-refusal") + ("large language model" | "large language models" | LLM | LLMs)',
          'publicationDateOrYear': '2023-01-01:2026-09-03',
          'fields': 'title,year,publicationDate,externalIds,venue,publicationTypes,abstract'}
allp, token = [], None
while True:
    p = dict(params)
    if token:
        p['token'] = token
    d = None
    for attempt in range(8):
        try:
            d = json.loads(curl(base + '?' + urllib.parse.urlencode(p)))
        except Exception:
            d = {}
        if 'data' in d:
            break
        time.sleep(15 + attempt * 10)
    allp += d['data']
    token = d.get('token')
    if not token:
        break
    time.sleep(3)
json.dump(allp, open('s2_raw.json', 'w'))
print('arXiv:', len(json.load(open('arxiv_hits.json'))), '| ACL (antes do corte de eventos):', len(hits), '| S2 bruto:', len(allp))
