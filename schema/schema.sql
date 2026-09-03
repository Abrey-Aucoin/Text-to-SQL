CREATE TABLE members (
    member_id SERIAL PRIMARY KEY,
    member_name TEXT,
    open_date DATE
);

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    member_id INT REFERENCES members(member_id),
    account_type TEXT NOT NULL,
    balance DECIMAL NOT NULL
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES accounts(account_id),
    amount DECIMAL NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type TEXT NOT NULL
);