# Sangin Promotion Quiz Platform

This repository provides a FastAPI backend that implements the core requirements of the internal photo-based quiz platform described in the PRD/TRD. The service exposes endpoints for employee quiz participation and administrator management actions such as image uploads, score threshold configuration, result exports, and retest approval.

## Project Structure

```
backend/
  app/
    api/
      routes/            # FastAPI routers for auth, quiz, and admin features
      deps.py            # Shared dependency utilities (auth, DB sessions)
    core/                # Application configuration and security helpers
    db/                  # SQLAlchemy session management and metadata helpers
    models/              # ORM models representing users, images, sessions, settings
    schemas/             # Pydantic schemas for request/response validation
    services/            # Domain services (quiz generation, scoring, etc.)
    main.py              # FastAPI application entrypoint
  requirements.txt       # Python dependencies
```

## Getting Started

1. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the API server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000` with interactive docs at `/docs`.

3. **Environment configuration (optional)**

   Create a `.env` file in the repository root (or export environment variables) to override defaults:

   ```env
   SECRET_KEY=change-me
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=supersecure
   DEFAULT_PASSING_SCORE=70
   DEFAULT_NUM_QUESTIONS=10
   DEFAULT_NUM_OPTIONS=10
   DATABASE_URL=sqlite:///./quiz.db
   ```

## Key Features

- Employee login with automatic account provisioning and JWT-based session tokens.
- Quiz generation that enforces non-reuse of images during an active session and supports retake gating.
- Automatic scoring with configurable passing thresholds and score persistence.
- Administrator endpoints for:
  - Managing quiz settings and image metadata.
  - Exporting results as CSV.
  - Resetting image usage flags and approving organization-wide retests.
- SQLite default persistence with SQLAlchemy models aligned to the TRD schema.

## Running Tests

Tests are not yet provided. You can validate the API manually via the interactive Swagger UI once the server is running.
