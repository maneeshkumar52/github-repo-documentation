# GitHub Repo Documentation Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

CLI tool that clones any GitHub repository and auto-generates comprehensive documentation — including per-file docs, architecture diagrams, AST analysis, and dependency graphs — using OpenAI GPT and NetworkX.

## Architecture

```
GitHub Repo URL
        │
        ▼
┌──────────────────────────────────────────┐
│  main.py (CLI entry point)               │
│                                          │
│  Step 1 ──► repo_cloner.py             │──► git clone to temp dir
│  Step 2 ──► file_traverser.py          │──► Discover relevant files
│  Step 3 ──► Parallel processing        │──► ThreadPoolExecutor
│       ├── process_python_file()        │──► AST parsing per file
│       └── build_consolidated_ast_graph │──► NetworkX dependency graph
│  Step 4 ──► doc_generator.py           │──► GPT-powered per-file docs
│  Step 5 ──► architecture_builder.py    │──► Architecture overview doc
│  Step 6 ──► AST graph HTML             │──► Interactive visualization
└──────────────────────────────────────────┘
        │
        ▼
Output directory (docs + diagrams)
```

## Key Features

- **Auto-Cloning** — `repo_cloner.py` clones any public GitHub repo
- **Smart File Discovery** — `file_traverser.py` identifies relevant source files
- **AST Analysis** — Parses Python files into Abstract Syntax Trees, builds consolidated dependency graphs with NetworkX
- **AI Documentation** — `doc_generator.py` uses OpenAI GPT to generate per-file documentation
- **Architecture Docs** — `architecture_builder.py` generates high-level architecture overview
- **Interactive Graphs** — Consolidated AST graph rendered as interactive HTML
- **Parallel Processing** — `ThreadPoolExecutor` for concurrent file processing

## Usage

```bash
git clone https://github.com/maneeshkumar52/github-repo-documentation.git
cd github-repo-documentation
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Generate documentation for any repo
python main.py https://github.com/owner/repo
```

## Repository Structure

```
github-repo-documentation/
├── main.py                  # CLI entry point
├── repo_cloner.py           # Git clone operations
├── file_traverser.py        # File discovery + AST parsing
├── doc_generator.py         # GPT-powered documentation
├── architecture_builder.py  # Architecture overview generation
├── llm_client.py            # OpenAI API client
├── utils.py                 # Logging + output directory setup
└── requirements.txt
```

## Configuration

Set `OPENAI_API_KEY` in your environment or `.env` file.

## License

MIT
# GitHub Repo Documentation

Professional-grade repository documentation automation CLI project with modular processing stages and deterministic artifact generation.

## 1. Executive Overview

This repository provides:
- CLI-first execution model
- Modular pipeline components
- Deterministic output generation
- Configurable model backends

## 2. Architecture

```txt
CLI Entry
  |
  +--> Input Acquisition
  +--> Processing and Analysis Pipeline
  +--> Documentation and Artifact Generator
  +--> Output Storage (docs/, outputs/)
```

## 3. Repository Structure

```txt
github-repo-documentation/
  main.py
  core modules
  requirements.txt
  docs/ or outputs/
```

## 4. Prerequisites

- Python 3.10+
- pip 23+
- Git

## 5. Local Setup and Execution

```bash
git clone https://github.com/maneeshkumar52/github-repo-documentation.git
cd github-repo-documentation
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python main.py <args>
```

## 6. Validation

```bash
python3 -m compileall -q .
```

## 7. Troubleshooting

- Missing dependencies: reinstall requirements in active environment
- Input errors: verify required CLI arguments and source data

## 8. License

See LICENSE in this repository.
