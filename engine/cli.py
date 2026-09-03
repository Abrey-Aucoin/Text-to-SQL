from dotenv import load_dotenv
from db import get_connection
from schema_context import get_schema_context
from generate_sql import generate_sql
from validate import is_valid_query

load_dotenv()

def main():
    connection = get_connection()
    cursor = connection.cursor()
    schema_text = get_schema_context(cursor)

    print("Text-to-SQL agent ready. Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ").strip()
        if question.lower() in ("exit", "quit"):
            break
        if not question:
            continue

        sql = generate_sql(question, schema_text)
        print(f"\nGenerated SQL:\n{sql}\n")

        if not is_valid_query(sql):
            print("Rejected: only SELECT queries are allowed.\n")
            continue

        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(row)
            else:
                print("No results.")
        except Exception as error:
            print(f"Query failed: {error}")
        print()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()