# F1 Database — Projeto Final SCC-541

Aplicação web para consulta e gerenciamento do banco de dados de Fórmula 1, desenvolvida como projeto final da disciplina **SCC-541 Laboratório de Bases de Dados** (ICMC-USP, 2026).

---

## Estrutura do projeto

```
ProjetoFinal/
├── sql/
│   ├── 01_users_tables.sql
│   ├── 02_populate_users.sql
│   ├── 03_triggers.sql
│   ├── 04_functions.sql
│   ├── 05_views.sql
│   └── 06_indexes.sql
├── app/
│   ├── db.py
│   ├── queries.py
│   ├── app.py
│   └── templates/
├── .env.example requirements.txt
└── README.md
```

---

## Pré-requisitos

- Python 3.10+
- Acesso ao banco PostgreSQL em `pgdb.icmc.usp.br` (fornecido pela disciplina)
- pip

---

## Configuração

**1. Clone o repositório**

```bash
git clone git@github.com:hrzanni/Formula1-database.git
cd Formula1-database
```

**2. Crie o arquivo `.env`** a partir do exemplo:

```bash
cp .env.example .env
```

Edite `.env` e preencha `DB_PASSWORD` com a senha do grupo:

```
DB_HOST=pgdb.icmc.usp.br
DB_NAME=scc541_g09_db
DB_USER=scc541_g09
DB_PASSWORD=<senha do grupo>
DB_PORT=5432
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

---

## Executar os scripts SQL (apenas uma vez)

Os scripts devem ser executados **em ordem** no banco remoto:

```bash
PGPASSWORD=<senha> psql -h pgdb.icmc.usp.br -U scc541_g09 -d scc541_g09_db \
  -f sql/01_users_tables.sql \
  -f sql/02_populate_users.sql \
  -f sql/03_triggers.sql \
  -f sql/04_functions.sql \
  -f sql/05_views.sql \
  -f sql/06_indexes.sql
```

> Se o banco já tiver sido configurado (tabelas USERS e USERS_LOG existentes), pule este passo — os scripts usam `IF NOT EXISTS` e `ON CONFLICT DO NOTHING` e são idempotentes.

---

## Rodar a aplicação

```bash
cd app
python3 app.py
```

Acesse **http://localhost:5000** no navegador.

---

## Logins de teste

| Perfil | Login | Senha |
|---|---|---|
| Administrador | `admin` | `admin` |
| Escuderia (McLaren) | `mclaren_c` | `mclaren` |
| Piloto (Hamilton) | `hamilton_d` | `hamilton` |

O padrão geral:
- Escuderia → `<constructor_ref>_c` / `<constructor_ref>`
- Piloto → `<driver_ref>_d` / `<driver_ref>`

---

## Funcionalidades

**Administrador**
- Dashboard com totais (pilotos, escuderias, temporadas), corridas recentes e classificações da temporada
- Cadastrar novas escuderias e pilotos (trigger cria o login automaticamente)
- Relatórios: R1 (resultados por status), R2 (aeroportos brasileiros por proximidade), R3 (hierárquico de circuitos)

**Escuderia**
- Dashboard com vitórias, pilotos distintos e anos em atividade
- Buscar piloto por sobrenome
- Importar pilotos em lote via CSV (`driver_ref, given_name, family_name, date_of_birth, nationality`)
- Relatórios: R4 (pilotos e vitórias), R5 (resultados por status)

**Piloto**
- Dashboard com desempenho detalhado por ano e circuito
- Relatórios: R6 (pontos por ano), R7 (resultados por status)

---

## Objetos SQL criados

| Tipo | Nome | Descrição |
|---|---|---|
| Tabela | `USERS` | Autenticação dos três perfis |
| Tabela | `USERS_LOG` | Auditoria de login/logout |
| Trigger | `TR_Constructors_User` | Cria usuário ao inserir escuderia |
| Trigger | `TR_Drivers_User` | Cria usuário ao inserir piloto |
| Function | `fn_vitorias_escuderia` | Total de vitórias da escuderia |
| Function | `fn_pilotos_escuderia` | Pilotos distintos da escuderia |
| Function | `fn_anos_escuderia` | Primeiro e último ano da escuderia |
| Function | `fn_anos_piloto` | Primeiro e último ano do piloto |
| Function | `fn_desempenho_piloto` | Desempenho por ano e circuito |
| View | `vw_resultados_por_status` | Resultados agrupados por status |
| View | `vw_temporada_mais_recente` | Ano da temporada mais recente |
| Índice | `idx_users_login` | Autenticação por login |
| Índice | `idx_results_constructor_id` | Filtro de resultados por escuderia |
| Índice | `idx_results_driver_id` | Filtro de resultados por piloto |
| Índice | `idx_airports_city_id` | JOIN aeroportos → cidades (R2) |
| Índice | `idx_airports_type_id` | Filtro por tipo de aeroporto (R2) |
| Índice | `idx_cities_country_id` | Filtro de cidades brasileiras (R2) |

---

## Tecnologias

- **Backend:** Python 3 + Flask 3
- **Banco de dados:** PostgreSQL (psycopg2-binary)
- **Frontend:** HTML + Bootstrap 5 (CDN)
- **Configuração:** python-dotenv
