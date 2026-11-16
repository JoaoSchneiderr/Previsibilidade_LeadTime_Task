"""
Funções compartilhadas pelo pipeline do TCC
(Previsão do Lead Time de Tasks de Sprint por meio de Aprendizado de Máquina).

Reúne em um só lugar:
- caminhos padrão do projeto;
- leitura das datas do Jira;
- tratamento da exportação e cálculo do lead time (regra de subtarefas por desenvolvedor);
- construção dos atributos do modelo.

O treinamento (03_atributos.py) e a consulta sob demanda (05_consulta.py) usam as MESMAS
funções de atributos, o que garante que uma task nova seja descrita exatamente como as
tasks usadas no treino.
"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

# ------------------------------------------------------------------ caminhos
PASTA_PIPELINE = Path(__file__).resolve().parent
RAIZ_PROJETO = PASTA_PIPELINE.parent
CSV_PADRAO = RAIZ_PROJETO / 'data' / 'raw' / 'Limber__1__1.csv'      # exportação do Jira (não versionar)
SAIDAS = PASTA_PIPELINE / 'saidas'                                     # arquivos intermediários (não versionar)
MODELO_PADRAO = PASTA_PIPELINE / 'modelo_final.joblib'                 # modelo treinado (não versionar)

# ------------------------------------------------------------------ colunas do Jira
DEV = 'Campo personalizado (Desenvolvedor)'
MOD = 'Campo personalizado (Módulo)'
CPX = 'Campo personalizado (Complexidade)'
VERT = 'Campo personalizado (Vertical)'
AREQ = 'Campo personalizado (Analista de Requisitos)'
OBUG = 'Campo personalizado (Origem Bug)'
CHART = 'Campo personalizado ([CHART] Time in Status)'

INICIO_PERIODO = pd.Timestamp('2024-08-01')
JANELA_ABERTAS = pd.Timedelta(days=90)
NI = 'não informado'
ORD = {'Lowest': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Highest': 5}
MESES = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
         'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}

CATEGORICOS = ['tipo_item', 'projeto', 'modulo', 'complexidade', 'vertical', 'origem_bug',
               'desenvolvedor', 'analista_requisitos']
NUMERICOS = ['prioridade_ord', 'complexidade_ord', 'eh_subtarefa', 'vinculada_epic', 'titulo_caracteres',
             'titulo_palavras', 'mes_criacao', 'dia_semana_criacao', 'hora_criacao', 'carga_dev_abertas',
             'backlog_projeto_abertas', 'dev_tasks_concluidas_antes', 'dev_lead_time_mediano_passado',
             'tipo_lead_time_mediano_passado']
ATRIBUTOS = CATEGORICOS + NUMERICOS

_COLUNAS_TRATAMENTO = {'Chave da item', 'Resumo', 'Tipo de item', 'Chave do projeto', 'Status', 'Categoria do status',
                       'Prioridade', 'Resolução', 'Responsável', DEV, MOD, CPX, VERT, AREQ, OBUG,
                       'Criado', 'Resolvido', CHART, 'Chave pai'}


# ------------------------------------------------------------------ datas
def parse_data(s):
    """Lê '08/set/26 17:08 PM' (formato Jira; hora já em 24h, AM/PM redundante) ou '2026-09-08 17:08:00'."""
    if not isinstance(s, str) or not s.strip():
        return pd.NaT
    s = s.strip()
    m = re.match(r'(\d{1,2})/(\w{3})/(\d{2}) (\d{1,2}):(\d{2})', s)
    if m:
        d, mo, y, h, mi = m.groups()
        return pd.Timestamp(2000 + int(y), MESES[mo.lower()], int(d), int(h), int(mi))
    m = re.match(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', s)
    if m:
        return pd.Timestamp(*map(int, m.groups()))
    return pd.NaT


def ler_exportacao(src):
    """Lê só as colunas usadas pelo pipeline (as colunas sensíveis, como Descrição, nunca são carregadas)."""
    return pd.read_csv(src, encoding='utf-8-sig', dtype=str, low_memory=False,
                       usecols=lambda c: c in _COLUNAS_TRATAMENTO or c.startswith('Sprint'))


# ------------------------------------------------------------------ tratamento e lead time
def tratar(src, inicio=INICIO_PERIODO):
    """
    Aplica os filtros e a regra de subtarefas e calcula lead_time_horas.
    Devolve (base, estatisticas).

    Regras:
    - Resolução == "Concluídos" e Tipo de item != "Epic";
    - desenvolvedor = Campo personalizado (Desenvolvedor); se vazio, Responsável;
    - subtarefa do mesmo desenvolvedor do pai (ou sem desenvolvedor identificado) -> incorporada ao pai:
      Resolvido_efetivo do pai = MAX(Resolvido do pai, Resolvido dessas subtarefas);
    - subtarefa de outro desenvolvedor -> linha própria, agrupada por (pai, desenvolvedor):
      lead time = MAX(Resolvido) - MIN(Criado) do grupo;
    - subtarefa cujo pai não está na base -> linha própria;
    - tasks criadas a partir de `inicio`.
    """
    st = {}
    raw = ler_exportacao(src)
    st['bruto'] = len(raw)
    df = raw[(raw['Resolução'] == 'Concluídos') & (raw['Tipo de item'] != 'Epic')].copy()
    st['apos_filtro'] = len(df)

    sprint_cols = [c for c in df.columns if c == 'Sprint' or re.match(r'Sprint\.\d+$', c)]
    df['Sprint'] = df[sprint_cols].apply(lambda r: next((v for v in r if pd.notna(v) and str(v).strip()), pd.NA), axis=1)

    keep = ['Chave da item', 'Resumo', 'Tipo de item', 'Chave do projeto', 'Status', 'Categoria do status', 'Prioridade',
            'Resolução', 'Responsável', DEV, MOD, CPX, VERT, AREQ, OBUG, 'Criado', 'Resolvido', CHART, 'Chave pai', 'Sprint']
    df = df[keep].copy()
    df['Criado_dt'] = df['Criado'].map(parse_data)
    df['Resolvido_dt'] = df['Resolvido'].map(parse_data)
    st['datas_invalidas'] = int((df['Criado_dt'].isna() | df['Resolvido_dt'].isna()).sum())
    df = df[df['Criado_dt'].notna() & df['Resolvido_dt'].notna()].copy()
    df['desenvolvedor'] = df[DEV].fillna(df['Responsável'])

    chaves = set(df['Chave da item'])
    eh_sub = df['Tipo de item'].str.startswith('Subtarefa')
    tem_pai = eh_sub & df['Chave pai'].isin(chaves)
    pais = df.set_index('Chave da item')
    df['dev_pai'] = df['Chave pai'].map(pais['desenvolvedor']).where(tem_pai)

    mesmo = tem_pai & ((df['desenvolvedor'] == df['dev_pai']) | df['desenvolvedor'].isna() | df['dev_pai'].isna())
    outro = tem_pai & ~mesmo
    st['subtarefas_total'] = int(eh_sub.sum())
    st['sub_mesmo_dev_incorporadas'] = int((tem_pai & (df['desenvolvedor'] == df['dev_pai'])).sum())
    st['sub_dev_nao_identificado_incorporadas'] = int((mesmo & ~(df['desenvolvedor'] == df['dev_pai'])).sum())
    st['sub_outro_dev'] = int(outro.sum())
    st['sub_orfas'] = int((eh_sub & ~tem_pai).sum())

    # 1) incorporação no pai (mesmo desenvolvedor)
    g = df[mesmo].groupby('Chave pai')
    max_sub, n_sub = g['Resolvido_dt'].max(), g.size()
    df['Resolvido_efetivo'] = df['Resolvido_dt']
    mp = df['Chave da item'].isin(max_sub.index)
    df.loc[mp, 'Resolvido_efetivo'] = pd.concat(
        [df.loc[mp, 'Resolvido_dt'], df.loc[mp, 'Chave da item'].map(max_sub)], axis=1).max(axis=1)
    df['subtarefas_incorporadas'] = df['Chave da item'].map(n_sub).fillna(0).astype(int)
    st['pais_com_incorporacao'] = int(mp.sum())
    st['pais_com_data_estendida'] = int((df.loc[mp, 'Resolvido_efetivo'] > df.loc[mp, 'Resolvido_dt']).sum())

    # 2) subtarefas de outro desenvolvedor: uma linha por (pai, desenvolvedor)
    o = df[outro].sort_values('Criado_dt')
    linhas = []
    for (pai, dev), grp in o.groupby(['Chave pai', 'desenvolvedor'], sort=False):
        r = grp.iloc[0].copy()
        r['Criado_dt'] = grp['Criado_dt'].min()
        r['Resolvido_efetivo'] = grp['Resolvido_dt'].max()
        r['subtarefas_incorporadas'] = len(grp) - 1
        r['chaves_agrupadas'] = ', '.join(grp['Chave da item'])
        for c in [MOD, CPX, VERT, OBUG, AREQ]:          # herda do pai o contexto ausente na subtarefa
            if pd.isna(r[c]):
                r[c] = pais.at[pai, c]
        r['origem_linha'] = 'subtarefa de outro desenvolvedor'
        linhas.append(r)
    outros = pd.DataFrame(linhas)
    st['linhas_outro_dev'] = len(outros)

    base = df[~mesmo & ~outro].copy()
    base['chaves_agrupadas'] = pd.NA
    base['origem_linha'] = 'item'
    base.loc[eh_sub & ~tem_pai, 'origem_linha'] = 'subtarefa sem pai na base'
    base = pd.concat([base, outros], ignore_index=True)
    st['apos_consolidacao'] = len(base)

    base['lead_time_horas'] = (base['Resolvido_efetivo'] - base['Criado_dt']).dt.total_seconds() / 3600
    st['lead_time_negativo'] = int((base['lead_time_horas'] < 0).sum())
    base = base[base['lead_time_horas'] >= 0]
    st['antes_periodo'] = int((base['Criado_dt'] < inicio).sum())
    base = base[base['Criado_dt'] >= inicio].copy()
    st['final'] = len(base)
    base = base.drop(columns=['dev_pai']).sort_values('Criado_dt', ascending=False).reset_index(drop=True)
    return base, st


def historico_bruto(src):
    """Todas as tasks (exceto Epic), abertas ou não, para medir carga e backlog em cada instante."""
    raw = ler_exportacao(src)
    raw = raw[raw['Tipo de item'] != 'Epic'].copy()
    raw['c'] = raw['Criado'].map(parse_data)
    raw['r'] = raw['Resolvido'].map(parse_data)          # vazio = ainda aberta
    raw['dev'] = raw[DEV].fillna(raw['Responsável'])
    return raw


# ------------------------------------------------------------------ atributos
def atributos_da_task(tipo, projeto, prioridade, modulo, complexidade, vertical, origem_bug,
                      desenvolvedor, analista_requisitos, titulo, criado, chave_pai=None):
    """Atributos que vêm só dos campos da própria task (vazio -> "não informado")."""
    vazio = lambda v: v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NA or (isinstance(v, str) and not v.strip())
    titulo = '' if vazio(titulo) else str(titulo)
    eh_sub = str(tipo).startswith('Subtarefa')
    return {
        'tipo_item': tipo,
        'projeto': projeto,
        'modulo': NI if vazio(modulo) else modulo,
        'complexidade': NI if vazio(complexidade) else complexidade,
        'vertical': NI if vazio(vertical) else vertical,
        'origem_bug': NI if vazio(origem_bug) else origem_bug,
        'desenvolvedor': NI if vazio(desenvolvedor) else desenvolvedor,
        'analista_requisitos': NI if vazio(analista_requisitos) else analista_requisitos,
        'prioridade_ord': ORD.get(prioridade, 3),
        'complexidade_ord': 0 if vazio(complexidade) else ORD.get(complexidade, 0),
        'eh_subtarefa': int(eh_sub),
        'vinculada_epic': int((not eh_sub) and not vazio(chave_pai)),
        'titulo_caracteres': len(titulo),
        'titulo_palavras': len(titulo.split()),
        'mes_criacao': criado.month,
        'dia_semana_criacao': criado.dayofweek,
        'hora_criacao': criado.hour,
    }


class Contexto:
    """
    Contexto histórico no instante de criação de uma task. Usa SOMENTE eventos anteriores a esse instante:
    - carga_dev_abertas / backlog_projeto_abertas: tasks abertas no instante, criadas nos 90 dias anteriores
      (a janela evita contar itens esquecidos abertos há anos);
    - dev_tasks_concluidas_antes: tasks da base concluídas pelo desenvolvedor antes do instante (experiência);
    - dev_/tipo_lead_time_mediano_passado: mediana do lead time dessas tasks (mínimo de 5).
    """

    def __init__(self, raw, base):
        self.por_dev = {d: g[['c', 'r']] for d, g in raw.groupby('dev')}
        self.por_proj = {p: g[['c', 'r']] for p, g in raw.groupby('Chave do projeto')}
        self.hist = base[['desenvolvedor', 'Tipo de item', 'Resolvido_efetivo', 'lead_time_horas']]

    @staticmethod
    def _abertas(t, sub):
        return int(((sub['c'] < t) & (sub['c'] >= t - JANELA_ABERTAS) & (sub['r'].isna() | (sub['r'] > t))).sum())

    def calcular(self, criado, desenvolvedor, projeto, tipo):
        dev_raw = desenvolvedor if desenvolvedor != NI else None
        passado = self.hist[self.hist['Resolvido_efetivo'] < criado]
        lt_dev = passado[passado['desenvolvedor'] == dev_raw]['lead_time_horas']
        lt_tipo = passado[passado['Tipo de item'] == tipo]['lead_time_horas']
        return {
            'carga_dev_abertas': self._abertas(criado, self.por_dev[dev_raw]) if dev_raw in self.por_dev else 0,
            'backlog_projeto_abertas': self._abertas(criado, self.por_proj[projeto]) if projeto in self.por_proj else 0,
            'dev_tasks_concluidas_antes': len(lt_dev),
            'dev_lead_time_mediano_passado': lt_dev.median() if len(lt_dev) >= 5 else np.nan,
            'tipo_lead_time_mediano_passado': lt_tipo.median() if len(lt_tipo) >= 5 else np.nan,
        }


def montar_atributos(base, raw):
    """Tabela de atributos de todas as tasks da base (usada no treino)."""
    b = base.sort_values('Criado_dt').reset_index(drop=True)
    ctx = Contexto(raw, b)
    linhas = []
    for _, r in b.iterrows():
        a = atributos_da_task(r['Tipo de item'], r['Chave do projeto'], r['Prioridade'], r[MOD], r[CPX], r[VERT],
                              r[OBUG], r['desenvolvedor'], r[AREQ], r['Resumo'], r['Criado_dt'], r['Chave pai'])
        a.update(ctx.calcular(r['Criado_dt'], a['desenvolvedor'], r['Chave do projeto'], r['Tipo de item']))
        linhas.append(a)
    X = pd.DataFrame(linhas)[ATRIBUTOS]
    X[NUMERICOS] = X[NUMERICOS].astype(float)
    X['Criado_dt'] = b['Criado_dt']
    X['chave'] = b['Chave da item']
    X['lead_time_horas'] = b['lead_time_horas']
    return X
