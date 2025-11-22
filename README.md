# Claim Agent MVP

**Cursor for insurance claims** - An agentic claim processing system where each claim is treated like a repository with files and generated artifacts.

## Overview

Claim Agent allows you to:
- Create and manage insurance claims
- Upload files (PDFs, text documents) to claims
- Use an AI agent (chat interface) to generate summaries, update files, and create artifacts
- Review proposed changes in a git-style diff view
- Accept or reject agent proposals

## Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript + Vite
- **Storage**: Local filesystem (designed for easy S3 swap)

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for PostgreSQL, optional)

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL if needed
```

4. Start PostgreSQL (using Docker):
```bash
docker-compose up -d postgres
```

5. Run migrations:
```bash
cd backend
alembic upgrade head
```

6. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Create `.env` file (optional, defaults are fine):
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Create a Claim**: Click "Create New Claim" and enter a title
2. **Upload Files**: Upload PDFs or text files to your claim
3. **Use the Agent**: Open the agent chat tab and type commands like:
   - "create a summary"
   - "update file"
4. **Review Proposals**: The agent will show diffs of proposed changes
5. **Accept Changes**: Click "Accept Changes" to apply proposals

## Development

### Backend Structure

```
backend/app/
├── core/          # Configuration, database, dependencies
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── routers/       # FastAPI route handlers
├── services/      # Business logic
└── storage/       # Storage abstraction
```

### Frontend Structure

```
frontend/src/
├── components/    # React components
├── services/      # API client
└── types/         # TypeScript types
```

## TODO / Future Enhancements

- [ ] Replace mock agent with real LLM integration (OpenAI/Bedrock)
- [ ] Improve PDF text extraction
- [ ] Add support for Word documents
- [ ] Add RAG/embeddings for semantic search
- [ ] Add file versioning
- [ ] Improve diff visualization
- [ ] Add authentication
- [ ] Add S3 storage support
- [ ] Add more artifact types (letters, forms, etc.)

## License

MIT

