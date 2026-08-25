O Claude Code deverá seguir obrigatoriamente estas regras:

Regra 1 — Não inventar dados

Nunca criar dados reais fictícios e apresentá-los como resultados do TCC.

Para desenvolvimento, poderá ser criado um dataset sintético claramente identificado como:

SAMPLE / MOCK DATA

Esse dataset não deverá ser utilizado para afirmar resultados científicos.

Regra 2 — Não inventar resultados

Valores de MAE, RMSE, R², feature importance ou redução percentual somente poderão ser apresentados após execução real dos experimentos.

Regra 3 — Preservar a separação temporal

Não substituir a divisão temporal por train/test aleatório sem autorização explícita.

Regra 4 — Evitar data leakage

Nenhuma variável derivada de informações posteriores à criação da task poderá entrar no modelo.

Regra 5 — Código modular

Evitar notebooks monolíticos como implementação principal.

A lógica deverá permanecer em src/.

Os notebooks deverão servir principalmente para exploração, documentação e apresentação dos experimentos.

Regra 6 — Reprodutibilidade

Sempre que houver aleatoriedade, utilizar random_state configurável.

Regra 7 — Explicabilidade

O sistema deverá registrar quais variáveis foram utilizadas pelo modelo.

Regra 8 — Simplicidade

Não adicionar funcionalidades que não sejam necessárias ao objetivo do TCC.

Não transformar o projeto em uma plataforma completa de gerenciamento de projetos.

Regra 9 — Dados sensíveis

Nunca adicionar ao GitHub:

nomes reais de desenvolvedores;
descrições reais contendo informações confidenciais;
credenciais;
tokens;
arquivos .env;
exports reais do Jira.