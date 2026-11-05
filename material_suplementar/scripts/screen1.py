import json, collections

# Triagem 1 (título e resumo). Códigos:
#   I     = segue para leitura do texto completo
#   E-SEC = estudo secundário (survey/revisão), sem validação empírica própria (CE3)
#   E-ATQ = contribuição principal é um ataque para contornar a recusa ou um detector de jailbreak (CI2 não atendido)
#   E-APL = recusa/abstenção é componente de um sistema de outra tarefa, não objeto de estudo (CI2 não atendido)
D = {}
for i in [3, 107, 119]:
    D[i] = 'E-SEC'
for i in [4, 8, 10, 32, 52, 66, 85, 94]:
    D[i] = 'E-ATQ'
for i in [19, 41, 48, 73, 74, 80, 83, 86, 89, 99, 100, 118, 123, 124, 132]:
    D[i] = 'E-APL'

u = json.load(open('unique.json'))
for r in u:
    n = int(r['id'][1:])
    r['triagem1'] = D.get(n, 'I')
json.dump(u, open('screen1.json', 'w'), indent=0, ensure_ascii=False)
print(collections.Counter(r['triagem1'] for r in u))
