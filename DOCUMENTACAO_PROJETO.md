# Documentação do Projeto — Previsibilidade do Lead Time de Tasks de Sprint

## 1. Objetivo do documento

Este documento registra, de forma detalhada e em ordem cronológica, tudo que foi realizado no projeto até o momento, além dos próximos passos planejados para o desenvolvimento da solução de previsão do lead time de tasks de sprint.

A documentação foi estruturada para manter o acompanhamento do trabalho em etapas, preservar a rastreabilidade do projeto e facilitar futuras alterações, validações e apresentações acadêmicas.

---

## 2. Contexto do projeto

O projeto tem como objetivo desenvolver uma solução baseada em aprendizado de máquina para prever o lead time de novas tasks de sprint, utilizando dados históricos de desenvolvimento.

A base conceitual do projeto foi definida no documento de especificação e no escopo do TCC, com foco em:

- importação de dados históricos exportados do Jira;
- validação e tratamento dos dados;
- cálculo do lead time real;
- engenharia de atributos;
- treinamento de modelos de regressão;
- comparação entre modelos;
- seleção do melhor modelo;
- persistência do modelo;
- inferência para novas tasks;
- análise de variáveis relevantes.

A regra de integridade do projeto também foi considerada desde o início:

- não usar dados reais sensíveis;
- não inventar resultados;
- não substituir divisão temporal por amostragem aleatória;
- evitar data leakage;
- manter a lógica de implementação em src/;
- usar notebooks apenas para exploração e apresentação;
- manter reprodutibilidade com random_state configurável.

---

## 3. Arquivos e artefatos já existentes no repositório

Até o momento, o repositório contém os seguintes artefatos principais:

- [CLAUDE.md](CLAUDE.md): documento de regras e orientações do projeto;
- [README.md](README.md): arquivo inicial do projeto;
- [SPEC.md](SPEC.md): especificação técnica e conceitual do TCC;
- [Proposta_TCC_PREV_LEADTIME.docx (2).pdf](Proposta_TCC_PREV_LEADTIME.docx%20(2).pdf): proposta do TCC aprovada;
- estrutura de diretórios criada para organização do código e dos dados.

---

## 4. Etapas executadas

### Etapa 1 — Leitura e análise da base documental do projeto

Data: 2026-10-09

Ações realizadas:

- leitura do arquivo [README.md](README.md);
- leitura do documento de especificação em [SPEC.md](SPEC.md);
- leitura do arquivo de regras em [CLAUDE.md](CLAUDE.md);
- identificação do objetivo acadêmico, escopo e arquitetura esperada do sistema.

Resultado:

- foi confirmada a definição do problema, os requisitos do TCC e a direção metodológica da solução;
- foi identificado que o projeto deve seguir uma arquitetura simples e modular, com foco em regressão supervisionada;
- foi mantida a separação temporal e a prevenção de data leakage como prioridade metodológica.

---

### Etapa 2 — Organização inicial da estrutura de pastas

Data: 2026-10-09

Ações realizadas:

- criação da pasta principal do projeto;
- criação da estrutura de diretórios para código-fonte e artefatos de dados;
- organização de pastas para:
  - código-fonte em src/;
  - dados crus em data/raw/;
  - dados processados em data/processed/;
  - notebooks em notebooks/;
  - testes em tests/;
  - relatórios em reports/.

Estrutura criada:

- [src](src)
- [src/data](src/data)
- [src/features](src/features)
- [src/models](src/models)
- [src/evaluation](src/evaluation)
- [data](data)
- [data/raw](data/raw)
- [data/processed](data/processed)
- [notebooks](notebooks)
- [tests](tests)
- [reports](reports)

Resultado:

- o repositório passou a ter uma base de organização adequada para o desenvolvimento incremental do projeto;
- a separação entre código, dados e documentação ficou alinhada à regra de modularização do TCC.

---

### Etapa 3 — Extração e coleta da base histórica

Data: 2026-10-09

Ações realizadas:

- recebimento e organização da exportação histórica em formato tabular para uso no projeto;
- armazenamento do arquivo bruto em [data/raw/Extração_limpa_final.xlsx](data/raw/Extração_limpa_final.xlsx);
- registro do processo de tratamento e coleta em [Processo_Tratamento_Dados_TCC.docx.pdf](Processo_Tratamento_Dados_TCC.docx.pdf);
- manutenção da base em estado bruto, preservando a rastreabilidade e evitando que a etapa de coleta seja confundida com a etapa de modelagem.

Resultado:

- o projeto passou a contar com a base histórica necessária para a etapa seguinte;
- foi preservada a origem da informação em arquivo exportado, sem depender de API direta do Jira;
- a extração foi tratada como entrada do pipeline de processamento, respeitando a arquitetura definida no escopo do TCC.

---

### Etapa 4 — Pipeline inicial de validação e preparação da base

Data: 2026-10-09

Ações realizadas:

- criação do módulo [src/data/data_pipeline.py](src/data/data_pipeline.py) para carregar a base extraída;
- padronização dos nomes das colunas para o formato esperado pelo projeto;
- validação da presença das colunas obrigatórias da base;
- conversão das colunas de data para datetime;
- cálculo da variável alvo `lead_time_hours` como diferença entre data de conclusão e data de criação;
- preparação da estrutura para persistência em [data/processed](data/processed);
- organização da lógica principal em [src](src), conforme a regra de modularização do projeto.

Resultado:

- a etapa de tratamento inicial da base foi estruturada em módulo próprio;
- o pipeline passou a ser o ponto de entrada para a preparação dos dados antes do treinamento;
- o fluxo agora está alinhado com o objetivo de transformar a extração bruta em uma base pronta para engenharia de atributos e modelagem.

---

### Etapa 5 — Anonimização de nomes e situações sensíveis

Data: 2026-10-09

Ações realizadas:

- identificação dos campos sensíveis na base exportada, especialmente nomes e situações relacionadas a clientes e responsáveis;
- criação do script [src/data/anonymize_data.py](src/data/anonymize_data.py) para mascarar valores identificáveis;
- geração da versão anonimizada em [data/raw/Extração_limpa_final_anonimizada.xlsx](data/raw/Extração_limpa_final_anonimizada.xlsx);
- persistência da base mascarada também em [data/processed/tasks_dataset_anonymized.csv](data/processed/tasks_dataset_anonymized.csv);
- preservação da base original em [data/raw/Extração_limpa_final.xlsx](data/raw/Extração_limpa_final.xlsx), evitando qualquer alteração de dados sensíveis na exportação original.

Resultado:

- nomes e situações reais foram substituídos por identificadores sintéticos, como `CLIENTE_001` e `SITUACAO_001`;
- a base passou a estar pronta para processamento analítico sem expor dados reais de clientes ou responsáveis;
- a anonimização foi aplicada antes do próximo passo de modelagem, respeitando as regras do projeto e do TCC.

---

### Etapa 6 — Cálculo do lead time na base anonimizada

Data: 2026-10-09

Ações realizadas:

- preparação da etapa de cálculo da variável alvo sobre a base anonimizada;
- criação do módulo [src/features/lead_time_calculation.py](src/features/lead_time_calculation.py) para transformar as datas de criação e resolução em lead time em horas;
- padronização do processamento para manter a base em formato de tabela pronto para a engenharia de atributos;
- organização da lógica em [src/features](src/features), seguindo a estrutura modular do projeto.

Resultado esperado:

- a base anonimizada deverá ter a variável `lead_time_horas` calculada a partir das datas disponíveis;
- a informação resultante será usada como alvo para os modelos de regressão;
- o próximo passo será a engenharia de atributos e a preparação dos dados para o treinamento.

---

## 5. Estrutura de desenvolvimento planejada

A arquitetura do projeto, conforme os documentos do escopo, prevê as seguintes camadas:

### 5.1 Camada de dados

Responsável por:

- importar a base exportada do Jira;
- validar colunas e tipos de dados;
- identificar valores ausentes e inconsistentes;
- preparar a base para processamento.

Diretório previsto:

- [src/data](src/data)

---

### 5.2 Camada de features / engenharia de atributos

Responsável por:

- calcular lead time;
- criar atributos derivados relevantes;
- preparar variáveis para o modelo;
- evitar uso de informações posteriores à criação da task.

Diretório previsto:

- [src/features](src/features)

---

### 5.3 Camada de modelos

Responsável por:

- treinar os modelos de regressão;
- parametrizar algoritmos;
- usar random_state configurável;
- persisting o modelo vencedor.

Diretório previsto:

- [src/models](src/models)

Modelos previstos no escopo:

- Gradient Boosting;
- Random Forest;
- XGBoost;
- LightGBM;
- CatBoost.

---

### 5.4 Camada de avaliação

Responsável por:

- medir performance dos modelos;
- calcular MAE, RMSE e R²;
- comparar com baseline;
- registrar resultados reais após execução.

Diretório previsto:

- [src/evaluation](src/evaluation)

---

### 5.5 Dados e relatórios

Responsável por:

- manter bases brutas e processadas;
- guardar artefatos gerados;
- armazenar relatórios e gráficos de análise.

Diretórios previstos:

- [data](data)
- [reports](reports)

---

## 6. Regras metodológicas que devem orientar o desenvolvimento

Durante o desenvolvimento, as seguintes regras devem ser respeitadas rigorosamente:

### 6.1 Regras de dados

- Não inventar dados reais ou fictícios como se fossem resultados do TCC;
- Empregar apenas dados sintéticos marcados explicitamente como SAMPLE / MOCK DATA quando necessário para testes de desenvolvimento;
- Não apresentar métricas como MAE, RMSE, R², importância de variáveis ou reduções percentuais sem execução real.

### 6.2 Regras de treinamento

- Manter a divisão temporal entre treino e teste;
- Não substituir por dados aleatórios sem autorização explícita;
- Evitar data leakage;
- Usar apenas variáveis disponíveis no momento da criação da task.

### 6.3 Regras de implementação

- Manter a lógica principal em [src](src);
- Usar notebooks apenas para exploração e documentação;
- Modularizar funções e etapas do pipeline;
- Garantir reprodutibilidade com random_state configurável;
- Registrar variáveis utilizadas pelo modelo para explicabilidade.

---

## 7. Próximos passos previstos

A sequência esperada de trabalho para continuar o desenvolvimento é a seguinte:

### Passo 1 — Definir o pipeline de dados

Objetivo:

- estabelecer a rotina de carregamento e validação da base de dados.

Tarefas:

- criar módulo de importação;
- validar colunas esperadas;
- tratar tipos de dados;
- identificar valores ausentes e inconsistentes;
- preparar a estrutura de dados para cálculo do lead time.

---

### Passo 2 — Implementar cálculo do lead time

Objetivo:

- transformar a base bruta em uma tabela com target calculado.

Tarefas:

- verificar data de criação e data de conclusão;
- calcular a diferença em horas;
- padronizar a unidade da variável alvo;
- validar resultados e inconsistências.

---

### Passo 3 — Realizar engenharia de atributos

Objetivo:

- gerar variáveis úteis para a predição.

Tarefas:

- extrair atributos de título e descrição;
- transformar variáveis categóricas;
- criar features temporais e contextuais;
- registrar quais variáveis foram usadas.

---

### Passo 4 — Preparar os dados para treinamento

Objetivo:

- montar a base final para modelagem.

Tarefas:

- separar treino e teste temporalmente;
- aplicar pré-processamento;
- definir baseline inicial;
- preparar pipeline modular de treinamento.

---

### Passo 5 — Treinar e comparar modelos

Objetivo:

- avaliar diferentes algoritmos de regressão.

Tarefas:

- treinar Gradient Boosting;
- treinar Random Forest;
- treinar XGBoost;
- treinar LightGBM;
- treinar CatBoost;
- comparar métricas realistas.

---

### Passo 6 — Avaliar o melhor modelo

Objetivo:

- selecionar o modelo com melhor desempenho.

Tarefas:

- calcular MAE, RMSE e R²;
- comparar modelos com baseline;
- analisar erros e ajustes;
- registrar indicadores de desempenho com evidência real.

---

### Passo 7 — Persistência e inferência

Objetivo:

- preparar o sistema para prever novas tasks.

Tarefas:

- salvar o modelo vencedor;
- armazenar preprocessamento;
- criar rotina de predição para nova task;
- exportar valor estimado de lead time.

---

### Passo 8 — Documentação e apresentação do estudo

Objetivo:

- consolidar o resultado do projeto para apresentação acadêmica.

Tarefas:

- gerar relatórios e gráficos;
- registrar variáveis importantes;
- documentar metodologia e limitações;
- produzir material para discussão do TCC.

---

## 8. Situação atual

Status do projeto em 2026-10-09:

- [x] análise do escopo e requisitos do TCC;
- [x] leitura da especificação técnica do projeto;
- [x] definição das regras de integridade metodológica;
- [x] criação da estrutura inicial do repositório;
- [x] coleta e organização da base extraída do Jira;
- [x] registro do processo documental da coleta e tratamento;
- [x] implementação do pipeline inicial de validação e preparação da base;
- [x] anonimização de nomes e situações sensíveis;
- [x] implementação do cálculo do lead time na base anonimizada;
- [ ] validação executada do cálculo do lead time na tabela final;
- [ ] engenharia de atributos;
- [ ] treinamento dos modelos;
- [ ] comparação de desempenho;
- [ ] persistência do modelo vencedor;
- [ ] inferência para nova task.

---

## 9. Observações finais

Este documento representa o estado inicial e o registro de acompanhamento do projeto. Ele deve ser atualizado conforme cada etapa for concluída, de modo que a evolução da implementação e da metodologia permaneça transparente, organizada e rastreável.

A manutenção deste registro é importante para garantir:

- alinhamento com o escopo acadêmico;
- controle do progresso em etapas;
- facilidade de revisão por orientador ou avaliadores;
- conformidade com as regras do projeto e da pesquisa.

---

## 10. Próximo registro a ser incluído

O próximo documento de evolução deverá incluir:

- módulos criados em src/;
- código implementado por etapa;
- testes executados;
- resultados reais de treinamento;
- decisões metodológicas tomadas;
- versões e ajustes em cada iteração.
