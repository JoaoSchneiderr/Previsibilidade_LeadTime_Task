# SPEC — Previsão do Lead Time de Tasks de Sprint por meio de Aprendizado de Máquina

**Projeto:** TCC — Previsão do Lead Time de Tasks de Sprint por meio de Aprendizado de Máquina
**Autor:** João Lucas Schneider
**Curso:** Tecnologia em Análise e Desenvolvimento de Sistemas — UNIMATER
**Ano:** 2026
**Orientador:** Prof. Dr. Rafael Rodrigues Barbosa

---

# 1. Visão Geral

## 1.1 Objetivo do projeto

Desenvolver uma solução baseada em aprendizado de máquina supervisionado capaz de prever o **lead time de novas tasks de sprint**, utilizando como fonte de dados o histórico de tasks de uma equipe de desenvolvimento.

O sistema deverá utilizar dados históricos exportados do Jira para:

1. realizar o tratamento dos dados;
2. calcular o lead time real das tasks;
3. realizar engenharia de atributos;
4. treinar diferentes modelos de regressão;
5. comparar o desempenho dos modelos;
6. identificar o modelo com melhor desempenho;
7. comparar o melhor modelo com um baseline;
8. identificar as variáveis mais relevantes para a previsão;
9. aplicar o modelo treinado a uma nova task;
10. retornar uma estimativa de lead time.

A proposta acadêmica define como objetivo geral desenvolver e avaliar modelos capazes de prever o lead time de novas demandas a partir do histórico de desenvolvimento, apoiando a alocação de desenvolvedores e a estimativa de horas para orçamento.

---

# 2. Problema

Equipes de desenvolvimento de software frequentemente estimam o tempo necessário para concluir uma task com base na experiência dos desenvolvedores ou do gerente.

Esse processo pode apresentar elevada variabilidade e dificultar:

* planejamento das sprints;
* distribuição das demandas;
* alocação de desenvolvedores;
* estimativa de horas;
* previsão de custos;
* identificação de fatores que influenciam o tempo de execução.

O projeto pretende utilizar dados históricos para construir uma abordagem quantitativa de previsão.

---

# 3. Escopo

## 3.1 Dentro do escopo

O sistema deverá contemplar:

* importação de dados históricos provenientes do Jira;
* validação da estrutura da base;
* tratamento de dados ausentes e inconsistentes;
* anonimização dos identificadores dos desenvolvedores;
* cálculo do lead time;
* criação de atributos derivados;
* análise exploratória;
* divisão temporal dos dados;
* treinamento de modelos de regressão;
* otimização de hiperparâmetros;
* avaliação dos modelos;
* comparação com baseline;
* análise de importância das variáveis;
* persistência do modelo vencedor;
* previsão de novas tasks;
* geração de gráficos e tabelas para análise do TCC.

## 3.2 Fora do escopo

O sistema NÃO deverá:

* acessar diretamente a API do Jira;
* alterar tasks no Jira;
* criar ou editar sprints;
* alterar a prioridade das tasks;
* substituir a decisão do gerente;
* realizar previsão de custos automaticamente sem parâmetros fornecidos;
* utilizar informações que somente ficam disponíveis após o início da task;
* utilizar o histórico de status como variável de entrada da previsão;
* implementar modelos de redes neurais;
* criar uma plataforma SaaS;
* implementar autenticação ou controle de usuários.

A extração do Jira será realizada externamente e disponibilizada ao projeto em formato tabular.

---

# 4. Fonte dos Dados

A fonte primária dos dados será uma exportação histórica proveniente do Jira.

A proposta prevê que a equipe responsável pela base realize a extração, uma vez que o acadêmico não terá acesso direto à API do Jira.

O arquivo deverá conter, quando disponíveis, os seguintes campos:

| Campo            | Tipo               | Utilização              |
| ---------------- | ------------------ | ----------------------- |
| desenvolvedor    | categórico         | Entrada do modelo       |
| data_criacao     | datetime           | Cálculo do lead time    |
| data_conclusao   | datetime           | Cálculo do lead time    |
| historico_status | estruturado        | Cálculo/análise         |
| tags             | categórico         | Entrada                 |
| modulo           | categórico         | Entrada                 |
| prioridade       | categórico/ordinal | Entrada                 |
| titulo           | texto              | Engenharia de atributos |
| descricao        | texto              | Engenharia de atributos |
| sprint           | categórico         | Entrada/análise         |
| lead_time        | numérico           | Variável alvo           |

O campo `lead_time` não deverá existir obrigatoriamente no arquivo original.

Ele deverá ser calculado pelo sistema:

```text
lead_time = data_conclusao - data_criacao
```

A unidade principal utilizada pelo projeto será **horas**.

---

# 5. Regra Fundamental contra Data Leakage

Esta é uma das regras mais importantes do projeto.

O modelo somente poderá utilizar informações que estejam disponíveis **no momento da criação da task**.

Não deverão ser utilizadas como variáveis preditoras informações que surgem durante a execução da task.

### Permitido

* desenvolvedor;
* prioridade;
* módulo;
* tags;
* sprint;
* tipo da demanda;
* complexidade estimada;
* tamanho do título;
* tamanho da descrição;
* demais atributos disponíveis na criação.

### Não permitido

* data de conclusão;
* duração real;
* histórico de status;
* quantidade de alterações posteriores;
* tempo aguardando revisão;
* tempo aguardando desenvolvimento;
* informações adicionadas depois da criação da task.

O `historico_status` deverá ser utilizado para calcular/analisar o lead time, mas não deverá ser utilizado como entrada do modelo.

---

# 6. Arquitetura do Projeto

A solução deverá seguir uma arquitetura simples e modular.

```text
Dados Jira
    |
    v
[Importação]
    |
    v
[Validação]
    |
    v
[Pré-processamento]
    |
    v
[Engenharia de Atributos]
    |
    +----------------------+
    |                      |
    v                      v
[Treinamento]          [Análise]
    |
    v
[Modelos]
    |
    +--> Gradient Boosting
    +--> Random Forest
    +--> XGBoost
    +--> LightGBM
    +--> CatBoost
    |
    v
[Avaliação]
    |
    +--> MAE
    +--> RMSE
    +--> R²
    |
    v
[Seleção do melhor modelo]
    |
    v
[Persistência]
    |
    v
[Inferência de nova Task]
    |
    v
[Lead Time estimado]
```

---

# 7. Stack Tecnológica

## 7.1 Linguagem

* Python 3.11+

## 7.2 Bibliotecas

### Manipulação

* pandas
* NumPy

### Machine Learning

* scikit-learn
* XGBoost
* LightGBM
* CatBoost

### Visualização

* Matplotlib
* Seaborn

### Persistência

* joblib

### Ambiente de experimentação

* Jupyter Notebook

### Testes

* pytest

---

# 8. Estrutura do Repositório

O projeto deverá utilizar a seguinte estrutura:

```text
lead-time-prediction/
│
├── README.md
├── SPEC.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── notebooks/
│   ├── 01_exploracao.ipynb
│   ├── 02_preprocessamento.ipynb
│   ├── 03_modelagem.ipynb
│   └── 04_avaliacao.ipynb
│
├── src/
│   ├── __init__.py
│   │
│   ├── config.py
│   │
│   ├── data/
│   │   ├── loader.py
│   │   ├── validator.py
│   │   └── preprocessing.py
│   │
│   ├── features/
│   │   └── engineering.py
│   │
│   ├── models/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   ├── baseline.py
│   │   └── predict.py
│   │
│   ├── visualization/
│   │   └── plots.py
│   │
│   └── utils/
│       └── logger.py
│
├── models/
│   ├── best_model.joblib
│   └── preprocessing_pipeline.joblib
│
├── reports/
│   ├── figures/
│   └── metrics/
│
├── tests/
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_prediction.py
│
└── scripts/
    ├── train.py
    ├── evaluate.py
    └── predict.py
```

---

# 9. Pipeline de Dados

## 9.1 Importação

O sistema deverá aceitar arquivo CSV ou formato tabular equivalente.

Exemplo:

```bash
python scripts/train.py --input data/raw/tasks.csv
```

O carregamento deverá:

1. localizar o arquivo;
2. verificar sua existência;
3. verificar as colunas obrigatórias;
4. informar colunas ausentes;
5. converter tipos;
6. registrar quantidade de registros carregados.

---

# 10. Validação dos Dados

Antes do treinamento, o sistema deverá verificar:

* existência das colunas obrigatórias;
* valores nulos;
* datas inválidas;
* data de conclusão anterior à criação;
* tasks sem conclusão;
* valores duplicados;
* categorias inconsistentes;
* valores extremos de lead time.

Tasks impossíveis de serem utilizadas deverão ser registradas em log e tratadas conforme uma regra explícita.

O sistema não deverá simplesmente excluir dados silenciosamente.

---

# 11. Anonimização

Os identificadores dos desenvolvedores deverão ser anonimizados.

Exemplo:

```text
joao.silva -> DEV_001
maria.souza -> DEV_002
carlos.santos -> DEV_003
```

A anonimização deverá ser consistente dentro da mesma execução.

Não deverá ser armazenado no repositório nenhum dado pessoal real dos desenvolvedores.

Arquivos contendo dados reais deverão estar no `.gitignore`.

---

# 12. Engenharia de Atributos

A engenharia de atributos deverá utilizar somente informações disponíveis na criação da task.

Atributos possíveis:

### Texto

```text
titulo_tamanho
descricao_tamanho
titulo_palavras
descricao_palavras
```

### Categoria

```text
tipo_demanda
modulo
prioridade
desenvolvedor
sprint
tags
```

### Complexidade

Quando disponível:

```text
complexidade_estimada
```

### Data

A partir de `data_criacao`, podem ser derivados:

```text
dia_semana
mes
hora_criacao
```

Esses atributos deverão ser avaliados empiricamente e somente mantidos caso façam sentido para o experimento.

---

# 13. Variável Target

A variável alvo será:

```text
lead_time
```

Definição:

```text
lead_time = data_conclusao - data_criacao
```

Resultado:

```text
lead_time em horas
```

Exemplo:

```text
Criação:    10/08/2026 08:00
Conclusão:  11/08/2026 14:00

Lead Time = 30 horas
```

---

# 14. Divisão dos Dados

A divisão deverá ser **temporal**.

Não utilizar divisão aleatória como estratégia principal.

Exemplo:

```text
Histórico mais antigo
        |
        v
   TREINAMENTO
        |
        v
Histórico mais recente
        |
        v
       TESTE
```

A finalidade é simular o cenário real:

> utilizar histórico conhecido para prever uma task futura.

O conjunto de teste não deverá ser utilizado no treinamento ou na otimização dos hiperparâmetros.

---

# 15. Modelos Obrigatórios

O sistema deverá implementar e comparar cinco algoritmos:

1. Gradient Boosting
2. Random Forest
3. XGBoost
4. LightGBM
5. CatBoost

Cada modelo deverá possuir uma configuração inicial e uma estratégia de ajuste de hiperparâmetros.

O código deverá permitir adicionar novos modelos futuramente sem alterar toda a arquitetura.

---

# 16. Pipeline de Pré-processamento

O pré-processamento deverá ser integrado ao pipeline de treinamento.

Para atributos numéricos:

* tratamento de valores ausentes;
* normalização somente quando necessária ao algoritmo.

Para atributos categóricos:

* tratamento de valores ausentes;
* codificação apropriada.

Para atributos textuais:

* inicialmente utilizar características simples derivadas do texto, como tamanho e quantidade de palavras.

Não é objetivo desta versão utilizar modelos de linguagem ou redes neurais para processamento textual.

---

# 17. Avaliação

Cada modelo deverá ser avaliado utilizando:

## MAE

Mean Absolute Error.

Indica o erro absoluto médio da previsão.

Quanto menor, melhor.

## RMSE

Root Mean Squared Error.

Penaliza erros maiores de maneira mais intensa.

Quanto menor, melhor.

## R²

Coeficiente de determinação.

Indica a capacidade do modelo de explicar a variação dos dados.

Quanto maior, melhor.

Os resultados deverão ser armazenados em uma tabela:

```text
modelo | MAE | RMSE | R2
```

---

# 18. Baseline

O sistema deverá possuir um modelo de referência simples.

O baseline deverá utilizar a média histórica do lead time, podendo ser calculada por:

* tipo de demanda;
* complexidade estimada;
* ou combinação definida conforme a disponibilidade dos dados.

O método utilizado deverá ser documentado no relatório.

A finalidade é verificar se os modelos de Machine Learning realmente apresentam ganho em relação a uma abordagem simples.

---

# 19. Seleção do Melhor Modelo

O sistema deverá identificar automaticamente o modelo com melhor desempenho.

O critério principal será o **menor MAE**, mantendo RMSE e R² como métricas complementares.

Exemplo:

```text
Modelo vencedor:
XGBoost

MAE: 12.42
RMSE: 19.31
R²: 0.71
```

Os valores acima são apenas ilustrativos.

O sistema não deverá criar resultados fictícios.

---

# 20. Feature Importance

Para o modelo vencedor deverá ser realizada análise das variáveis mais relevantes.

O resultado deverá apresentar um ranking:

```text
1. complexidade_estimada
2. modulo
3. desenvolvedor
4. prioridade
5. titulo_tamanho
6. descricao_tamanho
```

A técnica utilizada deverá ser compatível com o modelo.

Sempre que possível, deverá ser utilizada uma abordagem consistente entre os modelos para permitir comparação.

---

# 21. Artefatos da Avaliação

O sistema deverá gerar obrigatoriamente:

### 21.1 Tabela comparativa

```text
Modelo | MAE | RMSE | R²
```

### 21.2 Gráfico previsto x real

Gráfico de dispersão:

```text
X = Lead Time Real
Y = Lead Time Previsto
```

### 21.3 Ranking de importância

Gráfico das principais variáveis.

### 21.4 Comparação com baseline

Apresentar:

```text
Erro baseline
Erro modelo
Redução percentual do erro
```

Fórmula:

```text
redução = ((erro_baseline - erro_modelo) / erro_baseline) * 100
```

---

# 22. Inferência

Após o treinamento, o melhor modelo deverá ser salvo.

Exemplo:

```text
models/
└── best_model.joblib
```

O pipeline de pré-processamento também deverá ser salvo.

A previsão deverá ser executada sem necessidade de novo treinamento.

Exemplo:

```bash
python scripts/predict.py
```

O usuário deverá informar os dados disponíveis para uma nova task.

Exemplo:

```text
Tipo da demanda: Melhoria
Prioridade: Alta
Módulo: Financeiro
Complexidade: 5
Título: Ajustar cálculo de desconto
Descrição: Corrigir cálculo...
Desenvolvedor: DEV_003
Sprint: Sprint 25
```

Resultado:

```text
Lead Time estimado: 18,7 horas
```

A saída deverá deixar claro que se trata de uma **estimativa**, não de uma garantia.

---

# 23. Interface de Consulta

A primeira versão deverá priorizar simplicidade.

Não é necessário criar uma aplicação web complexa.

A interface mínima poderá ser executada localmente e deverá permitir:

1. informar os dados da nova task;
2. executar o modelo;
3. exibir o lead time estimado;
4. informar a unidade da previsão;
5. informar qual modelo foi utilizado.

Exemplo:

```text
========================================
 PREVISÃO DE LEAD TIME
========================================

Tipo: Melhoria
Prioridade: Alta
Módulo: Financeiro
Complexidade: 5
Desenvolvedor: DEV_003

----------------------------------------
Lead Time estimado: 18,7 horas
Modelo: XGBoost
----------------------------------------
```

Uma interface gráfica/local poderá ser adicionada posteriormente, mas não deverá ser requisito para o funcionamento do projeto.

---

# 24. CLI

O projeto deverá possuir comandos separados.

## Treinamento

```bash
python scripts/train.py --input data/raw/tasks.csv
```

## Avaliação

```bash
python scripts/evaluate.py
```

## Predição

```bash
python scripts/predict.py
```

---

# 25. Saídas do Treinamento

Após o treinamento, o sistema deverá gerar:

```text
models/
    best_model.joblib
    preprocessing_pipeline.joblib

reports/
    metrics/
        model_comparison.csv
        baseline_comparison.csv

    figures/
        predictions_vs_real.png
        feature_importance.png
        model_comparison.png
```

---

# 26. Logs

O sistema deverá registrar:

* quantidade de registros importados;
* quantidade de registros removidos;
* motivos das remoções;
* quantidade de registros utilizados no treinamento;
* quantidade utilizada no teste;
* modelos treinados;
* métricas;
* modelo vencedor;
* erros durante execução.

Não registrar dados sensíveis ou informações pessoais reais.

---

# 27. Testes

Deverão existir testes automatizados para:

### Dados

* cálculo correto do lead time;
* validação de colunas;
* tratamento de datas;
* tratamento de valores ausentes.

### Features

* geração correta das variáveis;
* ausência de informações futuras;
* consistência das transformações.

### Modelos

* treinamento sem erro;
* geração de previsão;
* cálculo correto das métricas.

### Inferência

* carregamento do modelo;
* aplicação correta do pipeline;
* geração de previsão para uma nova task.

---

# 28. Critérios de Aceitação

O projeto será considerado funcional quando:

* [ ] Um arquivo histórico do Jira puder ser carregado.
* [ ] Os dados forem validados.
* [ ] O lead time puder ser calculado automaticamente.
* [ ] Desenvolvedores puderem ser anonimizados.
* [ ] As features forem geradas automaticamente.
* [ ] A divisão temporal puder ser executada.
* [ ] Os cinco modelos forem treinados.
* [ ] Os cinco modelos forem avaliados.
* [ ] MAE, RMSE e R² forem calculados.
* [ ] O baseline for calculado.
* [ ] O modelo vencedor for identificado.
* [ ] A importância das variáveis for calculada.
* [ ] Os gráficos forem gerados.
* [ ] O modelo vencedor puder ser salvo.
* [ ] Uma nova task puder receber uma previsão.
* [ ] O projeto puder ser executado novamente por outro usuário seguindo o README.
* [ ] Nenhum dado real/sensível seja versionado no GitHub.

---

# 29. Organização das Tasks de Desenvolvimento

## Fase 1 — Configuração

* [ ] Criar estrutura do projeto.
* [ ] Criar ambiente Python.
* [ ] Criar `requirements.txt`.
* [ ] Criar `.gitignore`.
* [ ] Criar README inicial.
* [ ] Criar configuração central do projeto.

## Fase 2 — Dados

* [ ] Criar carregador de CSV.
* [ ] Criar validador de dados.
* [ ] Implementar tratamento de datas.
* [ ] Implementar cálculo do lead time.
* [ ] Implementar anonimização.
* [ ] Implementar tratamento de valores ausentes.
* [ ] Criar dataset processado.

## Fase 3 — Engenharia de Atributos

* [ ] Implementar atributos derivados do título.
* [ ] Implementar atributos derivados da descrição.
* [ ] Implementar atributos temporais.
* [ ] Implementar atributos categóricos.
* [ ] Documentar cada feature criada.
* [ ] Garantir ausência de data leakage.

## Fase 4 — Modelagem

* [ ] Implementar Gradient Boosting.
* [ ] Implementar Random Forest.
* [ ] Implementar XGBoost.
* [ ] Implementar LightGBM.
* [ ] Implementar CatBoost.
* [ ] Implementar ajuste de hiperparâmetros.
* [ ] Implementar divisão temporal.

## Fase 5 — Avaliação

* [ ] Implementar MAE.
* [ ] Implementar RMSE.
* [ ] Implementar R².
* [ ] Implementar baseline.
* [ ] Comparar modelos.
* [ ] Selecionar modelo vencedor.
* [ ] Calcular redução de erro contra baseline.
* [ ] Gerar feature importance.

## Fase 6 — Visualização

* [ ] Criar gráfico previsto x real.
* [ ] Criar gráfico de comparação dos modelos.
* [ ] Criar gráfico de feature importance.
* [ ] Criar gráfico de comparação com baseline.
* [ ] Salvar resultados em `reports/`.

## Fase 7 — Inferência

* [ ] Salvar modelo vencedor.
* [ ] Salvar pipeline de transformação.
* [ ] Criar script de previsão.
* [ ] Criar entrada de nova task.
* [ ] Implementar previsão.
* [ ] Exibir resultado.

## Fase 8 — Qualidade

* [ ] Criar testes automatizados.
* [ ] Testar pipeline completo.
* [ ] Validar execução em ambiente limpo.
* [ ] Revisar tratamento de erros.
* [ ] Revisar documentação.
* [ ] Garantir que dados reais não sejam enviados ao Git.

---

# 31. Definition of Done

Uma funcionalidade somente será considerada concluída quando:

* estiver implementada;
* estiver testada;
* não quebrar funcionalidades existentes;
* estiver documentada;
* não introduzir data leakage;
* não utilizar dados reais no repositório;
* puder ser executada por meio das instruções do README.

---

# 32. Resultado Final Esperado

Ao final do desenvolvimento, o projeto deverá permitir executar o seguinte fluxo:

```text
CSV exportado do Jira
        ↓
Validação
        ↓
Pré-processamento
        ↓
Cálculo do Lead Time
        ↓
Engenharia de Atributos
        ↓
Divisão Temporal
        ↓
Treinamento
        ↓
┌───────────────────────────┐
│ Gradient Boosting         │
│ Random Forest             │
│ XGBoost                   │
│ LightGBM                  │
│ CatBoost                  │
└───────────────────────────┘
        ↓
Avaliação
        ↓
MAE / RMSE / R²
        ↓
Comparação com Baseline
        ↓
Seleção do Melhor Modelo
        ↓
Feature Importance
        ↓
Salvar Modelo
        ↓
Nova Task
        ↓
Previsão do Lead Time
```

O resultado final deverá fornecer uma ferramenta experimental capaz de receber os atributos disponíveis no momento da criação de uma nova task e retornar uma estimativa de seu lead time, utilizando o modelo de melhor desempenho identificado nos experimentos.

O sistema deverá ser tratado como uma **ferramenta de apoio à decisão**, e não como substituto da avaliação do gerente ou dos desenvolvedores.
