# cyclebot

A playground for LLM agents

## Features

- Modern Python project structure
- Comprehensive testing with pytest and coverage reporting
- Code quality tools (Ruff for linting/formatting, MyPy for type checking)
- Pre-commit hooks for automated quality checks
- GitHub Actions CI/CD pipeline
- VS Code tasks integration

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/cyclebot.git
cd cyclebot
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the project in development mode:

```bash
# Using Make (recommended)
make install

# Or using UV (fastest)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

4. Install pre-commit hooks:

```bash
pre-commit install
```

## Development

### Available Commands

```bash
# Using Make (recommended)
make help         # Show all available commands
make test         # Run tests with coverage
make lint         # Run linting
make format       # Format code
make type-check   # Run type checking
make docs         # Build documentation
make all          # Run all checks

# Or run tools directly
pytest --cov=. --cov-report=term-missing --cov-fail-under=80 --cov-report=html
ruff format .     # Format code
ruff check .      # Lint code
mypy .           # Run type checking
mkdocs serve     # Serve documentation locally
pre-commit run --all-files  # Run all checks
```

### VS Code Integration

This project includes VS Code tasks for common operations:

- `Ctrl+Shift+P` -> "Tasks: Run Task" to see all available tasks
- Install the "Task Explorer" extension for a better task management experience

## Browser Automation with Playwright MCP

This project uses Playwright MCP for browser automation with persistent login sessions.

### Setup Persistent Chrome Profile

1. **Configure Playwright MCP server** with a persistent Chrome profile:

```bash
claude mcp add --transport stdio playwright -s user -- \
  npx -y @playwright/mcp@latest \
  --browser chrome \
  --user-data-dir /home/YOUR_USERNAME/.config/cyclebot/chrome-profile-tradingview \
  --no-sandbox
```

2. **Login to websites** using the provided launcher script:

```bash
./launch-chrome-profile.sh tradingview
# Navigate to your website and login
# Close Chrome when done
```

3. **Run your automation script** - it will reuse the saved login session:

```bash
python src/cyclebot/hello.py
```

### Important: Linux Cookie Encryption Issue

**Problem**: On Linux, Chrome uses the system keyring (v11 encryption) to encrypt cookies by default. When Playwright launches Chrome, it doesn't have access to the same keyring, causing it to corrupt the cookie database when trying to read/write cookies.

**Solution**: The `launch-chrome-profile.sh` script uses `--password-store=basic` to force Chrome to use simple cookie encryption (v10) that doesn't require the system keyring. This ensures both manual Chrome sessions and Playwright-launched sessions can read/write the same cookies without corruption.

**Key takeaway**: Always use `--password-store=basic` when creating Chrome profiles that will be shared between manual browsing and Playwright automation on Linux.

## Project Structure

```
cyclebot/
├── src/cyclebot/                   # Main package
│   ├── hello.py                    # Demo script with Playwright
│   └── web.py                      # FastAPI web interface
├── tests/                          # Test suite
├── launch-chrome-profile.sh        # Helper script to launch Chrome with profile
├── .github/workflows/              # GitHub Actions
├── .vscode/                        # VS Code configuration
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## Contributing

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/amazing-feature`
1. Make your changes and run the quality checks
1. Commit your changes: `git commit -m 'Add amazing feature'`
1. Push to the branch: `git push origin feature/amazing-feature`
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Seth Lakowske - lakowske@gmail.com
