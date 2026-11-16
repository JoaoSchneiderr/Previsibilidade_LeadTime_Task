"""
Etapa 5: consulta sob demanda — estima o lead time de uma task nova.

O gerente informa os campos conhecidos na criação da task. O script calcula o contexto do
desenvolvedor (experiência, carga atual e histórico) a partir da exportação do Jira mais recente
e aplica o modelo treinado (pipeline_tcc/modelo_final.joblib).

Exemplos (a partir da pasta do projeto):

  # uma task, um desenvolvedor
  python pipeline_tcc/05_consulta.py --tipo Bug --projeto ERP --prioridade High --vertical Agro \
      --modulo Financeiro --desenvolvedor "Nome do Dev" --titulo "Erro ao emitir boleto"

  # mesma task simulada com vários desenvolvedores (apoio à alocação)
  python pipeline_tcc/05_consulta.py --tipo Melhoria --projeto CARD --prioridade Medium \
      --desenvolvedor "Dev A" "Dev B" "Dev C" --titulo "Novo filtro no relatório de vendas"

  # várias tasks de um arquivo CSV (colunas iguais aos nomes dos parâmetros, ver exemplos/)
  python pipeline_tcc/05_consulta.py --arquivo pipeline_tcc/exemplos/tasks_exemplo_MOCK.csv --saida previsoes.csv

  # valores conhecidos pelo modelo para cada campo
  python pipeline_tcc/05_consulta.py --listar-valores

A exportação do Jira deve ser a mais recente possível: os atributos de contexto dependem
das tasks abertas e concluídas até a data de criação informada.
"""
import argparse
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))  # permite rodar de qualquer pasta
from comum import (ATRIBUTOS, CATEGORICOS, CSV_PADRAO, MODELO_PADRAO, NI, ORD, Contexto,  # noqa: E402
                   atributos_da_task, historico_bruto, tratar)

warnings.filterwarnings('ignore')
CAMPOS_CSV = ['tipo', 'projeto', 'prioridade', 'modulo', 'complexidade', 'vertical', 'origem_bug',
              'desenvolvedor', 'analista_requisitos', 'titulo', 'data_criacao', 'chave_pai']
DIAS_HISTORICO_DESATUALIZADO = 7


def carregar_modelo(caminho):
    pacote = joblib.load(caminho)
    valores = {}
    try:  # categorias vistas no treino (codificação one-hot)
        prep = pacote['modelo'].regressor_.named_steps['prep']
        enc = prep.named_transformers_['cat']
        for nome, cats in zip(pacote['categoricos'], enc.categories_):
            valores[nome] = sorted(map(str, cats))
    except (KeyError, AttributeError):
        pass
    pacote['valores_conhecidos'] = valores
    return pacote


def preparar_historico(csv):
    base, _ = tratar(csv)
    raw = historico_bruto(csv)
    fim = raw['c'].max()
    return Contexto(raw, base), fim


def montar_linha(task, ctx):
    criado = task['data_criacao']
    a = atributos_da_task(task.get('tipo'), task.get('projeto'), task.get('prioridade'), task.get('modulo'),
                          task.get('complexidade'), task.get('vertical'), task.get('origem_bug'),
                          task.get('desenvolvedor'), task.get('analista_requisitos'), task.get('titulo'),
                          criado, task.get('chave_pai'))
    a.update(ctx.calcular(criado, a['desenvolvedor'], task.get('projeto'), task.get('tipo')))
    return a


def avisos_de_valores(linha, conhecidos):
    avisos = []
    for campo in CATEGORICOS:
        v = str(linha[campo])
        if conhecidos.get(campo) and v not in conhecidos[campo]:
            avisos.append(f'{campo} = "{v}" não aparece (ou é raro) no treino; será tratado como categoria rara')
    return avisos


def prever(pacote, linhas):
    X = pd.DataFrame(linhas)[ATRIBUTOS]
    X[pacote['numericos']] = X[pacote['numericos']].astype(float)
    return np.clip(pacote['modelo'].predict(X), 0, None)


def ler_data(texto):
    if texto is None or (isinstance(texto, float) and np.isnan(texto)) or str(texto).strip() == '':
        return None
    return pd.Timestamp(texto)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Estimativa do lead time de uma task nova (TCC — Previsão do Lead Time).')
    ap.add_argument('--tipo', help='Tipo de item: Bug, Melhoria, Novas Funcionalidades, Tarefa, Subtarefa, Subtarefa - Bug')
    ap.add_argument('--projeto', help='Chave do projeto: ERP ou CARD')
    ap.add_argument('--prioridade', default='Medium', choices=list(ORD), help='Prioridade (padrão: Medium)')
    ap.add_argument('--modulo', help='Módulo do sistema (opcional)')
    ap.add_argument('--complexidade', choices=list(ORD), help='Complexidade estimada (opcional)')
    ap.add_argument('--vertical', help='Vertical: Turismo, Agro, Fiscal, Varejo, ... (opcional)')
    ap.add_argument('--origem-bug', dest='origem_bug', choices=['Sim', 'Não'], help='Origem bug (opcional)')
    ap.add_argument('--desenvolvedor', nargs='+', help='Um ou mais desenvolvedores (vários = simulação de alocação)')
    ap.add_argument('--analista-requisitos', dest='analista_requisitos', help='Analista de requisitos (opcional)')
    ap.add_argument('--titulo', default='', help='Título (resumo) da task')
    ap.add_argument('--epic', dest='chave_pai', help='Chave do Epic ou do item pai, se houver (opcional)')
    ap.add_argument('--data-criacao', dest='data_criacao', help='Data/hora de criação (AAAA-MM-DD HH:MM). Padrão: agora')
    ap.add_argument('--arquivo', help='CSV com várias tasks (colunas: ' + ', '.join(CAMPOS_CSV) + ')')
    ap.add_argument('--saida', help='Grava as previsões do --arquivo neste CSV')
    ap.add_argument('--historico', default=str(CSV_PADRAO), help=f'Exportação do Jira (padrão: {CSV_PADRAO})')
    ap.add_argument('--modelo', default=str(MODELO_PADRAO), help='Modelo treinado (.joblib)')
    ap.add_argument('--detalhes', action='store_true', help='Mostra todos os atributos usados na previsão')
    ap.add_argument('--listar-valores', action='store_true', help='Lista os valores conhecidos pelo modelo')
    a = ap.parse_args(argv)

    pacote = carregar_modelo(a.modelo)
    if a.listar_valores:
        for campo, vals in pacote['valores_conhecidos'].items():
            print(f'\n{campo} ({len(vals)}):\n  ' + '\n  '.join(vals))
        return 0

    if a.arquivo:
        tasks = pd.read_csv(a.arquivo, dtype=str, comment='#').to_dict('records')
    else:
        if not (a.tipo and a.projeto):
            ap.error('informe --tipo e --projeto (ou use --arquivo)')
        devs = a.desenvolvedor or [None]
        base = {k: getattr(a, k) for k in CAMPOS_CSV if k != 'desenvolvedor'}
        tasks = [dict(base, desenvolvedor=d) for d in devs]

    if not Path(a.historico).exists():
        print(f'Exportação do Jira não encontrada: {a.historico}\n'
              'Coloque a exportação mais recente em data/raw/ ou informe --historico.', file=sys.stderr)
        return 1
    print(f'Lendo o histórico do Jira: {a.historico} ...', file=sys.stderr)
    ctx, fim_hist = preparar_historico(a.historico)

    agora = pd.Timestamp.now().floor('min')
    linhas, avisos, processadas = [], set(), []
    for t in tasks:
        t = {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in t.items()}
        processadas.append(t)
        t['data_criacao'] = ler_data(t.get('data_criacao')) or agora
        if t['data_criacao'] - fim_hist > pd.Timedelta(days=DIAS_HISTORICO_DESATUALIZADO):
            avisos.add(f'a exportação do Jira vai até {fim_hist:%d/%m/%Y}; para a data {t["data_criacao"]:%d/%m/%Y} '
                       'a carga e o histórico do desenvolvedor ficam desatualizados — exporte o Jira novamente')
        linha = montar_linha(t, ctx)
        avisos.update(avisos_de_valores(linha, pacote['valores_conhecidos']))
        linhas.append(linha)

    prev = prever(pacote, linhas)
    res = pd.DataFrame(linhas)
    res.insert(0, 'lead_time_previsto_h', prev.round(1))
    res.insert(1, 'lead_time_previsto_dias', (prev / 24).round(1))
    if 'titulo' in pd.DataFrame(tasks).columns:
        res.insert(2, 'titulo', [t.get('titulo') for t in tasks])

    for av in sorted(avisos):
        print('Aviso:', av, file=sys.stderr)

    if a.arquivo:
        if a.saida:
            res.to_csv(a.saida, index=False, encoding='utf-8-sig')
            print(f'{len(res)} previsões gravadas em {a.saida}')
        else:
            print(res[['titulo', 'tipo_item', 'desenvolvedor', 'lead_time_previsto_h', 'lead_time_previsto_dias']].to_string(index=False))
    else:
        cols = ['desenvolvedor', 'lead_time_previsto_h', 'lead_time_previsto_dias', 'dev_tasks_concluidas_antes',
                'carga_dev_abertas', 'dev_lead_time_mediano_passado']
        tab = res[cols].sort_values('lead_time_previsto_h').rename(columns={
            'desenvolvedor': 'Desenvolvedor', 'lead_time_previsto_h': 'Previsto (h)', 'lead_time_previsto_dias': 'Previsto (dias)',
            'dev_tasks_concluidas_antes': 'Tasks concluídas', 'carga_dev_abertas': 'Abertas agora',
            'dev_lead_time_mediano_passado': 'Mediana histórica (h)'})
        print(f'\nTask: {a.tipo} | {a.projeto} | prioridade {a.prioridade} | "{a.titulo}"')
        print(f'Criação considerada: {processadas[0]["data_criacao"]:%d/%m/%Y %H:%M}\n')
        print(tab.to_string(index=False, na_rep='-'))
        if a.detalhes:
            print('\nAtributos usados pelo modelo:')
            print(res[ATRIBUTOS].T.to_string(header=False, na_rep='(vazio)'))

    print(f'\nModelo: {pacote["nome"]} | erro absoluto mediano no teste: {pacote.get("mdae_teste_h", float("nan")):.0f} h | '
          f'erro médio (MAE): {pacote.get("mae_teste_h", float("nan")):.0f} h. '
          'Use a previsão como referência, não como prazo garantido.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
