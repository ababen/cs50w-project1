DROP TABLE IF EXISTS books CASCADE;

CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  isbn INTEGER,
  title VARCHAR,
  author VARCHAR,
  year INTEGER
);

DROP TABLE IF EXISTS reviews CASCADE;

CREATE TABLE reviews (
  id SERIAL PRIMARY KEY,
  book_id INTEGER,
  user_id INTEGER,
  stars INTEGER,
  review TEXT NULL
);

INSERT INTO books (isbn, title, author, year)
VALUES ('0765317508','Aztec','Gary Jennings','1980');
