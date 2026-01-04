# Notes API with Version History

A FastAPI-based backend for a note-taking application with version history.

## Features
- **User Authentication**: Register/Login with JWT.
- **Notes Management**: Create, Read, Update, Delete (CRUD) notes.
- **Version History**: Automatically saves versions on update.
- **Restore**: Restore a note to any previous version.

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (e.g., Neon, Supabase, or local)

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd notes-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file or set environment variables:

```ini
SQLALCHEMY_DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> **Note**: For local development, update `alembic.ini` `sqlalchemy.url` if running migrations manually, though `env.py` handles it if env vars are loaded.

### Database Migrations

Initialize the database schema:

```bash
alembic upgrade head
```

### Running the Server

```bash
uvicorn app.main:app --reload
```
Access API docs at: `http://localhost:8000/docs`

## Testing

Run the test suite (uses in-memory SQLite):

```bash
python -m pytest
```

## API Documentation

A Postman collection is included: `postman_collection.json`. Import it into Postman to test all endpoints.

## Deployment

### Render / Railway / Fly.io

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**: Set `SQLALCHEMY_DATABASE_URL` and `SECRET_KEY` in the dashboard.
4. **Migrations**: Add a build script or run `alembic upgrade head` as part of the start command.
   Example Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## License
MIT
