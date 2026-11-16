"""
Etapa 3: engenharia de atributos.
Somente informações disponíveis no momento da criação da task (sem vazamento de dados).
Excluídos por decisão do projeto: Analista de Teste, Story Points - Dev, Tempo gasto,
histórico de status ([CHART] Time in Status), Sprint, Descrição e demais campos sensíveis.
Uso:  python pipeline_tcc/03_atributos.py [caminho_da_exportacao.csv]
Saída: pipeline_tcc/saidas/atributos.pkl
"""
import sys

import pandas as pd

from comum import CSV_PADRAO, SAIDAS, historico_bruto, montar_atributos


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else CSV_PADRAO
    base = pd.read_pickle(SAIDAS / 'base_tratada.pkl')
    X = montar_atributos(base, historico_bruto(src))
    X.to_pickle(SAIDAS / 'atributos.pkl')
    print(X.shape)
    print(X.drop(columns=['Criado_dt', 'chave']).describe(include='all').T[['count', 'unique', 'top', 'mean', 'min', 'max']].to_string())


if __name__ == '__main__':
    main()
