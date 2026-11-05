# Material suplementar: Comportamento de Recusa (Abstenção) em LLMs

## Busca

- Busca original: 03/09/2026. As contagens por base não foram preservadas.
- Reexecução: 04/11/2026, com o mesmo recorte (publicações de 01/01/2023 a 03/09/2026).
- Campo: apenas o título.
- String: `("large language model" OR "LLM") AND ("refusal" OR "abstention" OR "over-refusal")`, aceitando plurais (LLMs, refusals, over-refusals).
- Bases:
  - arXiv: API pública (`export.arxiv.org`).
  - ACL Anthology: exportação completa `anthology+abstracts.bib.gz`. Eventos realizados após 03/09/2026 foram descartados (EMNLP 2026, Findings of EMNLP 2026, WMT 2026, GroundLM 2026 e BlackboxNLP 2026).
  - Semantic Scholar: API de busca em lote, com o filtro de título aplicado localmente.
  - Google Scholar, usado na busca original, não foi incluído na reexecução porque não permite exportação reprodutível.

## Fluxo de seleção

| Etapa | Registros |
|---|---|
| Identificados: arXiv 123, ACL Anthology 26, Semantic Scholar 147 | 296 |
| Duplicatas removidas (ID arXiv, DOI ou título normalizado) | −150 |
| Registros únicos | 146 |
| Excluídos na triagem por título e resumo (3 CE3, 8 ataque/detector de jailbreak, 15 recusa não é o objeto) | −26 |
| Verificados no texto completo (local de publicação, código/dados, acesso, retirada) | 120 |
| Excluídos na elegibilidade (43 CI1, 9 CI3 texto não obtido, 2 CE2 retirados) | −54 |
| **Incluídos** | **66** |

## Critérios

- **CI1:** publicação em NeurIPS, ACL (incluindo Findings), ICML, ICLR ou NAACL, ou código/dados abertos com link no artigo.
- **CI2:** recusa ou abstenção do LLM como objeto principal. Excluem-se ataques e detectores de jailbreak, e sistemas em que a abstenção é só um componente de outra tarefa.
- **CI3:** texto integral em inglês acessível.
- **CE1:** alucinação sem modelagem de recusa.
- **CE2:** duplicatas, resumos, tutoriais ou artigos retirados.
- **CE3:** sem validação empírica própria (surveys e revisões).

## Extração e qualidade

- Extraídos do título e do resumo:
- Categoria: mecanismo interno; método de treino ou intervenção; benchmark, métrica ou avaliação; estudo com usuários.
- Tipo de recusa: epistêmica, por segurança ou ambas.
- Qualidade (avaliada após a seleção, sem uso para exclusão; 0 ou 1 cada):
  - **Q1:** revisado por pares (conferência, periódico ou workshop) até 04/11/2026.
  - **Q2:** código ou dados abertos.
  - **Q3:** avaliação com mais de uma família de modelos. Primeira passada automática: família citada ao menos 3 vezes no texto completo.

## Arquivos

- `registros_triagem.csv`: os 146 registros únicos, com bases, link e decisão em cada etapa.
- `estudos_incluidos.csv`: os 66 estudos (S01–S66), com categoria, tipo de recusa, notas Q1–Q3 e link do código ou dos dados.
- `scripts/`: código usado na reexecução. Ordem: `busca.py`, `merge.py`, `screen1.py`, `fulltext.py`, `code_check.py`, `eligibility.py`, `extract.py` e `export.py`.

## Uso de IA generativa

A coleta, a deduplicação e as verificações automáticas (texto completo, links de código, famílias de modelos) foram feitas por scripts. A primeira classificação de triagem, extração e qualidade foi feita com apoio de IA generativa, com a decisão e o motivo registrados para cada registro. Os autores revisaram essa classificação.
