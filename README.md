# Finance API

Uma API RESTful para gerenciamento financeiro pessoal, com funcionalidades de:

* **Registro e autenticação** de usuários via JWT em cookies.
* **CRUD de categorias**, **metas** e **transações**, incluindo parser de texto livre via Google Gemini.
* **Geração de insights** financeiros e chat com agente inteligente.
* **Exportação** de transações para **CSV** e **PDF**.
* **Relatórios** consolidados dos últimos 30 dias.
* **Health check**, documentação OpenAPI/Swagger e histórico de dados.

---

## Sumário

1. [Tecnologias](#tecnologias)
2. [Instalação](#instalação)
3. [Variáveis de ambiente](#variáveis-de-ambiente)
4. [Execução](#execução)
5. [Documentação e testes](#documentação-e-testes)
6. [Endpoints](#endpoints)

   * [Autenticação de usuários (`/user/users`)](#autenticação-de-usuários-userusers)
   * [Finanças (`/finances`)](#finanças-finances)
   * [Análise (`/analysis`)](#análise-analysis)
   * [Health Check (`/health/`)](#health-check-health)
7. [Funcionalidades Avançadas](#funcionalidades-avançadas)
8. [Próximos passos](#próximos-passos)

---

## Tecnologias

* **Django 5.2** + **Django REST Framework**
* **DRF Spectacular** para OpenAPI/Swagger
* **rest-framework-simplejwt** para JWT em cookies
* **django-health-check** para monitoramento
* **Google Gemini SDK** (`google-genai`) para NLP/IA
* **ReportLab** e **pandas** para geração de PDF/CSV
* **SQLite** (desenvolvimento) / **PostgreSQL** (produção)

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/finance.git
cd finance/backend

# Crie e ative virtualenv
python -m venv .venv
source .venv/bin/activate

# Instale dependências
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do backend com:

```dotenv
# Chave da API Google Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Django settings
DJANGO_SECRET_KEY=suachavesecreta
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

O `core/config.py` e o `settings.py` já leem essas variáveis via Pydantic e `os.environ`.

---

## Execução

```bash
# Gere as migrations e aplique no banco
python manage.py makemigrations
python manage.py migrate

# Crie um superusuário (opcional)
python manage.py createsuperuser

# Rode o servidor
python manage.py runserver
```

Para rodar via Docker Compose (com PostgreSQL):

```bash
docker-compose down --rmi all --volumes --remove-orphans
docker-compose up --build -d
```

---

## Documentação e testes

* **Swagger UI**: [`/api/docs/`](http://localhost:8000/api/docs/)
* **OpenAPI schema**: [`/api/schema/`](http://localhost:8000/api/schema/)
* **Health check**: [`/health/`](http://localhost:8000/health/)
* **Testes unitários**:

  ```bash
  python manage.py test user
  python manage.py test finances
  python manage.py test analysis
  ```

---

## Endpoints

> **Nota**: Todos os endpoints, exceto registro e login, requerem autenticação via JWT em cookie `access`.

### Autenticação de usuários (`/user/users`)

| Método | Rota         | Descrição                                   | Autorização |
| ------ | ------------ | ------------------------------------------- | ----------- |
| POST   | `/register/` | Cria novo usuário                           | Anônimo     |
| POST   | `/login/`    | Gera cookies `access` e `refresh`           | Anônimo     |
| POST   | `/refresh/`  | Renova token de acesso via cookie `refresh` | Anônimo     |
| POST   | `/logout/`   | Invalida `refresh` e limpa cookies          | Anônimo     |
| GET    | `/profile/`  | Retorna dados do usuário autenticado        | Usuário     |
| PUT    | `/update/`   | Atualiza dados do usuário                   | Usuário     |

### Finanças (`/finances`)

#### Categorias (`/categories`)

| Método | Rota                         | Descrição                   |
| ------ | ---------------------------- | --------------------------- |
| GET    | `/finances/categories/`      | Lista categorias do usuário |
| POST   | `/finances/categories/`      | Cria nova categoria         |
| GET    | `/finances/categories/{id}/` | Detalha categoria           |
| PUT    | `/finances/categories/{id}/` | Atualiza categoria          |
| PATCH  | `/finances/categories/{id}/` | Atualiza parcialmente       |
| DELETE | `/finances/categories/{id}/` | Remove categoria            |

#### Metas (`/goals`)

| Método | Rota                    | Descrição                   |
| ------ | ----------------------- | --------------------------- |
| GET    | `/finances/goals/`      | Lista metas do usuário      |
| POST   | `/finances/goals/`      | Cria meta (parser de texto) |
| GET    | `/finances/goals/{id}/` | Detalha meta                |
| PUT    | `/finances/goals/{id}/` | Atualiza meta               |
| PATCH  | `/finances/goals/{id}/` | Atualiza parcialmente       |
| DELETE | `/finances/goals/{id}/` | Remove meta                 |

#### Transações (`/transactions`)

| Método | Rota                                    | Descrição                              |
| ------ | --------------------------------------- | -------------------------------------- |
| GET    | `/finances/transactions/`               | Lista transações do usuário            |
| POST   | `/finances/transactions/`               | Cria transação (parser de texto livre) |
| GET    | `/finances/transactions/{id}/`          | Detalha transação                      |
| PUT    | `/finances/transactions/{id}/`          | Atualiza transação                     |
| PATCH  | `/finances/transactions/{id}/`          | Atualiza parcialmente                  |
| DELETE | `/finances/transactions/{id}/`          | Remove transação                       |
| GET    | `/finances/transactions/export_csv/`    | Download CSV de todas as transações    |
| GET    | `/finances/transactions/export_pdf/`    | Download PDF de transações             |
| GET    | `/finances/transactions/report_30days/` | JSON com resumo dos últimos 30 dias    |

### Análise (`/analysis`)

#### Chat de agente (`/chats`)

| Método | Rota                    | Descrição                                             |
| ------ | ----------------------- | ----------------------------------------------------- |
| GET    | `/analysis/chats/`      | Lista mensagens (user + agent)                        |
| POST   | `/analysis/chats/`      | Cria mensagem de usuário                              |
| POST   | `/analysis/chats/chat/` | Envia mensagem ao Gemini e retorna resposta do agente |
| GET    | `/analysis/chats/{id}/` | Detalha mensagem                                      |
| PUT    | `/analysis/chats/{id}/` | Atualiza mensagem                                     |
| PATCH  | `/analysis/chats/{id}/` | Atualiza parcialmente                                 |
| DELETE | `/analysis/chats/{id}/` | Remove mensagem                                       |

#### Insights (`/insights`)

| Método | Rota                                  | Descrição                                          |
| ------ | ------------------------------------- | -------------------------------------------------- |
| GET    | `/analysis/insights/`                 | Lista insights salvos                              |
| POST   | `/analysis/insights/generate/{type}/` | Gera novo insight (`summary`,`forecast`,`anomaly`) |
| GET    | `/analysis/insights/{id}/`            | Detalha insight                                    |

### Health Check (`/health/`)

Verifica:

* Cache
* Banco de dados
* Storage
* Conectividade com Google Gemini API

---

## Funcionalidades Avançadas

* **Parser de texto livre** para transações e metas via Google Gemini
* **Relatórios agendados** (CSV/PDF) com Celery ou cron
* **Análise de anomalias** e **forecast** financeiro
* **Histórico de conversas** e **versionamento** de dados (simple\_history)
* **Documentação** e **testes** cobrindo 100% dos serviços

---