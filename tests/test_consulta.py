"""
Testes do script de consulta sob demanda (pipeline_tcc/05_consulta.py).

Rodar a partir da pasta do projeto:  pytest -q

Os testes que dependem da exportação real do Jira ou do modelo treinado são pulados
automaticamente quando esses arquivos não estão na máquina (eles não vão para o GitHub).
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
PIPE = RAIZ / 'pipeline_tcc'
sys.path.insert(0, str(PIPE))

import comum  # noqa: E402

spec = importlib.util.spec_from_file_location('consulta', PIPE / '05_consulta.py')
consulta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consulta)

TEM_DADOS = comum.CSV_PADRAO.exists()
TEM_MODELO = comum.MODELO_PADRAO.exists()
MOCK = PIPE / 'exemplos' / 'tasks_exemplo_MOCK.csv'
precisa_dados = pytest.mark.skipif(not TEM_DADOS, reason='exportação do Jira ausente em data/raw/')
precisa_modelo = pytest.mark.skipif(not (TEM_DADOS and TEM_MODELO), reason='modelo treinado ou exportação ausentes')


@pytest.fixture(scope='module')
def historico():
    base, _ = comum.tratar(comum.CSV_PADRAO)
    raw = comum.historico_bruto(comum.CSV_PADRAO)
    return base, raw


# ------------------------------------------------------------- sem dados reais
def test_atributos_da_task_campos_vazios_viram_nao_informado():
    a = comum.atributos_da_task('Bug', 'ERP', 'High', None, '', None, None, None, None,
                                'Erro ao salvar', pd.Timestamp('2026-09-15 09:30'))
    assert a['modulo'] == a['complexidade'] == a['vertical'] == a['desenvolvedor'] == comum.NI
    assert a['prioridade_ord'] == 4 and a['complexidade_ord'] == 0
    assert a['titulo_palavras'] == 3 and a['titulo_caracteres'] == len('Erro ao salvar')
    assert (a['mes_criacao'], a['dia_semana_criacao'], a['hora_criacao']) == (9, 1, 9)


def test_subtarefa_nao_conta_como_vinculada_a_epic():
    t = pd.Timestamp('2026-09-15')
    assert comum.atributos_da_task('Subtarefa - Bug', 'ERP', 'Low', None, None, None, None, None, None, 'x', t, 'ERP-1')['vinculada_epic'] == 0
    assert comum.atributos_da_task('Melhoria', 'ERP', 'Low', None, None, None, None, None, None, 'x', t, 'ERP-1')['vinculada_epic'] == 1


def test_arquivo_mock_esta_identificado():
    assert 'SAMPLE / MOCK DATA' in MOCK.read_text(encoding='utf-8').splitlines()[0]


# ------------------------------------------------------------- com dados reais
@precisa_dados
def test_paridade_treino_e_consulta(historico):
    """Uma task da base, descrita pelo caminho da consulta, deve gerar exatamente os atributos do treino."""
    base, raw = historico
    X = comum.montar_atributos(base, raw)
    ctx = comum.Contexto(raw, base)
    b = base.sort_values('Criado_dt').reset_index(drop=True)
    for i in np.linspace(0, len(b) - 1, 60).astype(int):
        r = b.iloc[i]
        task = dict(tipo=r['Tipo de item'], projeto=r['Chave do projeto'], prioridade=r['Prioridade'], modulo=r[comum.MOD],
                    complexidade=r[comum.CPX], vertical=r[comum.VERT], origem_bug=r[comum.OBUG],
                    desenvolvedor=r['desenvolvedor'], analista_requisitos=r[comum.AREQ], titulo=r['Resumo'],
                    data_criacao=r['Criado_dt'], chave_pai=r['Chave pai'])
        linha = consulta.montar_linha(task, ctx)
        for c in comum.ATRIBUTOS:
            esperado, obtido = X.loc[i, c], linha[c]
            if c in comum.NUMERICOS:
                assert (pd.isna(esperado) and pd.isna(obtido)) or np.isclose(float(esperado), float(obtido)), (r['Chave da item'], c)
            else:
                assert str(esperado) == str(obtido), (r['Chave da item'], c)


@precisa_modelo
def test_consulta_em_lote_com_tasks_mock(tmp_path):
    saida = tmp_path / 'prev.csv'
    assert consulta.main(['--arquivo', str(MOCK), '--saida', str(saida)]) == 0
    res = pd.read_csv(saida)
    assert len(res) == 6
    assert (res['lead_time_previsto_h'] > 0).all() and np.isfinite(res['lead_time_previsto_h']).all()
    assert np.allclose(res['lead_time_previsto_dias'], res['lead_time_previsto_h'] / 24, atol=0.06)


@precisa_modelo
def test_consulta_e_deterministica(tmp_path):
    s1, s2 = tmp_path / 'a.csv', tmp_path / 'b.csv'
    consulta.main(['--arquivo', str(MOCK), '--saida', str(s1)])
    consulta.main(['--arquivo', str(MOCK), '--saida', str(s2)])
    assert pd.read_csv(s1)['lead_time_previsto_h'].equals(pd.read_csv(s2)['lead_time_previsto_h'])


@precisa_modelo
def test_simulacao_com_varios_desenvolvedores(capsys):
    assert consulta.main(['--tipo', 'Bug', '--projeto', 'ERP', '--prioridade', 'High', '--titulo', 'Erro ao salvar pedido',
                          '--desenvolvedor', 'DEV_EXEMPLO_1', 'DEV_EXEMPLO_2', '--data-criacao', '2026-09-20 10:00']) == 0
    out = capsys.readouterr().out
    assert 'DEV_EXEMPLO_1' in out and 'DEV_EXEMPLO_2' in out and 'Previsto (h)' in out
