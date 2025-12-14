# Deep Research API Comparison

Compare deep research capabilities between **Perplexity Sonar Deep Research** and **Google Gemini Deep Research** APIs.

## Features

- Run identical queries on both APIs
- Generates comprehensive research reports with citations
- Saves results as JSON and Markdown

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests python-dotenv google-genai

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
python run_deep_research.py
```

Results are saved to `research_results/`.

## API Documentation

- [Perplexity Deep Research API](docs/perplexity-deep-research-api.md)
- [Google Gemini Deep Research API](docs/google-gemini-deep-research-api.md)

## API Keys

| Provider | Get Key |
|----------|---------|
| Perplexity | [docs.perplexity.ai](https://docs.perplexity.ai) |
| Google Gemini | [ai.google.dev](https://ai.google.dev) |

## License

MIT
