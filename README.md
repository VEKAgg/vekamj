# VEKA Bot

A modern, feature-rich Discord bot built with nextcord, featuring a modular architecture and best practices for scalability and maintainability.

[![CI](https://github.com/yourusername/veka-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/veka-bot/actions/workflows/ci.yml)
[![CD](https://github.com/yourusername/veka-bot/actions/workflows/cd.yml/badge.svg)](https://github.com/yourusername/veka-bot/actions/workflows/cd.yml)
[![codecov](https://codecov.io/gh/yourusername/veka-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/veka-bot)

## Features

- Modern async/await syntax
- Modular cog-based command system
- Comprehensive error handling and logging
- Configuration management using YAML and environment variables
- Database integration ready (MongoDB & Redis)
- Clean and maintainable project structure
- Modern Python tooling (pyproject.toml, black, isort, mypy)
- Docker support with multi-stage builds
- CI/CD with GitHub Actions

## Prerequisites

- Python 3.10 or higher
- MongoDB (optional)
- Redis (optional)
- Discord Bot Token
- Docker (optional, but recommended)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/veka-bot.git
cd veka-bot
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Discord bot token and other settings
```

3. Start the services:
```bash
docker compose up -d
```

### Manual Installation

1. Create and activate a conda environment:
```bash
conda create -n veka-bot python=3.10
conda activate veka-bot
```

2. Install dependencies:
```bash
# Install core dependencies
pip install .

# Install development dependencies (optional)
pip install ".[dev]"

# Install test dependencies (optional)
pip install ".[test]"
```

3. Set up environment variables and start the bot:
```bash
cp .env.example .env
# Edit .env with your settings
python main.py
```

## Development

### Code Style and Quality

The project uses several tools to maintain code quality:

- `black` for code formatting
- `isort` for import sorting
- `mypy` for static type checking
- `ruff` for fast linting

You can run these tools using:
```bash
# Format code
black .
isort .

# Type checking
mypy .

# Linting
ruff check .
```

### Pre-commit Hooks

Set up pre-commit hooks to automatically check code quality:
```bash
pre-commit install --install-hooks
```

### Running Tests

```bash
pytest
```

### Docker Development

For development with Docker:

1. Build the development image:
```bash
docker compose build
```

2. Run with development settings:
```bash
docker compose up
```

3. View logs:
```bash
docker compose logs -f bot
```

## Deployment

### Using GitHub Actions (Recommended)

1. Push a new tag to trigger deployment:
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. The CD pipeline will:
   - Build and push Docker image to GitHub Container Registry
   - Create a GitHub Release
   - Generate release notes

### Manual Deployment

1. Build the production image:
```bash
docker build -t veka-bot .
```

2. Run in production:
```bash
docker compose -f docker-compose.yml up -d
```

## Project Structure

```
veka-bot/
├── app/                    # Main application package
│   ├── core/              # Core bot functionality
│   ├── cogs/              # Command modules
│   ├── database/          # Database connections
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── tests/                 # Test suite
├── .github/               # GitHub Actions workflows
├── docs/                  # Documentation
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── pyproject.toml        # Project configuration
└── README.md            # Project documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes (using commitizen)
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 