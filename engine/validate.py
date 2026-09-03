import psycopg2

def is_valid_query(sql: str) -> bool:
    query = sql.strip()
    if not query:
        return False
    return query.upper().startswith("SELECT")