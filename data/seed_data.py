import os
import random
import sys
from dotenv import load_dotenv
from faker import Faker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engine"))
from db import get_connection

load_dotenv()
fake = Faker()

try:
    connection = get_connection()
    # cursor = connection.cursor()

    # # for serial in range(1, 51):
    # #     member_name = fake.name()
    # #     open_date = fake.date()
    # #     sql = "INSERT INTO members (member_name, open_date) VALUES (%s, %s);"
    # #     cursor.execute(sql, (member_name, open_date))

    # cursor.execute("SELECT member_id FROM members")
    # member_ids = [row[0] for row in cursor.fetchall()]

    # for serial in range(1, 51):
    #     member_id = random.choice(member_ids)
    #     account_type = fake.random_element(elements=('Savings', 'Checking', 'Business'))
    #     balance = round(random.uniform(7.0, 100000.0), 2)
    #     sql = "INSERT INTO accounts (member_id, account_type, balance) VALUES (%s, %s, %s);"
    #     cursor.execute(sql, (member_id, account_type, balance))

    # cursor.execute("SELECT account_id FROM accounts")
    # account_ids = [row[0] for row in cursor.fetchall()]

    # for serial in range(1, 51):
    #     account_id = random.choice(account_ids)
    #     amount = round(random.uniform(7.0, 100000.0), 2)
    #     transaction_date = fake.date()
    #     transaction_type = fake.random_element(elements=('Deposit', 'Withdrawal', 'Transfer', 'ACH', 'Debit Card', 'ATM', 'Credit Card', 'Check', 'Fee', 'Interest'))
    #     sql = "INSERT INTO transactions (account_id, amount, transaction_date, transaction_type) VALUES (%s, %s, %s, %s);"
    #     cursor.execute(sql, (account_id, amount, transaction_date, transaction_type))

    # connection.commit()
    # cursor.close()
    connection.close()

except Exception as error:
    print(f"error connecting to postgresql: {error}")