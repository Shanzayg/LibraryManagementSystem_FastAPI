# Library Management API

A backend for a small library, built with **FastAPI**, **PostgreSQL (Neon)**, **SQLAlchemy** and **Alembic**. Members can sign up, log in, browse books and borrow them. Librarians manage the books.

## Features

- Sign up and log in with email and password (passwords hashed with Argon2, login with JWT tokens)
- Two roles: `member` and `librarian`
- Books: create, read, update, delete, search and paginate
- Loans: borrow and return books, see your own loans, list overdue loans
- Business rules: no borrowing without copies left, a limit on active loans per user, one active loan per book per user
- Request timing and logging middleware, CORS, consistent JSON error messages
- Database changes tracked with Alembic migrations

## Tech stack

Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2, Alembic, PostgreSQL on Neon, Pydantic and pydantic-settings, PyJWT, pwdlib (Argon2), managed with [uv](https://docs.astral.sh/uv/).

## Setup

1. **Clone the project and open its folder**
   ```
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. **Install dependencies**
   ```
   uv sync
   ```
3. **Create your `.env` file** by copying the example:
   - Windows: `copy .env.example .env`
   - Mac/Linux: `cp .env.example .env`
4. **Fill in `.env`** (see the table below). Generate a secret key with:
   ```
   uv run python -c "import secrets; print(secrets.token_hex(32))"
   ```
5. **Create the database tables**
   ```
   uv run alembic upgrade head
   ```
6. **Run the app**
   ```
   uv run uvicorn app.main:app --reload
   ```
7. Open the interactive docs at http://127.0.0.1:8000/docs

## Environment variables

Set these in `.env`. Never commit `.env`; only `.env.example` is committed.

| Variable | Purpose | Example |
|---|---|---|
| `APP_NAME` | Title shown in the docs | `Library API` |
| `DEBUG` | Debug mode | `true` |
| `DATABASE_URL` | Neon connection string (must start with `postgresql+psycopg://`) | `postgresql+psycopg://user:pass@host/db?sslmode=require` |
| `SECRET_KEY` | Key used to sign login tokens | long random string |
| `ALGORITHM` | Token signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long a login lasts | `30` |
| `MAX_LOANS_PER_USER` | Borrow limit per user | `3` |
| `LOAN_DAYS` | Loan length in days | `14` |
| `ALLOWED_ORIGINS` | Comma-separated websites allowed by CORS | `http://localhost:3000` |

## Making a librarian

New users are always created as `member`. To promote someone, run this once in the Neon SQL Editor:

```sql
UPDATE users SET role = 'librarian' WHERE email = 'librarian@example.com';
```

## Using the API in Swagger

1. Create a user with `POST /api/v1/auth/signup`.
2. Click **Authorize** (top right), enter your email as `username` and your password, then click **Authorize**.
3. Try the endpoints below.

## Endpoints

All routes except `/health` are under `/api/v1`.

| Method | Path | Who can use it | Description |
|---|---|---|---|
| GET | `/health` | anyone | Health check |
| POST | `/api/v1/auth/signup` | anyone | Create a member account |
| POST | `/api/v1/auth/login` | anyone | Get a login token |
| GET | `/api/v1/users/me` | logged-in user | Your own profile |
| GET | `/api/v1/books` | anyone | List books. Filters: `title`, `author`, `available=true`, `skip`, `limit` |
| GET | `/api/v1/books/{book_id}` | anyone | One book |
| POST | `/api/v1/books` | librarian | Add a book |
| PUT | `/api/v1/books/{book_id}` | librarian | Replace a book (all fields) |
| PATCH | `/api/v1/books/{book_id}` | librarian | Update some fields |
| DELETE | `/api/v1/books/{book_id}` | librarian | Delete a book (not allowed if it has loans) |
| POST | `/api/v1/loans` | logged-in user | Borrow a book (`{"book_id": 1}`) |
| GET | `/api/v1/loans/me` | logged-in user | Your loans. Use `?active=true` for current ones |
| POST | `/api/v1/loans/{loan_id}/return` | borrower or librarian | Return a book |
| GET | `/api/v1/loans/overdue` | librarian | Loans past their due date |

## Rules and error codes

| Situation | Status |
|---|---|
| Book, user or loan not found | 404 |
| Duplicate ISBN or email, or already holding the same book | 409 |
| No copies left, borrow limit reached, loan already returned | 400 |
| Wrong email or password, missing or expired token | 401 |
| Member tries a librarian-only action | 403 |
| Invalid input (wrong type, too short, bad ISBN) | 422 |

Errors are returned as `{"detail": "message"}`.

## Project structure

```
app/
  main.py          app setup only
  config.py        settings read from .env
  database.py      engine, session, Base
  models.py        User, Book, Loan tables
  security.py      password hashing and JWT tokens
  dependencies.py  get_db, pagination, current user, role check
  middleware.py    timing, logging, CORS
  exceptions.py    custom errors and their handler
  schemas/         Pydantic models (book, user, loan, token)
  crud/            database functions (book, user, loan)
  routers/         API routes (auth, users, books, loans)
alembic/           database migrations
```

## Database migrations

After changing a model in `app/models.py`:

```
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

Always open the generated file in `alembic/versions/` and read it before applying it. Undo the last migration with `uv run alembic downgrade -1`.