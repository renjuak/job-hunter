# Job Hunter

A Python-based job hunting assistant with resume embedding and storage capabilities using OpenAI and Supabase.

## Features

- Resume text embedding using OpenAI's embedding API
- Data storage and retrieval using Supabase
- Structured data handling with Pydantic models
- Comprehensive testing setup with pytest

## Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)
- OpenAI API key
- Supabase project with service key

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-hunter
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your actual API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_KEY`: Your Supabase service key

5. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

## Project Structure

```
/job_hunter
  ├─ __init__.py
  ├─ resume/
  │    ├─ __init__.py
  │    └─ embed_resume.py        # embeds text via OpenAI and writes to Supabase
  ├─ storage/
  │    ├─ __init__.py
  │    └─ db.py                  # Supabase upsert helper
  └─ main.py                     # will orchestrate later
```

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run isort .
```

### Linting
```bash
poetry run flake8 .
```

## Usage

The project is currently in development. The main orchestration logic will be implemented in `main.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. 