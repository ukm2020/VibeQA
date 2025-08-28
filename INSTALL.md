# Installation Guide

## Prerequisites

1. **Python 3.8 or higher** - Download from [python.org](https://python.org/downloads/)
2. **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/api-keys)

## Quick Install

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Set your API key (Windows)
set OPENAI_API_KEY=your-api-key-here

# 2. Set your API key (Mac/Linux)
export OPENAI_API_KEY=your-api-key-here

# 3. Verify installation
python verify_setup.py

# 4. Run demo
python demo.py
```

## Manual Testing (without API key)

```bash
# Run unit tests
python run_tests.py

# Test CLI import
python -c "from src.cli import main; print('CLI import successful')"

# Test core components
python -c "from src.core import create_engine; print('Core import successful')"
```

## Usage Examples

```bash
# Generate Rainforest test
python -m src.cli "Login with valid credentials" --framework rainforest --base-url https://example.com

# Generate Cypress test
python -m src.cli "User adds item to cart" --framework cypress --tags "e2e,cart"

# Generate Gherkin feature
python -m src.cli "Password reset flow" --framework gherkin --out password-reset.feature
```

## Troubleshooting

### Python Not Found
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### API Key Issues
```bash
# Check if key is set (Windows)
echo %OPENAI_API_KEY%

# Check if key is set (Mac/Linux)
echo $OPENAI_API_KEY
```

## Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest --cov=src tests/

# Format code
black src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
vibeqa-generator/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   ├── frameworks/        # Framework adapters
│   ├── utils/             # Utilities
│   └── cli.py            # Command-line interface
├── tests/                 # Unit tests
├── examples/              # Sample scenarios and outputs
├── prompts/               # LLM prompt templates
├── logs/                  # Execution logs (created at runtime)
├── demo.py               # 90-second demo script
├── verify_setup.py       # Setup verification
└── run_tests.py          # Test runner
```

