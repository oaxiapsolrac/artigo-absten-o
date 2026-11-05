import json, csv, os, re, collections

OUT = os.environ['OUT']
os.makedirs(OUT, exist_ok=True)
u = json.load(open('final.json'))
ax = {x['arxiv']: x for x in json.load(open('arxiv_superset.json'))}
acl = {re.sub(r'[^a-z0-9]', '', x['title'].lower()): x for x in json.load(open('acl_hits.json'))}

MOT1 = {'I': 'Segue para texto completo',
        'E-SEC': 'Excluído (CE3): estudo secundário, sem validação empírica própria',
        'E-ATQ': 'Excluído (CI2): contribuição principal é ataque ou detector de jailbreak',
        'E-APL': 'Excluído (CI2): recusa/abstenção não é o objeto principal do estudo'}
MOT2 = {'INCLUIDO': 'Incluído',
        'E-CI1': 'Excluído (CI1): fora dos eventos listados e sem código/dados abertos',
        'E-TXT': 'Excluído (CI3): texto integral não obtido',
        'E-RET': 'Excluído (CE2): artigo retirado (withdrawn) do arXiv',
        '': ''}
CAT = {'M': 'Mecanismo interno', 'T': 'Método de treino/intervenção', 'B': 'Benchmark/métrica/avaliação', 'U': 'Estudo com usuários'}
TIPO = {'E': 'Epistêmica', 'S': 'Segurança', 'ES': 'Ambas'}


def link(r):
    if r.get('arxiv'):
        return 'https://arxiv.org/abs/' + r['arxiv']
    if r.get('url'):
        return r['url']
    if r.get('doi'):
        return 'https://doi.org/' + r['doi']
    return ''


def authors(r):
    if r.get('arxiv') and r['arxiv'] in ax:
        return '; '.join(ax[r['arxiv']]['authors'])
    k = re.sub(r'[^a-z0-9]', '', r['title'].lower())
    if k in acl:
        return acl[k]['authors'].replace(' and ', '; ')
    return ''


def venue(r):
    vs = [v for v in (r.get('venues') or []) if v and v != 'arXiv.org' and not re.match(r'^\d+ pages', v)]
    return vs[0][:120] if vs else 'arXiv (preprint)'


with open(os.path.join(OUT, 'registros_triagem.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id_registro', 'titulo', 'data', 'bases', 'link', 'triagem_titulo_resumo', 'elegibilidade_texto_completo'])
    for r in u:
        w.writerow([r['id'], r['title'], r['date'], ' + '.join(r['sources']), link(r), MOT1[r['triagem1']], MOT2[r.get('elegibilidade', '')]])

inc = [r for r in u if r.get('elegibilidade') == 'INCLUIDO']
inc.sort(key=lambda r: (r['date'], r['title']))
for k, r in enumerate(inc, 1):
    r['sid'] = f'S{k:02d}'
with open(os.path.join(OUT, 'estudos_incluidos.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id_estudo', 'id_registro', 'titulo', 'autores', 'data', 'publicacao', 'link', 'categoria', 'tipo_de_recusa',
                'Q1_revisado_por_pares', 'Q2_codigo_ou_dados_abertos', 'Q3_mais_de_uma_familia_de_modelos', 'nota_qualidade', 'codigo_dados'])
    for r in inc:
        w.writerow([r['sid'], r['id'], r['title'], authors(r), r['date'], venue(r), link(r), CAT[r['categoria']], TIPO[r['tipo']],
                    r['Q1'], r['Q2'], r['Q3'], r['Q1'] + r['Q2'] + r['Q3'], (r.get('code_links') or [''])[0]])
json.dump(inc, open('included_sid.json', 'w'), indent=0, ensure_ascii=False)

c1 = collections.Counter(r['triagem1'] for r in u)
c2 = collections.Counter(r.get('elegibilidade') for r in u if r['triagem1'] == 'I')
print('triagem1', c1, 'eleg', c2)
print('cat x tipo', collections.Counter((r['categoria'], r['tipo']) for r in inc))
for r in inc:
    print(r['sid'], r['id'], r['categoria'], r['tipo'], r['Q1'] + r['Q2'] + r['Q3'], r['title'][:70])
