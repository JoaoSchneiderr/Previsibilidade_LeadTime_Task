"""
Etapa 1: tratamento da exportação do Jira e cálculo do lead time.
Uso:  python pipeline_tcc/01_tratamento.py [caminho_da_exportacao.csv]
Saída: pipeline_tcc/saidas/base_tratada.pkl e base_tratada_stats.json
As regras estão documentadas em comum.tratar().
"""
import json
import sys

from comum import CSV_PADRAO, SAIDAS, tratar


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else CSV_PADRAO
    SAIDAS.mkdir(exist_ok=True)
    base, st = tratar(src)
    base.to_pickle(SAIDAS / 'base_tratada.pkl')
    (SAIDAS / 'base_tratada_stats.json').write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(st, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
