from collections import defaultdict

def get_schema_context(cursor) -> str:
    """
    Queries Postgres for table/column info and returns
    a formatted text block describing the schema.
    """
    
    #Query information_schema
    query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """
    cursor.execute(query)
    rows = cursor.fetchall() 
    
    #Group rows by table_name
    tables = defaultdict(list)
    for row in rows:
        table_name, column_name, data_type = row
        tables[table_name].append((column_name, data_type))
    
    # 3. Build the text block
    schema_text = ""
    for table_name, columns in tables.items():
        schema_text += f"Table: {table_name}\n"
        for column_name, data_type in columns:
            schema_text += f"  {column_name} ({data_type})\n"
        schema_text += "\n"
    schema_text += "Relationships:\n"
    schema_text += "- accounts.member_id references members.member_id (each account belongs to one member)\n"
    schema_text += "- transactions.account_id references accounts.account_id (each transaction belongs to one account)\n"
    
    return schema_text


#test connection and schema output
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from db import get_connection
    try:
        connection = get_connection()
        cursor = connection.cursor()
        print(get_schema_context(cursor))
        cursor.close()
    except Exception as error:
        print(f"error connecting to postgresql: {error}")   