"""
TCC - Previsão do Lead Time de Tasks de Sprint
Etapa 1: tratamento da 5ª extração do Jira (Limber__1__1.csv) e cálculo do lead time.

Regras:
- Resolução == "Concluídos" e Tipo de item != "Epic"
- Datas no formato Jira (08/set/26 17:08 PM) ou ISO
- Subtarefas:
    * mesmo desenvolvedor do item pai (ou desenvolvedor não identificado) -> incorporada ao pai,
      Resolvido_efetivo do pai = MAX(Resolvido do pai, Resolvido dessas subtarefas)
    * desenvolvedor diferente do item pai -> vira linha própria, atribuída a esse desenvolvedor;
      várias subtarefas do mesmo pai feitas pelo mesmo outro desenvolvedor são agrupadas numa linha:
      lead time = MAX(Resolvido) - MIN(Criado) do grupo
    * subtarefa cujo pai não está na base filtrada -> linha própria
- Desenvolvedor = Campo personalizado (Desenvolvedor); se vazio, Responsável
- Período: tasks criadas a partir de 01/08/2024
- Colunas sensíveis (Descrição, Cliente, Comentários etc.) não são carregadas na base
"""
import re, sys, json
import pandas as pd

SRC = sys.argv[1] if len(sys.argv) > 1 else 'Limber__1__1.csv'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'base_tratada.pkl'
INICIO = pd.Timestamp('2024-08-01')

DEV, MOD, CPX = 'Campo personalizado (Desenvolvedor)', 'Campo personalizado (Módulo)', 'Campo personalizado (Complexidade)'
VERT, AREQ, OBUG = 'Campo personalizado (Vertical)', 'Campo personalizado (Analista de Requisitos)', 'Campo personalizado (Origem Bug)'
CHART = 'Campo personalizado ([CHART] Time in Status)'

MESES = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}


def parse_data(s):
    if not isinstance(s, str) or not s.strip():
        return pd.NaT
    s = s.strip()
    m = re.match(r'(\d{1,2})/(\w{3})/(\d{2}) (\d{1,2}):(\d{2})', s)
    if m:  # formato Jira: hora já em 24h, AM/PM redundante
        d, mo, y, h, mi = m.groups()
        return pd.Timestamp(2000 + int(y), MESES[mo.lower()], int(d), int(h), int(mi))
    m = re.match(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', s)
    if m:  # formato ISO (conversão do Excel)
        return pd.Timestamp(*map(int, m.groups()))
    return pd.NaT


def main():
    st = {}
    raw = pd.read_csv(SRC, encoding='utf-8-sig', dtype=str, low_memory=False)
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
        # herda do pai os atributos de contexto quando a subtarefa não os tem
        for c in [MOD, CPX, VERT, OBUG, AREQ]:
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
    st['antes_periodo'] = int((base['Criado_dt'] < INICIO).sum())
    base = base[base['Criado_dt'] >= INICIO].copy()
    st['final'] = len(base)
    base = base.drop(columns=['dev_pai']).sort_values('Criado_dt', ascending=False).reset_index(drop=True)
    base.to_pickle(OUT)
    json.dump(st, open(OUT.replace('.pkl', '_stats.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(st, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
