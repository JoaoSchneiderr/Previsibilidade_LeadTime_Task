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

Incluídos em 2026-11-03:

- [reports/Processo_Tratamento_Dados_TCC.docx](reports/Processo_Tratamento_Dados_TCC.docx): documentação do tratamento dos dados (versão 3: 5ª extração, regra de subtarefas por desenvolvedor, validação do lead time e análise das tasks recentes);
- [reports/Relatorio_Atributos_e_Treinamento.docx](reports/Relatorio_Atributos_e_Treinamento.docx): engenharia de atributos, configuração do treinamento e resultados dos cinco modelos;
- [reports/figuras](reports/figuras): gráficos do relatório (MAE por modelo, importância dos atributos, real x previsto);
- [data/processed/Base_Final_Lead_Time.xlsx](data/processed/Base_Final_Lead_Time.xlsx): base final tratada (4.977 linhas), com abas de atributos, resumo e validação — **contém nomes reais, não versionar**;
- [pipeline_tcc](pipeline_tcc): scripts do tratamento, validação, atributos e treinamento, e o modelo treinado `modelo_final.joblib` — **o modelo guarda nomes reais de desenvolvedores como categorias, não versionar**.

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

### Etapa 7 — Ampliação da base com a 5ª extração do Jira

Data: 2026-11-03

Ações realizadas:

- análise da 5ª extração (`Limber__1__1.csv`, 10.000 linhas e 1.027 colunas), que contém integralmente a extração anterior (4.523 linhas) e amplia o histórico de 12 para 26 meses;
- identificação do limite de 10.000 linhas por exportação do Jira: como o arquivo está ordenado da task mais recente para a mais antiga, o corte atingiu apenas tasks anteriores a 24/07/2024;
- definição do período da base: tasks criadas de **01/08/2024 a 21/09/2026**, descartando julho/2024, que veio incompleto (59 linhas);
- decisão de não solicitar períodos mais antigos: 26 meses são suficientes, e dados antigos tendem a refletir outra equipe, outros processos e outros sistemas;
- inclusão de novos campos: Vertical (99,7% preenchido), Analista de Requisitos e Origem Bug.

Campos avaliados e excluídos:

- **Analista de Teste** e **Story Points - Dev**: preenchidos depois do início do desenvolvimento (data leakage) — decisão do projeto;
- **Tempo gasto**: só existe depois da execução (data leakage);
- **Estimativa original, Data início de desenvolvimento, Equipe, Story Points de Análise/Testes, Categoria de trabalho**: preenchimento insuficiente (0% a 4%);
- **Descrição, Cliente, Telefone Cliente, Comentários, Registro de Trabalho, Anexos**: dados sensíveis.

Resultado:

- base ampliada de 2.047 para 4.977 linhas após o tratamento.

---

### Etapa 8 — Tratamento de subtarefas por desenvolvedor

Data: 2026-11-03

Regra definida pela equipe:

- **subtarefa do mesmo desenvolvedor do item pai** → incorporada ao pai; a data de conclusão do pai passa a ser `MAX(Resolvido do pai, Resolvido dessas subtarefas)`;
- **subtarefa de outro desenvolvedor** → vira linha própria, atribuída a esse desenvolvedor; várias subtarefas do mesmo pai feitas pelo mesmo outro desenvolvedor são agrupadas numa linha, com lead time `MAX(Resolvido) − MIN(Criado)`;
- **subtarefa sem desenvolvedor identificado** → incorporada ao pai;
- **subtarefa cujo pai não está na base** → linha própria.

Desenvolvedor considerado: campo `Desenvolvedor`; se vazio, `Responsável`.

Números:

| Situação | Quantidade |
|---|---|
| Subtarefas concluídas na base filtrada | 2.111 |
| Incorporadas ao pai (mesmo desenvolvedor) | 1.512 |
| Incorporadas ao pai (desenvolvedor não identificado) | 142 |
| Subtarefas de outro desenvolvedor | 300 (agrupadas em 157 linhas) |
| Subtarefas sem pai na base | 157 |
| Itens pai com data de conclusão estendida | 96 |

Correção: na versão anterior, itens pai vinculados a um Epic (pelo campo `Chave pai`) não recebiam a data das suas subtarefas. Corrigido nesta versão.

Evolução da base:

| Etapa | Linhas |
|---|---|
| Extração bruta | 10.000 |
| Resolução = Concluídos e sem Epic | 6.833 |
| Após tratamento de subtarefas | 5.036 |
| Após recorte do período (a partir de 01/08/2024) | **4.977** (3.773 ERP, 1.204 CARD) |

Script: [pipeline_tcc/01_tratamento.py](pipeline_tcc/01_tratamento.py)

---

### Etapa 9 — Validação do cálculo do lead time

Data: 2026-11-03

Ações realizadas:

- recálculo do lead time de todas as 4.977 linhas diretamente do CSV bruto, por uma segunda implementação independente (Python puro, `csv` + `datetime.strptime`), sem reutilizar o código do tratamento;
- conferência manual de uma amostra de 8 linhas cobrindo todas as situações da regra de subtarefas.

Verificações (todas **OK**):

- mesma quantidade de linhas e mesmo conjunto de chaves no recálculo e na base;
- lead time idêntico ao recálculo (diferença máxima de 0 h);
- `lead_time_horas = (Resolvido_efetivo − Criado) / 3600`;
- nenhum lead time negativo ou vazio;
- `Resolvido_efetivo ≥ Resolvido` do próprio item;
- chaves únicas; subtarefas incorporadas não aparecem como linha própria;
- nenhuma task criada antes de 01/08/2024.

Pontos de atenção (mantidos e documentados como ruído do alvo):

- 345 linhas com fechamento em lote (10 ou mais tasks resolvidas no mesmo minuto, provavelmente no fechamento de versões);
- subtarefas encerradas meses depois do item pai (ex.: ERP-5183, 242 dias);
- 93 tasks com lead time menor que 1 hora e 29 maiores que 1 ano.

Lead time da base final: mediana 363 h, média 954 h, máximo 17.788 h.

Script: [pipeline_tcc/02_validacao.py](pipeline_tcc/02_validacao.py) — resultados nas abas `Validação*` da base final.

---

### Etapa 10 — Análise da redução do lead time nas tasks recentes

Data: 2026-11-03

- O lead time mediano do 3º trimestre de 2026 caiu para 165 h (trimestres anteriores: 234 h a 590 h). Segundo a equipe, isso está associado ao **uso de IA como apoio aos desenvolvedores**.
- Para separar esse efeito do viés das tasks ainda abertas (a base só tem tasks concluídas, e das recentes só as rápidas já terminaram), comparou-se o percentual resolvido em até 7 e 30 dias com a mesma janela de observação para todos os trimestres.
- Resultado: 3º tri/2026 com 27,1% em 7 dias e 51,2% em 30 dias, contra médias históricas de 25,3% e 50,8%. Há melhora em relação ao 1º semestre de 2026, mas o patamar é semelhante ao histórico: a maior parte da queda da mediana vem das 250 tasks do trimestre ainda abertas na extração.
- Decisão: manter todas as tasks na base e reportar também o erro no subconjunto de teste com pelo menos 90 dias de observação.

---

### Etapa 11 — Engenharia de atributos

Data: 2026-11-03

Somente informações disponíveis no momento da criação da task. Os atributos históricos usam apenas eventos anteriores à criação.

| Grupo | Atributos |
|---|---|
| Categóricos (vazio = "não informado") | tipo_item, projeto, modulo, complexidade, vertical, origem_bug, desenvolvedor, analista_requisitos |
| Ordinais / binários | prioridade_ord, complexidade_ord, eh_subtarefa, vinculada_epic |
| Título | titulo_caracteres, titulo_palavras |
| Calendário | mes_criacao, dia_semana_criacao, hora_criacao |
| Contexto histórico | carga_dev_abertas e backlog_projeto_abertas (tasks abertas criadas nos 90 dias anteriores), dev_tasks_concluidas_antes, dev_lead_time_mediano_passado, tipo_lead_time_mediano_passado |

Fora do modelo: Analista de Teste, Story Points - Dev, Tempo gasto, histórico de status, Sprint, quantidade de subtarefas incorporadas e Descrição.

Script: [pipeline_tcc/03_atributos.py](pipeline_tcc/03_atributos.py)

---

### Etapa 12 — Treinamento e comparação dos modelos

Data: 2026-11-03

Configuração:

- divisão temporal 80/20: treino com 3.981 tasks (01/08/2024 a 28/01/2026), teste com 996 tasks (28/01/2026 a 21/09/2026);
- busca em grade com validação walk-forward (`TimeSeriesSplit`, 5 blocos) no treino, critério MAE;
- alvo treinado em `log1p(lead_time_horas)`, previsões convertidas para horas;
- one-hot nos categóricos (CatBoost com categorias nativas); `random_state = 42`;
- baseline da proposta: média do treino por Tipo de item × Complexidade; adicionalmente, a mediana pelos mesmos grupos.

Resultados reais no conjunto de teste:

| Modelo | MAE (h) | RMSE (h) | R² | MdAE (h) | MAE teste ≥90 dias (h) |
|---|---|---|---|---|---|
| Baseline — média | 766 | 971 | −0,068 | 645 | 771 |
| Baseline — mediana | 567 | 941 | −0,003 | 297 | 690 |
| Gradient Boosting | 530 | 925 | 0,030 | 229 | 655 |
| Random Forest | 515 | 913 | 0,056 | 229 | 645 |
| XGBoost | 513 | 910 | 0,062 | 220 | 647 |
| **LightGBM** | **507** | 909 | 0,063 | **206** | 642 |
| CatBoost | 509 | **906** | **0,070** | 224 | **638** |

Conclusões:

- todos os modelos superam os baselines; o LightGBM tem o menor MAE (507 h ≈ 21 dias), 34% abaixo do baseline pela média e 11% abaixo do baseline pela mediana;
- LightGBM, CatBoost, XGBoost e Random Forest ficam praticamente empatados (diferença < 8 h de MAE);
- **R² baixo (até 0,07)**: os atributos disponíveis na criação explicam pouco da variação do lead time, que inclui filas, esperas e dependências não registradas — limitação a registrar na monografia;
- erro mais realista: cerca de 640 h nas tasks do teste com pelo menos 90 dias de observação;
- atributos mais influentes (importância por permutação): experiência do desenvolvedor, tipo de item, vertical, prioridade e lead time mediano passado do desenvolvedor;
- modelo final: **LightGBM** (learning_rate 0,03; num_leaves 15; n_estimators 300), salvo em `pipeline_tcc/modelo_final.joblib` com a lista de atributos usados.

Script: [pipeline_tcc/04_treino.py](pipeline_tcc/04_treino.py) — detalhes em [reports/Relatorio_Atributos_e_Treinamento.docx](reports/Relatorio_Atributos_e_Treinamento.docx).

Observação: os scripts desta etapa foram desenvolvidos fora da estrutura `src/` e trabalham sobre a base com nomes reais. A migração para `src/` e para a base anonimizada está entre os próximos passos.

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

Os passos 1 a 6 do planejamento original (pipeline de dados, cálculo e validação do lead time, engenharia de atributos, preparação dos dados, treinamento, comparação e seleção do modelo) foram executados nas etapas 7 a 12. Restam os passos abaixo, em ordem de prioridade.

### Passo 1 — Proteger os dados sensíveis no repositório

Objetivo:

- cumprir a Regra 9 antes de qualquer commit.

Tarefas:

- criar um `.gitignore` que exclua `data/processed/Base_Final_Lead_Time.xlsx`, `pipeline_tcc/modelo_final.joblib`, os exports do Jira (`*.csv` brutos) e os arquivos `.pkl` intermediários;
- conferir com `git status` que nenhum desses arquivos está rastreado.

---

### Passo 2 — Migrar o pipeline para `src/` e para a base anonimizada

Objetivo:

- cumprir as Regras 5 e 9, mantendo os resultados reproduzíveis.

Tarefas:

- distribuir a lógica de `pipeline_tcc/` nos módulos existentes: tratamento em `src/data/data_pipeline.py`, regra de subtarefas e lead time em `src/features/lead_time_calculation.py`, atributos em `src/features/`, treinamento em `src/models/`, métricas e importância em `src/evaluation/`;
- aplicar `src/data/anonymize_data.py` sobre a base da 5ª extração (desenvolvedores e analistas como `DEV_001`, `ANALISTA_001` etc.) antes do treinamento;
- retreinar e confirmar que as métricas não mudam (a anonimização só troca rótulos);
- transformar as verificações de `02_validacao.py` em testes em `tests/`.

---

### Passo 3 — Script de consulta sob demanda (inferência)

Objetivo:

- cumprir o sétimo objetivo específico: prever o lead time de uma task nova informada pelo gerente.

Tarefas:

- criar script de linha de comando que receba os dados da task (tipo, projeto, prioridade, módulo, complexidade, vertical, origem bug, desenvolvedor, analista de requisitos, título);
- calcular os atributos de contexto (experiência, carga e medianas passadas do desenvolvedor) a partir de uma extração recente do Jira;
- carregar o modelo salvo e devolver o lead time estimado em horas e dias;
- permitir simular a mesma task com desenvolvedores diferentes, apoiando a alocação.

---

### Passo 4 — Refinar o modelo (opcional)

Tarefas:

- obter a data aproximada de início do uso de IA pela equipe e incluir o atributo binário "período com IA";
- retirar atributos de contribuição nula ou negativa (tamanho do título, mês de criação, carga do desenvolvedor, complexidade categórica);
- testar palavras-chave do título como atributos textuais, já que a Descrição não pode ser usada;
- retreinar e comparar com os resultados da Etapa 12.

---

### Passo 5 — Documentação e apresentação do estudo

Tarefas:

- levar resultados, figuras e limitações para o capítulo de resultados da monografia;
- registrar as limitações: baixo poder explicativo dos atributos disponíveis na criação, preenchimento parcial de Complexidade e Módulo, ruído do alvo (fechamentos em lote) e viés das tasks recentes ainda abertas;
- preparar o material de apresentação para a banca.

---

## 8. Situação atual

Status do projeto em 2026-11-03:

- [x] análise do escopo e requisitos do TCC;
- [x] leitura da especificação técnica do projeto;
- [x] definição das regras de integridade metodológica;
- [x] criação da estrutura inicial do repositório;
- [x] coleta e organização da base extraída do Jira;
- [x] registro do processo documental da coleta e tratamento;
- [x] implementação do pipeline inicial de validação e preparação da base;
- [x] anonimização de nomes e situações sensíveis (base anterior);
- [x] implementação do cálculo do lead time na base anonimizada;
- [x] ampliação da base com a 5ª extração (26 meses, 4.977 linhas);
- [x] tratamento de subtarefas por desenvolvedor;
- [x] validação executada do cálculo do lead time na tabela final;
- [x] engenharia de atributos;
- [x] treinamento dos modelos;
- [x] comparação de desempenho;
- [x] persistência do modelo vencedor (LightGBM);
- [ ] proteção dos dados sensíveis no repositório (`.gitignore`);
- [ ] migração do pipeline para `src/` e para a base anonimizada;
- [ ] inferência para nova task (script de consulta sob demanda);
- [ ] refinamento do modelo (opcional);
- [ ] redação dos resultados na monografia.

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

O próximo registro deverá incluir:

- a criação do `.gitignore` e a conferência dos arquivos rastreados;
- os módulos migrados para `src/` e os testes criados em `tests/`;
- a confirmação das métricas após o retreino com a base anonimizada;
- o script de consulta sob demanda e exemplos reais de uso;
- eventuais ajustes do modelo (atributo de uso de IA, remoção de atributos) e seus resultados.
