# Examples

Outputs from running `engine/generate_sql.py` against the seeded `text-to-sql`
database (100 rows each in `members`, `accounts`, `transactions`), using the
`llama3.2` model via Ollama.

Schema recap:

```
members(member_id, member_name, open_date)
accounts(account_id, member_id, account_type, balance)
transactions(transaction_id, account_id, amount, transaction_date, transaction_type)
```

## Works well: single table, filters and aggregates

**Q: Show all transactions greater than 5000 dollars.**

```sql
SELECT t.transaction_id, t.amount, t.transaction_date, t.transaction_type
FROM transactions t
WHERE t.amount > 5000
```

Result: 97 rows, correct.

**Q: What is the average transaction amount by transaction type?**

```sql
SELECT AVG(amount), transaction_type
FROM transactions
GROUP BY transaction_type
```

Result: 10 rows, one per transaction type, correct.

**Q: What is the total balance and name of the member with member id = 1?**

```sql
SELECT SUM(balance), (SELECT member_name FROM members WHERE member_id = 1)
FROM accounts
```

Result: `(4819582.88, 'Jamie Olsen')`, correct, though the model reached for
a scalar subquery instead of a `WHERE member_id = 1` filter on a joined
`accounts`/`members`. Works, but not how a human would write it.

## Works sometimes: joins

**Q: How many transactions happened on each account, joined with the member name?**

```sql
SELECT T1.account_id, T2.member_name, COUNT(T3.transaction_id)
FROM accounts AS T1
INNER JOIN members AS T2 ON T1.member_id = T2.member_id
INNER JOIN transactions AS T3 ON T1.account_id = T3.account_id
GROUP BY T1.account_id, T2.member_name
```

Result: 60 rows, correct: a clean three-table join with proper aliasing and
`GROUP BY`.

## Fails: joins

**Q: List the top 5 members by total account balance.**

```sql
SELECT T2.member_name, SUM(T3.balance) AS total_balance
FROM members T1
INNER JOIN accounts T2 ON T1.member_id = T2.member_id
INNER JOIN transactions T3 ON T2.account_id = T3.account_id
GROUP BY T2.member_id
ORDER BY SUM(T3.balance) DESC
LIMIT 5;
```

```
QUERY ERROR: column t2.member_name does not exist
LINE 1: SELECT T2.member_name, SUM(T3.balance) AS total_balance FROM...
               ^
HINT:  Perhaps you meant to reference the column "t1.member_name".
```

The model mixed up its own aliases: `T2` is `accounts` (no `member_name`
column), `T1` is `members` (has it). It also joined in `transactions` and
summed `balance` from the wrong table entirely — the question needed no join
past `accounts` at all.

**Q: What is the name of the member who made the largest deposit, and how much was it?**

```sql
SELECT T2.member_name, MAX(T1.amount)
FROM transactions AS T1
INNER JOIN accounts AS T2 ON T1.account_id = T2.account_id
GROUP BY T2.member_id
```

```
QUERY ERROR: column t2.member_name does not exist
LINE 1: SELECT T2.member_name, MAX(T1.amount) FROM transactions AS T...
               ^
```

Same failure mode: `T2` here is `accounts`, which has no `member_name`. That
column lives on `members`, a table the query never joins in. A correct
version needs a second join (`accounts` to `members`) that the model dropped.

**Q: How many accounts does each member have?**

```sql
SELECT COUNT(DISTINCT T1.member_id)
FROM accounts AS T1
JOIN members AS T2 ON T1.member_id = T2.member_id
GROUP BY T1.member_id
```

Runs without error, but is silently wrong: it returns a single row
(`62`, the count of distinct members with an account) instead of one row per
member with their per-member account count. No `GROUP BY` in the version
actually executed by the model, and the aggregate collapses everything into
one number. This is arguably worse than the errors above — it looks like a
valid answer.

See [README.md](README.md) for the full list of known limitations.
