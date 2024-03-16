CREATE TABLE tokens (
    token TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    FOREIGN KEY (email) REFERENCES users(email)
);

CREATE TABLE users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    firstname TEXT NOT NULL,
    familyname TEXT NOT NULL,
    gender TEXT NOT NULL,
    city TEXT,
    country TEXT
);

CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email TEXT NOT NULL,
    receiver_email TEXT NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (sender_email) REFERENCES users(email),
    FOREIGN KEY (receiver_email) REFERENCES users(email)
);