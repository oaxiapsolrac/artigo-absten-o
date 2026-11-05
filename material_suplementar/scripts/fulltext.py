import json, re, subprocess, time, os, sys
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

os.makedirs('ft', exist_ok=True)
u = json.load(open('screen1.json'))
cand = [r for r in u if r['triagem1'] == 'I']
ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}


def curl(url, out=None, timeout=90):
    args = ['curl', '-sL', '--max-time', str(timeout), '-A', 'Mozilla/5.0 (RSL research script)']
    if out:
        args += ['-o', out]
    p = subprocess.run(args + [url], capture_output=True)
    return p.stdout


# 1) metadados arXiv (comentários e journal_ref)
ids = [r['arxiv'] for r in cand if r['arxiv']]
meta = {}
for i in range(0, len(ids), 50):
    chunk = ids[i:i + 50]
    for attempt in range(5):
        data = curl('https://export.arxiv.org/api/query?id_list=' + ','.join(chunk) + '&max_results=60')
        if b'<feed' in data:
            break
        time.sleep(6)
    root = ET.fromstring(data)
    for e in root.findall('a:entry', ns):
        aid = e.find('a:id', ns).text.split('/abs/')[-1]
        aid = re.sub(r'v\d+$', '', aid)
        c = e.find('x:comment', ns)
        j = e.find('x:journal_ref', ns)
        meta[aid] = {'comment': c.text if c is not None else '', 'jref': j.text if j is not None else ''}
    time.sleep(3)


# 2) texto completo e busca por links de código/dados
LINK = re.compile(r'(https?://(?:www\.)?(?:github\.com|gitlab\.com|huggingface\.co|zenodo\.org|osf\.io|figshare\.com)/[^\s"\'<>\)\]\}]+)', re.I)


def get_text(r):
    path = f"ft/{r['id']}.txt"
    if os.path.exists(path) and os.path.getsize(path) > 2000:
        return open(path, errors='ignore').read()
    txt = ''
    if r['arxiv']:
        h = curl(f"https://arxiv.org/html/{r['arxiv']}").decode('utf-8', 'ignore')
        if 'ltx_page_main' in h or len(h) > 50000:
            txt = re.sub(r'<[^>]+>', ' ', h)
            links = re.findall(r'href="(https?://[^"]+)"', h)
            txt += '\n' + '\n'.join(links)
        if len(txt) < 5000:
            curl(f"https://arxiv.org/pdf/{r['arxiv']}", out=f"ft/{r['id']}.pdf")
            subprocess.run(['pdftotext', f"ft/{r['id']}.pdf", path], capture_output=True)
            txt = open(path, errors='ignore').read() if os.path.exists(path) else ''
    elif r.get('url') and 'aclanthology' in r['url']:
        curl(r['url'].rstrip('/') + '.pdf', out=f"ft/{r['id']}.pdf")
        subprocess.run(['pdftotext', f"ft/{r['id']}.pdf", path], capture_output=True)
        txt = open(path, errors='ignore').read() if os.path.exists(path) else ''
    open(path, 'w').write(txt)
    return txt


def work(r):
    try:
        txt = get_text(r)
    except Exception as ex:
        txt = ''
    links = sorted(set(l.rstrip('.,;') for l in LINK.findall(txt)))
    # descarta links genéricos de bibliotecas/modelos de terceiros muito comuns
    own = [l for l in links if not re.search(r'huggingface\.co/(meta-llama|mistralai|Qwen|google|microsoft|openai|lmsys|allenai|tiiuae|deepseek-ai|datasets/(tatsu-lab|openai|truthful_qa|cais|walledai|natolambert))', l, re.I)]
    return r['id'], {'fulltext_chars': len(txt), 'links': own[:8]}


res = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for k, v in ex.map(work, cand):
        res[k] = v
        print(k, v['fulltext_chars'], (v['links'][:2] if v['links'] else '-'), flush=True)

for r in cand:
    r.update(res[r['id']])
    if r['arxiv'] in meta:
        r['arxiv_comment'] = meta[r['arxiv']]['comment']
        r['arxiv_jref'] = meta[r['arxiv']]['jref']
json.dump(u, open('fulltext.json', 'w'), indent=0, ensure_ascii=False)
print('done')
