import json, re, os

u = json.load(open('fulltext.json'))
BOILER = re.compile(r'github\.com/(arXiv|brucemiller|huggingface/(transformers|trl|peft|datasets|accelerate)|vllm-project|openai/(simple-evals|human-eval|tiktoken)|EleutherAI/lm-evaluation-harness|facebookresearch/llama|meta-llama|tatsu-lab|lm-sys|hiyouga|microsoft/DeepSpeed|pytorch|ggerganov|ollama|langchain|tloen|stanford-crfm|google-research/google-research)', re.I)
LINK = re.compile(r'https?://(?:www\.)?(?:github\.com|gitlab\.com|huggingface\.co|zenodo\.org|osf\.io|figshare\.com)/[^\s"\'<>\)\]\}]+', re.I)
CUE = re.compile(r'(our|the) (code|data|dataset|benchmark|implementation|repository)|code (is|and data are|and datasets are|will be) (publicly )?(available|released)|available at|we release|released at|publicly available|open-?source|github', re.I)

for r in u:
    if r['triagem1'] != 'I':
        continue
    path = f"ft/{r['id']}.txt"
    txt = open(path, errors='ignore').read() if os.path.exists(path) else ''
    txt = re.sub(r'\s+', ' ', txt)
    abstract = r.get('abstract') or ''
    found = []
    for m in LINK.finditer(abstract + ' ' + (r.get('arxiv_comment') or '') + ' ' + txt):
        url = m.group(0).rstrip('.,;')
        if BOILER.search(url):
            continue
        # contexto antes do link
        src = abstract + ' ' + (r.get('arxiv_comment') or '') + ' ' + txt
        ctx = src[max(0, m.start() - 250):m.start()]
        if CUE.search(ctx) or m.start() < len(abstract) + len(r.get('arxiv_comment') or '') + 2:
            found.append(url)
    r['code_links'] = sorted(set(found))[:5]
    r['fulltext_ok'] = len(txt) > 5000

json.dump(u, open('fulltext2.json', 'w'), indent=0, ensure_ascii=False)
c = [r for r in u if r['triagem1'] == 'I']
print('com texto completo:', sum(r['fulltext_ok'] for r in c), '/', len(c))
print('com link de código/dados:', sum(1 for r in c if r['code_links']))
for r in c:
    if not r['fulltext_ok']:
        print('SEM TEXTO', r['id'], r['title'][:70], r.get('doi') or r.get('url'))
