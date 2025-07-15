# GitHub Repo Documentation Generator

This tool automates the process of generating technical documentation and architecture diagrams for any GitHub repository using a local or cloud LLM (OpenAI or Ollama).

## Features

- Clones a GitHub repository
- Traverses and filters relevant source files (multi-language support)
- Generates per-component and overall documentation using OpenAI or Ollama
- Produces architecture and flow diagrams (optionally Mermaid)
- Fast, parallel processing
- Pluggable LLM backend (OpenAI or Ollama)

## Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python main.py <github_repo_url>`

### LLM Backend Configuration

- **Ollama (default, local):**
  - Start Ollama and pull your desired model (e.g., `ollama pull llama3`)
  - Optionally set environment variables:
    - `LLM_BACKEND=ollama`
    - `LLM_MODEL=llama3`
    - `OLLAMA_URL=http://localhost:11434/api/generate`
- **OpenAI (cloud):**
  - Set environment variables:
    - `LLM_BACKEND=openai`
    - `LLM_MODEL=gpt-4o` (or your preferred model)
    - `OPENAI_API_KEY=your-key-here`

## Requirements

- Python 3.8+
- For OpenAI: OpenAI API key
- For Ollama: Ollama running locally with your model pulled

## Output

- `docs/COMPONENTS.md`: Per-component documentation
- `docs/ARCHITECTURE.md`: Overall architecture and flow
