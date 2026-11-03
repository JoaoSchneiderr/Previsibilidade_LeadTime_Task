"""
Etapa 3: engenharia de atributos.
Somente informações disponíveis no momento da criação da task (sem vazamento de dados).
Excluídos por decisão do projeto: Analista de Teste, Story Points - Dev, Tempo gasto,
histórico de status ([CHART] Time in Status), Sprint, Descrição e demais campos sensíveis.
"""
import sys
import numpy as np
import pandas as pd

exec(open('01_tratamento.py', encoding='utf-8').read().split('def main')[0])  # reutiliza parse_data e nomes de colunas

BASE = 'base_tratada.pkl'
RAW = sys.argv[1] if len(sys.argv) > 1 else 'Limber__1__1.csv'
NI = 'não informado'
ORD = {'Lowest': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Highest': 5}

b = pd.read_pickle(BASE).sort_values('Criado_dt').reset_index(drop=True)
X = pd.DataFrame(index=b.index)

# --- categóricos (ausência = categoria própria) ---
X['tipo_item'] = b['Tipo de item']
X['projeto'] = b['Chave do projeto']
X['modulo'] = b[MOD].fillna(NI)
X['complexidade'] = b[CPX].fillna(NI)
X['vertical'] = b[VERT].fillna(NI)
X['origem_bug'] = b[OBUG].fillna(NI)
X['desenvolvedor'] = b['desenvolvedor'].fillna(NI)
X['analista_requisitos'] = b[AREQ].fillna(NI)

# --- ordinais / binários ---
X['prioridade_ord'] = b['Prioridade'].map(ORD).fillna(3)
X['complexidade_ord'] = b[CPX].map(ORD).fillna(0)          # 0 = não informado
X['eh_subtarefa'] = b['Tipo de item'].str.startswith('Subtarefa').astype(int)
X['vinculada_epic'] = (~b['Tipo de item'].str.startswith('Subtarefa') & b['Chave pai'].notna()).astype(int)

# --- título (Resumo) ---
X['titulo_caracteres'] = b['Resumo'].fillna('').str.len()
X['titulo_palavras'] = b['Resumo'].fillna('').str.split().str.len()

# --- calendário da criação ---
X['mes_criacao'] = b['Criado_dt'].dt.month
X['dia_semana_criacao'] = b['Criado_dt'].dt.dayofweek
X['hora_criacao'] = b['Criado_dt'].dt.hour

# --- contexto histórico no momento da criação (usa só eventos anteriores) ---
raw = pd.read_csv(RAW, encoding='utf-8-sig', dtype=str, low_memory=False,
                  usecols=['Chave da item', 'Tipo de item', 'Chave do projeto', 'Resolução', 'Responsável', DEV, 'Criado', 'Resolvido'])
raw = raw[raw['Tipo de item'] != 'Epic'].copy()
raw['c'] = raw['Criado'].map(parse_data)
raw['r'] = raw['Resolvido'].map(parse_data)              # vazio = ainda aberta
raw['dev'] = raw[DEV].fillna(raw['Responsável'])


JANELA = pd.Timedelta(days=90)


def abertas_em(t, sub):
    # tasks abertas no instante t, criadas nos 90 dias anteriores
    # (janela evita contar itens esquecidos abertos há anos e o corte da exportação antes de jul/2024)
    return int(((sub['c'] < t) & (sub['c'] >= t - JANELA) & (sub['r'].isna() | (sub['r'] > t))).sum())


por_dev = {d: g[['c', 'r']] for d, g in raw.groupby('dev')}
por_proj = {p: g[['c', 'r']] for p, g in raw.groupby('Chave do projeto')}
X['carga_dev_abertas'] = [abertas_em(t, por_dev[d]) if d in por_dev else 0 for t, d in zip(b['Criado_dt'], b['desenvolvedor'])]
X['backlog_projeto_abertas'] = [abertas_em(t, por_proj[p]) for t, p in zip(b['Criado_dt'], b['Chave do projeto'])]

# experiência e desempenho passado do desenvolvedor: só tasks da base concluídas ANTES da criação
hist = b[['desenvolvedor', 'Tipo de item', 'Resolvido_efetivo', 'lead_time_horas']]
exp, med_dev, med_tipo = [], [], []
for t, d, tp in zip(b['Criado_dt'], b['desenvolvedor'], b['Tipo de item']):
    passado = hist[hist['Resolvido_efetivo'] < t]
    pd_ = passado[passado['desenvolvedor'] == d]['lead_time_horas']
    pt_ = passado[passado['Tipo de item'] == tp]['lead_time_horas']
    exp.append(len(pd_))
    med_dev.append(pd_.median() if len(pd_) >= 5 else np.nan)
    med_tipo.append(pt_.median() if len(pt_) >= 5 else np.nan)
X['dev_tasks_concluidas_antes'] = exp
X['dev_lead_time_mediano_passado'] = med_dev
X['tipo_lead_time_mediano_passado'] = med_tipo

X['Criado_dt'] = b['Criado_dt']
X['chave'] = b['Chave da item']
X['lead_time_horas'] = b['lead_time_horas']
X.to_pickle('atributos.pkl')
print(X.shape)
print(X.drop(columns=['Criado_dt', 'chave']).describe(include='all').T[['count', 'unique', 'top', 'mean', 'min', 'max']].to_string())
