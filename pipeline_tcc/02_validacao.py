"""
Etapa 2: validação do cálculo do lead time.
Uso:  python pipeline_tcc/02_validacao.py [caminho_da_exportacao.csv]
Recalcula o lead time de todas as linhas a partir do CSV bruto, com uma implementação
independente (Python puro, datetime.strptime), e confere as regras da tabela final.
"""
import csv, sys, json
from datetime import datetime
from collections import defaultdict
import pandas as pd

from comum import CSV_PADRAO, SAIDAS  # só caminhos: o cálculo abaixo é independente do comum.py

SRC = sys.argv[1] if len(sys.argv) > 1 else CSV_PADRAO
BASE = SAIDAS / 'base_tratada.pkl'

MES = {'jan': 'Jan', 'fev': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'mai': 'May', 'jun': 'Jun',
       'jul': 'Jul', 'ago': 'Aug', 'set': 'Sep', 'out': 'Oct', 'nov': 'Nov', 'dez': 'Dec'}


def data(s):
    # "08/set/26 17:08 PM" -> descarta AM/PM (hora já em 24h)
    d, m, resto = s.split('/', 2)
    ano, hora = resto.split(' ')[:2]
    return datetime.strptime(f'{d}/{MES[m]}/{ano} {hora}', '%d/%b/%y %H:%M')


# leitura independente do CSV (cabeçalhos repetidos -> primeira ocorrência)
with open(SRC, encoding='utf-8-sig', newline='') as fh:
    rd = csv.reader(fh)
    head = next(rd)
    idx = {}
    for i, h in enumerate(head):
        idx.setdefault(h, i)
    linhas = [r for r in rd]

col = lambda r, c: r[idx[c]].strip()
it = {}
for r in linhas:
    if col(r, 'Resolução') != 'Concluídos' or col(r, 'Tipo de item') == 'Epic':
        continue
    dev = col(r, 'Campo personalizado (Desenvolvedor)') or col(r, 'Responsável')
    it[col(r, 'Chave da item')] = dict(tipo=col(r, 'Tipo de item'), pai=col(r, 'Chave pai'), dev=dev,
                                       criado=data(col(r, 'Criado')), resolvido=data(col(r, 'Resolvido')))

esperado = {}       # chave da linha -> lead time esperado (h)
filhos_mesmo = defaultdict(list)
grupos_outro = defaultdict(list)
for k, v in it.items():
    if v['tipo'].startswith('Subtarefa') and v['pai'] in it:
        dp = it[v['pai']]['dev']
        if not v['dev'] or not dp or v['dev'] == dp:
            filhos_mesmo[v['pai']].append(v['resolvido'])
        else:
            grupos_outro[(v['pai'], v['dev'])].append(k)
for k, v in it.items():
    if v['tipo'].startswith('Subtarefa') and v['pai'] in it:
        continue
    fim = max([v['resolvido']] + filhos_mesmo.get(k, []))
    esperado[k] = (fim - v['criado']).total_seconds() / 3600
for (pai, dev), ks in grupos_outro.items():
    ks = sorted(ks, key=lambda x: it[x]['criado'])
    ini = min(it[x]['criado'] for x in ks)
    fim = max(it[x]['resolvido'] for x in ks)
    esperado[ks[0]] = (fim - ini).total_seconds() / 3600

# período: pelo Criado da linha (para grupos, o menor Criado = Criado da primeira subtarefa)
esp = {k: h for k, h in esperado.items() if it[k]['criado'] >= datetime(2024, 8, 1)}

b = pd.read_pickle(BASE)
res = []
def chk(nome, ok, detalhe=''):
    res.append((nome, 'OK' if ok else 'FALHA', detalhe))

chk('Mesma quantidade de linhas (recalculo independente x base)', len(esp) == len(b), f'{len(esp)} x {len(b)}')
chk('Mesmo conjunto de chaves', set(esp) == set(b['Chave da item']), '')
dif = (b['Chave da item'].map(esp) - b['lead_time_horas']).abs()
chk('Lead time idêntico ao recálculo independente (tolerância 0,001 h)', bool((dif < 1e-3).all()), f'maior diferença = {dif.max():.6f} h')
f = (b['Resolvido_efetivo'] - b['Criado_dt']).dt.total_seconds() / 3600
chk('lead_time_horas = (Resolvido_efetivo - Criado) / 3600', bool(((f - b['lead_time_horas']).abs() < 1e-9).all()), '')
chk('Nenhum lead time negativo ou vazio', bool((b['lead_time_horas'] >= 0).all() and b['lead_time_horas'].notna().all()), '')
it_rows = b[b['origem_linha'] == 'item']
chk('Resolvido_efetivo >= Resolvido do próprio item', bool((it_rows['Resolvido_efetivo'] >= it_rows['Resolvido_dt']).all()), '')
chk('Chaves únicas na base', b['Chave da item'].is_unique, '')
agr = set(x.strip() for s in b['chaves_agrupadas'].dropna() for x in s.split(','))
inc = {k for k, v in it.items() if v['tipo'].startswith('Subtarefa') and v['pai'] in it} - agr
chk('Subtarefas incorporadas não aparecem como linha própria', not (inc & set(b['Chave da item'])), '')
chk('Nenhuma task criada antes de 01/08/2024', bool((b['Criado_dt'] >= '2024-08-01').all()), '')

checks = pd.DataFrame(res, columns=['Verificação', 'Resultado', 'Detalhe'])

# amostra para conferência manual
amostra = []
for tipo, n in [('item', 4), ('subtarefa de outro desenvolvedor', 3), ('subtarefa sem pai na base', 1)]:
    s = b[b['origem_linha'] == tipo]
    if tipo == 'item':
        s = pd.concat([s[s['Resolvido_efetivo'] > s['Resolvido_dt']].sample(2, random_state=7), s[s['subtarefas_incorporadas'] == 0].sample(2, random_state=7)])
    else:
        s = s.sample(n, random_state=7)
    amostra.append(s)
am = pd.concat(amostra)[['Chave da item', 'origem_linha', 'Criado', 'Resolvido', 'subtarefas_incorporadas', 'chaves_agrupadas', 'Resolvido_efetivo', 'lead_time_horas']].copy()
am['lead_time_horas'] = am['lead_time_horas'].round(2)
am['lead_time_dias'] = (am['lead_time_horas'] / 24).round(1)

lt = b['lead_time_horas']
sanidade = pd.DataFrame([
    ('Tasks com lead time < 1 hora', int((lt < 1).sum())),
    ('Tasks com lead time > 1 ano (8.760 h)', int((lt > 8760).sum())),
    ('Mediana (h)', round(lt.median(), 1)), ('Média (h)', round(lt.mean(), 1)), ('Máximo (h)', round(lt.max(), 1)),
], columns=['Indicador', 'Valor'])

checks.to_pickle(SAIDAS / 'validacao_checks.pkl'); am.to_pickle(SAIDAS / 'validacao_amostra.pkl'); sanidade.to_pickle(SAIDAS / 'validacao_sanidade.pkl')
print(checks.to_string()); print(am.to_string()); print(sanidade.to_string())
