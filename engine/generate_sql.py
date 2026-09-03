import os
import requests

def generate_sql(question, schema_text, model=None):
    model = model or os.environ.get("OLLAMA_MODEL", "llama3.2")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    prompt = f"""You are a SQL query generator. Given the following PostgreSQL schema, write a single SQL query to answer the question.
Return ONLY the SQL query, with no explanation and no markdown code fences.

Important PostgreSQL rule: any non-aggregated column in the SELECT must also appear in the GROUP BY clause when using aggregate functions like SUM, COUNT, or AVG.

Schema:
{schema_text}

Question: {question}

SQL:"""

    response = requests.post(
        f"{ollama_host}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    result = response.json()

    return clean_sql(result["response"])

def clean_sql(raw_response):
    text = raw_response.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("sql\n", "", 1)  # in case it's ```sql specifically
    return text.strip()


#test generation
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    from db import get_connection
    from schema_context import get_schema_context
    try:
        connection = get_connection()
        cursor = connection.cursor()
        schema_text = get_schema_context(cursor)
        print(generate_sql("what is the total balance and name of the member with member id =1? ", schema_text))
        cursor.close()
        connection.close()
    except Exception as error:
        print(f"error connecting to postgresql: {error}")