# text-to-sql

A small local text-to-SQL prototype: it reads a Postgres schema, sends it plus
a plain-English question to a local Ollama model, and runs whatever `SELECT`
query comes back.

It works well for simple, single-table questions and gets noticeably shakier
on multi-table joins. See [examples.md](examples.md) for real input/output
pairs, including failures.

## How it works

1. `engine/schema_context.py` queries `information_schema.columns` for the
   `public` schema and formats it into a plain-text block, with a couple of
   hardcoded lines describing the foreign-key relationships between tables.
2. `engine/generate_sql.py` sends that schema text plus the user's question
   to a local Ollama model (`llama3.2` by default) via
   `POST {OLLAMA_HOST}/api/generate`, and strips markdown fences from the
   response.
3. `engine/validate.py` does one check before execution: the query must
   start with `SELECT`. It is not a full SQL sanitizer.
4. `engine/cli.py` ties it together into a REPL: connect to Postgres, loop
   asking for questions, generate SQL, validate, execute, print rows.
5. `engine/db.py` builds the Postgres connection from environment variables
   loaded from `.env`.

## Schema

The demo schema (`schema/schema.sql`) is a tiny banking model:

```
members(member_id, member_name, open_date)
accounts(account_id, member_id, account_type, balance)
transactions(transaction_id, account_id, amount, transaction_date, transaction_type)
```

`data/seed_data.py` uses Faker to generate sample rows (100 members, 100
accounts, 100 transactions in the current dev database).

## Setup

Prerequisites:
- Postgres running locally with a database for this project
- [Ollama](https://ollama.com) running locally with a model pulled, e.g.
  `ollama pull llama3.2`
- Python 3.13

Install dependencies:

```bash
pip install psycopg2-binary python-dotenv requests faker
```

Create a `.env` file in the project root (everything but `PGPASSWORD` is
optional and falls back to the defaults shown below):

```
PGHOST=127.0.0.1
PGPORT=5433
PGDATABASE=text-to-sql
PGUSER=postgres
PGPASSWORD=your_postgres_password

OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Load the schema and seed data:

```bash
psql -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -f schema/schema.sql
python data/seed_data.py
```

`seed_data.py`'s insert logic is currently commented out; uncomment it to
actually populate rows, or load your own data.

## Usage

```bash
python engine/cli.py
```

```
Text-to-SQL agent ready. Type 'exit' to quit.

Ask a question: Show all transactions greater than 5000 dollars.

Generated SQL:
SELECT t.transaction_id, t.amount, t.transaction_date, t.transaction_type
FROM transactions t WHERE t.amount > 5000

(97, Decimal('81985.22'), datetime.date(1975, 2, 5), 'Interest')
...
```

## Known limitations

- Joins are unreliable. With three-plus tables in play, the model frequently
  mixes up which alias refers to which table, or drops a join that's
  actually needed. Sometimes this raises a Postgres error; sometimes it
  silently returns a plausible-looking but wrong answer (e.g. collapsing a
  per-member breakdown into a single total). That's a limitation of running
  a small 3B-parameter local model, not of the prompt or schema logic. See
  [examples.md](examples.md) for concrete cases.
- Validation is minimal. `is_valid_query` only checks that the query starts
  with `SELECT`. It doesn't parse the SQL, so don't point this at untrusted
  input or a production database.
- No schema/data awareness beyond column names and types. The model doesn't
  see row samples or value distributions, which contributes to mistakes on
  questions that need semantic knowledge of the data.
