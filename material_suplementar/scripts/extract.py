import json, re, os, collections, csv

u = json.load(open('eligibility2.json'))

# Extração: categoria (C) e tipo de recusa (T)
#   C: M = análise de mecanismo interno; T = método de treino/intervenção; B = benchmark, métrica ou avaliação; U = estudo com usuários
#   T: E = epistêmica; S = segurança; ES = ambas
EX = {
 'R002': ('B', 'E'), 'R009': ('B', 'E'), 'R011': ('B', 'S'), 'R013': ('B', 'S'), 'R014': ('B', 'S'), 'R015': ('T', 'S'),
 'R016': ('B', 'S'), 'R018': ('B', 'S'), 'R020': ('T', 'S'), 'R021': ('B', 'S'), 'R022': ('T', 'S'), 'R023': ('M', 'S'),
 'R024': ('T', 'ES'), 'R025': ('B', 'ES'), 'R026': ('T', 'E'), 'R027': ('T', 'S'), 'R028': ('M', 'S'), 'R029': ('B', 'S'),
 'R030': ('T', 'E'), 'R031': ('T', 'S'), 'R033': ('T', 'S'), 'R034': ('T', 'S'), 'R037': ('T', 'S'), 'R038': ('U', 'ES'),
 'R040': ('T', 'S'), 'R042': ('M', 'S'), 'R044': ('M', 'ES'), 'R045': ('B', 'S'), 'R047': ('B', 'S'), 'R051': ('B', 'E'),
 'R054': ('M', 'S'), 'R055': ('B', 'E'), 'R056': ('B', 'E'), 'R057': ('B', 'S'), 'R061': ('M', 'S'), 'R063': ('B', 'E'),
 'R064': ('B', 'S'), 'R065': ('B', 'S'), 'R067': ('B', 'S'), 'R068': ('T', 'E'), 'R071': ('B', 'S'), 'R072': ('T', 'S'),
 'R075': ('T', 'E'), 'R076': ('B', 'E'), 'R077': ('T', 'S'), 'R078': ('T', 'S'), 'R079': ('T', 'S'), 'R081': ('M', 'S'),
 'R088': ('M', 'S'), 'R095': ('M', 'S'), 'R097': ('T', 'E'), 'R098': ('T', 'E'), 'R103': ('B', 'S'), 'R105': ('T', 'S'),
 'R108': ('B', 'S'), 'R109': ('T', 'E'), 'R111': ('M', 'S'), 'R114': ('M', 'S'), 'R115': ('T', 'S'), 'R120': ('B', 'S'),
 'R134': ('M', 'S'), 'R138': ('B', 'E'), 'R139': ('T', 'E'), 'R140': ('T', 'S'), 'R142': ('B', 'S'), 'R144': ('T', 'S'),
}
# Q1: revisado por pares (conferência, periódico ou workshop) até a data da avaliação (04/11/2026)
PEER = {'R002', 'R009', 'R011', 'R013', 'R014', 'R015', 'R016', 'R020', 'R025', 'R026', 'R027', 'R028', 'R029', 'R030', 'R031',
        'R033', 'R034', 'R037', 'R038', 'R040', 'R042', 'R044', 'R045', 'R047', 'R051', 'R054', 'R055', 'R056', 'R057', 'R061',
        'R063', 'R065', 'R067', 'R068', 'R072', 'R075', 'R076', 'R077', 'R078', 'R079', 'R081', 'R088', 'R095', 'R098', 'R105',
        'R111', 'R138', 'R139', 'R140', 'R142'}
FAM = {
 'Llama': r'\bl(la)?ma[- ]?\d|\bllama\b', 'Qwen': r'\bqwen', 'Mistral': r'\bmistral|\bmixtral', 'Gemma': r'\bgemma',
 'GPT': r'\bgpt-?(3\.5|4|4o|-4|o)', 'Claude': r'\bclaude', 'Gemini': r'\bgemini', 'DeepSeek': r'\bdeepseek', 'Phi': r'\bphi-?\d',
 'Vicuna': r'\bvicuna', 'Falcon': r'\bfalcon', 'OLMo': r'\bolmo', 'GLM': r'\b(chat)?glm', 'Yi': r'\byi-\d', 'InternLM': r'\binternlm',
}
rows = []
for r in u:
    if r.get('elegibilidade') != 'INCLUIDO':
        continue
    path = f"ft/{r['id']}.txt"
    t = open(path, errors='ignore').read().lower() if os.path.exists(path) else ''
    fams = [f for f, p in FAM.items() if len(re.findall(p, t)) >= 3]
    q1 = 1 if r['id'] in PEER else 0
    q2 = 1 if r.get('code_links') else 0
    q3 = 1 if len(fams) >= 2 else 0
    c, ty = EX[r['id']]
    r.update({'categoria': c, 'tipo': ty, 'Q1': q1, 'Q2': q2, 'Q3': q3, 'familias': fams})
    rows.append(r)

json.dump(u, open('final.json', 'w'), indent=0, ensure_ascii=False)
print('incluídos:', len(rows))
print('categoria:', collections.Counter(r['categoria'] for r in rows))
print('tipo:', collections.Counter(r['tipo'] for r in rows))
print('cat x tipo:', collections.Counter((r['categoria'], r['tipo']) for r in rows))
print('Q1:', sum(r['Q1'] for r in rows), 'Q2:', sum(r['Q2'] for r in rows), 'Q3:', sum(r['Q3'] for r in rows))
print('nota:', collections.Counter(r['Q1'] + r['Q2'] + r['Q3'] for r in rows))
print('ano:', collections.Counter(r['date'][:4] for r in rows))
for r in rows:
    if r['Q3'] == 0:
        print('Q3=0', r['id'], r['title'][:60], r['familias'])
