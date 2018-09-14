DROP TABLE IF EXISTS books CASCADE;

CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  isbn VARCHAR,
  title VARCHAR,
  author VARCHAR,
  year VARCHAR
);

DROP TABLE IF EXISTS reviews CASCADE;

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  book_id INTEGER,
  user_id INTEGER,
  stars INTEGER,
  review TEXT NULL
);

DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR,
  password VARCHAR
);
