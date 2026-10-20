# 🏃‍♂️ Strava Activity Analyzer (Portfólio Application)

Documento de especificação de arquitetura, funcionalidades e roadmap de desenvolvimento para a aplicação de análise de dados de atividades do Strava.

---

## 🎯 1. Visão Geral do Projeto

A aplicação é uma plataforma Web desacoplada desenvolvida para gestão, visualização e análise de dados esportivos. O sistema permite o upload manual de arquivos `.csv` exportados da conta do Strava, fornecendo persistência local, interface gráfica para interações via CRUD, autenticação própria e um assistente inteligente (IA/LLM) capaz de responder perguntas contextuais sobre os dados de treinos.

### Objetivos de Aprendizado (Ponta a Ponta)

- **Back-end:** Desenvolvimento de API RESTful assíncrona, autenticação JWT, validações com Pydantic e ORM.
- **Front-end:** Construção de uma interface interativa (SPA ou dashboard) consumindo rotas protegidas.
- **Processamento de Dados:** Parsing, higienização e conversão de arquivos CSV em instâncias de banco de dados.
- **Integração com IA:** Implementação de retentores de contexto e chamadas de funções (*Function Calling* / *RAG*) para consultas sobre treinos em linguagem natural.
- **DevOps & Arquitetura:** Containerização com Docker, gerenciamento de dependências ultra-rápido com `uv` e estratégias de deploy em nuvem.

---



## 🏛️ 2. Arquitetura & Stack Tecnológica

- **Linguagem Base:** Python 3.12+
- **Gerenciador de Pacotes/Projetos:** `uv`
- **Back-end (API):** FastAPI + Uvicorn
- **Modelagem e Validação:** Pydantic / Pydantic Settings
- **Banco de Dados:** PostgreSQL
- **ORM:** SQLAlchemy (Assíncrono) ou SQLModel
- **Autenticação:** JWT (OAuth2 Password Flow na própria API)
- **Front-end:** Next.js
- **Ecossistema de IA:** LangChain / OpenAI API em PRD (Ollama para modelos locais em DEV)
- **Infraestrutura:** Docker & Docker Compose

---



## ⚙️ 3. Mapeamento de Funcionalidades (Features)



### Módulo 1: Autenticação e Gestão de Usuários

- **[Auth-01] Cadastro de Usuário:** Registro com e-mail, nome e senha criptografada (Argon2). SDD: [docs/sdd/AUTH-01.md](sdd/AUTH-01.md).
- **[Auth-02] Login / Emissão de Token:** Autenticação via `OAuth2PasswordBearer` gerando tokens JWT (*Bearer Tokens*).
- **[Auth-03] Proteção de Rotas:** Middleware de verificação de autenticação para garantia de acesso isolado aos dados de cada usuário.



### Módulo 2: Importação e Processamento do CSV

- **[CSV-01] Upload de Arquivo:** Endpoint seguro para upload de arquivos `.csv` exportados diretamente do Strava.
- **[CSV-02] Parsing e Validação de Dados:** 
  - Leitura e limpeza das colunas do CSV (ex: conversão de tipos de dados, tratamento de nulos).
  - Mapeamento para modelos Pydantic/SQLAlchemy (ID da atividade, Data, Nome, Tipo de Esporte, Distância, Tempo, Elevação, Frequência Cardíaca Média, etc.).
- **[CSV-03] Deduplicação:** Identificação e prevenção da inserção de atividades duplicadas enviadas em arquivos consecutivos.



### Módulo 3: Gerenciamento de Atividades (CRUD)

- **[CRUD-01] Visualização/Listagem (Read):** Consulta paginada com suporte a filtros por período, tipo de esporte e buscas por título.
- **[CRUD-02] Inclusão Manual (Create):** Criação de treinos manuais diretamente pela interface.
- **[CRUD-03] Edição (Update):** Atualização de métricas ou inclusão de notas pessoais em uma atividade existente.
- **[CRUD-04] Remoção (Delete):** Exclusão individual ou em lote de registros de atividades do banco de dados.



### Módulo 4: Visualização e Dashboard (Front-end)

- **[UI-01] Painel Consolidado:** Exibição de métricas gerais (distância total acumulada, tempo total em movimento, média de ritmo/pace).
- **[UI-02] Listagem e Tabelas:** Interface responsiva com ordenação e filtros dinâmicos.
- **[UI-03] Formulários Dinâmicos:** Interface para upload de arquivo CSV com progresso e modais de criação/edição.



### Módulo 5: Assistente de Inteligência Artificial (Chatbot)

- **[AI-01] Interface de Chat:** Painel interativo para envio de mensagens e dúvidas.
- **[AI-02] Agente / Function Calling:** Integração da LLM com o banco de dados do usuário (RAG ou execução de consultas SQL seguras para responder perguntas como *"Qual foi a minha maior corrida no mês passado?"* ou *"Qual minha média de batimentos em treinos de ciclismo?"*).

---



## 🗺️ 4. Roadmap de Desenvolvimento (Passo a Passo)

```
[Fase 1: Core API & Auth] ──> [Fase 2: Processador CSV] ──> [Fase 3: CRUD Assíncrono]
                                                                    │
[Fase 6: Deploy & DevOps] <── [Fase 5: Assistente IA] <── [Fase 4: Front-end UI]
```



### **Fase 1: Estruturação e Autenticação (Back-end Base)**

- [ ] Inicializar o projeto usando `uv init`.
- [ ] Configurar a dependência `fastapi[standard]`.
- [ ] Configurar o banco de dados PostgreSQL via Docker Compose.
- [ ] Implementar a estrutura de pastas modularizada (`routers/`, `services/`, `models/`, `schemas/`, `core/`).
- [ ] Criar tabela e modelo de Usuários.
- [ ] Criar rotas `/api/v1/auth/register` e `/api/v1/auth/login` com hash de senha e geração de JWT.



### **Fase 2: Modelagem de Dados e Ingestão do CSV**

- [ ] Definir o schema da tabela de **Atividades** (`activities`).
- [ ] Criar a rota POST `/api/v1/activities/upload-csv` recebendo `UploadFile`.
- [ ] Escrever o serviço de parsing (`services/csv_processor.py`) usando Pandas ou a biblioteca nativa `csv` do Python.
- [ ] Adicionar tratamentos para campos nulos e conversões de unidades de medida (ex: metros para km, segundos para minutos).



### **Fase 3: Endpoints CRUD de Atividades**

- [ ] `GET /api/v1/activities`: Listagem paginada e filtrada pertencente ao usuário autenticado.
- [ ] `POST /api/v1/activities`: Criação manual de treino.
- [ ] `PUT /api/v1/activities/{id}`: Atualização parcial/total de um treino.
- [ ] `DELETE /api/v1/activities/{id}`: Remoção de treino.
- [ ] Adicionar testes unitários e de integração utilizando Pytest.



### **Fase 4: Desenvolvimento da Interface Visual (Front-end)**

- [ ] Configurar o ambiente do front-end escolhido (ex: React/Vite ou Streamlit).
- [ ] Criar formulário de Login / Registro com armazenamento seguro de token JWT.
- [ ] Implementar a tela de upload de arquivos CSV.
- [ ] Construir a tabela de listagem de atividades com paginação e os componentes gráficos do Dashboard.
- [ ] Conectar os formulários aos endpoints de edição e remoção.



### **Fase 5: Integração com Inteligência Artificial (Chat LLM)**

- [ ] Configurar o SDK de LLM (OpenAI API ou LangChain).
- [ ] Desenvolver o serviço de consulta de contexto (`services/ai_service.py`).
- [ ] Definir as ferramentas (*Tools*) de consulta que a LLM usará para buscar no banco de dados.
- [ ] Criar o endpoint de WebSocket ou POST `/api/v1/chat` para streaming de respostas.
- [ ] Implementar o componente visual do Chat no Front-end.



### **Fase 6: Containerização, CI/CD e Deploy**

- [ ] Criar `Dockerfile` otimizado em multi-stage para a API FastAPI.
- [ ] Atualizar o `docker-compose.yml` para rodar API, Banco PostgreSQL e Front-end em conjunto.
- [ ] Criar uma pipeline no GitHub Actions para rodar testes e linters (`ruff check`).
- [ ] Realizar o deploy da aplicação em ambiente de produção (ex: Render, Railway, Fly.io).

---



