<div align="center">

# 📖 GitHub Repo Documentation Generator

**An AI-powered CLI tool that automatically generates comprehensive technical documentation for any public GitHub repository — including component docs, architecture overviews, Mermaid diagrams, and interactive AST visualizations.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT_4-412991?logo=openai&logoColor=white)](https://openai.com)
[![Ollama](https://img.shields.io/badge/Ollama-Llama3-000000)](https://ollama.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-AST_Graphs-orange)](https://networkx.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [Configuration](#-configuration-reference) · [Project Structure](#-project-structure) · [Design Decisions](#-design-decisions) · [Troubleshooting](#-troubleshooting)

</div>

---

## 🎯 What This Project Does

Given any public GitHub repository URL, this tool:

1. **Clones** the repository locally via GitPython
2. **Discovers** all relevant source files using configurable extension filters
3. **Parses** Python files into Abstract Syntax Trees (ASTs) via the `ast` module
4. **Generates interactive AST visualizations** as HTML/SVG using NetworkX + Graphviz
5. **Builds cross-file dependency graphs** showing function call relationships across modules
6. **Generates per-component documentation** by sending source code to an LLM (OpenAI GPT or local Ollama)
7. **Synthesizes architecture-level documentation** by aggregating all component summaries into a single LLM call
8. **Outputs everything** into a structured `docs/` directory

### The Problem It Solves

| Challenge | This Tool's Solution |
|---|---|
| Onboarding onto unfamiliar codebases takes days | Auto-generates component + architecture docs in minutes |
| Manual documentation is tedious and quickly outdated | One command produces comprehensive technical docs |
| Understanding cross-file dependencies is hard | Interactive AST graphs + consolidated dependency visualization |
| Legacy codebases lack any documentation | AI-powered analysis of every source file |
| Architecture overviews require deep understanding | LLM synthesizes high-level architecture from component docs |

### Key Differentiators

- **Dual LLM backend** — Switch between OpenAI GPT and local Ollama via environment variable
- **Visual AST graphs** — Interactive HTML/SVG visualizations for every Python file
- **Cross-file dependency analysis** — Two-pass algorithm resolves function calls across modules
- **Chunked processing** — Large files split into 4000-char chunks for LLM context limits
- **Parallel execution** — ThreadPoolExecutor (8 workers) for concurrent file processing

---

## ✨ Features

| Feature | Description | Output |
|---|---|---|
| Repository Cloning | Clone any public GitHub repo via URL | `cloned_repo/` directory |
| File Discovery | Configurable filters — 50+ extensions, directory exclusions | Filtered file list |
| Per-File AST Graphs | Interactive SVG visualizations of Python AST nodes | `docs/ast/*.ast.html` |
| Function Documentation | Extract signatures, arguments, docstrings from Python ASTs | `docs/ast/*.md` |
| Consolidated Dependency Graph | Cross-file function call resolution across all Python modules | `docs/CONSOLIDATED_AST.html` |
| AI Component Documentation | LLM-generated technical docs for every source file | `docs/COMPONENTS.md` |
| AI Architecture Overview | High-level architecture synthesis with optional Mermaid diagram | `docs/ARCHITECTURE.md` |
| OpenAI Support | GPT-4, GPT-3.5-turbo, or any OpenAI model | Via `OPENAI_API_KEY` |
| Ollama Support | Local Llama3, Mistral, or any Ollama model | Via `OLLAMA_URL` |
| Parallel Processing | 8-thread concurrent file analysis | Faster processing |

---

## 🏗 Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     main.py (CLI Entry Point)                    │
│                                                                  │
│  sys.argv[1] = GitHub Repository URL                             │
│                                                                  │
│  Pipeline Steps:                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Step 1: utils.setup_logging() + ensure_output_dirs()     │    │
│  │ Step 2: repo_cloner.clone_repo(url) → local path         │    │
│  │ Step 3: file_traverser.get_relevant_files(path) → files  │    │
│  │ Step 4: ThreadPool(8) → AST graphs per .py file          │    │
│  │ Step 5: build_consolidated_ast_graph() → dependency map   │    │
│  │ Step 6: doc_generator.generate_component_docs() → LLM    │    │
│  │ Step 7: architecture_builder.generate_architecture_docs() │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Module Dependency Map

```
main.py
  ├── repo_cloner.py ─────────── GitPython (git.Repo.clone_from)
  │
  ├── file_traverser.py ──────── ast (stdlib), NetworkX, pydot
  │   ├── os.walk() file discovery
  │   ├── ast.parse() per Python file
  │   ├── NetworkX DiGraph construction
  │   └── pydot SVG rendering
  │
  ├── doc_generator.py
  │   ├── llm_client.py ──────── OpenAI SDK / requests (Ollama)
  │   └── utils.py ───────────── chunk_file(), save_markdown()
  │
  └── architecture_builder.py
      ├── llm_client.py
      └── utils.py
```

### Data Flow — Complete Pipeline

```
GitHub URL (e.g., https://github.com/user/repo)
        │
        ▼
repo_cloner.clone_repo()
        │  uses: gitpython → git.Repo.clone_from()
        │  if exists: shutil.rmtree() first
        │  output: cloned_repo/ directory
        │
        ▼
file_traverser.get_relevant_files()
        │  os.walk() → filter EXCLUDE_DIRS
        │  per file → check is_relevant_file():
        │    ├── not in EXCLUDE_FILES patterns
        │    └── extension in INCLUDE_EXTS (50+ extensions)
        │  output: List[str] of file paths
        │
        ▼
┌───────────────────────────────────────────┐
│  ThreadPoolExecutor(max_workers=8)         │
│                                            │
│  For each .py file:                        │
│  ├── ast.parse(source_code)                │
│  ├── build_ast_graph() → NetworkX DiGraph  │
│  │   └── Nodes: FunctionDef, ClassDef,     │
│  │       Import, Assign, etc.              │
│  │   └── Edges: parent → child             │
│  ├── save_ast_graph_html()                 │
│  │   └── pydot → SVG → HTML wrapper        │
│  │   └── output: docs/ast/{name}.ast.html  │
│  └── extract_function_docs()               │
│      └── Walk AST for FunctionDef nodes    │
│      └── Extract: name, args, docstrings   │
│      └── output: docs/ast/{name}.md        │
└───────────────────────────────────────────┘
        │
        ▼
build_consolidated_ast_graph(all_py_files)
        │
        │  Pass 1 — Collect function definitions:
        │  ├── Parse each file's AST
        │  ├── Walk for FunctionDef nodes
        │  └── Map: function_name → defining_file
        │
        │  Pass 2 — Resolve cross-file calls:
        │  ├── Walk for ast.Call nodes
        │  ├── Extract callee name from:
        │  │   ├── ast.Name → direct call
        │  │   └── ast.Attribute → method call
        │  ├── Lookup callee in function map
        │  └── Add edge: caller_file → callee_file
        │
        │  output: NetworkX DiGraph (cross-file dependencies)
        │
        ▼
save_consolidated_ast_graph_html()
        │  pydot → SVG → docs/CONSOLIDATED_AST.html
        │
        ▼
doc_generator.generate_component_docs(files)
        │
        │  ThreadPoolExecutor(max_workers=8)
        │  For each file:
        │  ├── Read source code
        │  ├── chunk_file(content, max_size=4000)
        │  ├── For each chunk → LLM prompt:
        │  │   "You are a senior software architect.
        │  │    Analyze the following code and generate
        │  │    detailed technical documentation..."
        │  ├── Join chunk responses
        │  └── Collect: {filename: documentation}
        │
        │  output: docs/COMPONENTS.md
        │
        ▼
architecture_builder.generate_architecture_docs()
        │
        │  Concatenate ALL component doc summaries
        │  Single LLM call (max_tokens=4096):
        │  "You are a senior software architect.
        │   Given the following component documentation,
        │   generate: overall technical documentation,
        │   high-level architecture, detailed flow,
        │   optionally a mermaid diagram..."
        │
        │  output: docs/ARCHITECTURE.md
        │
        ▼
Complete! All outputs in docs/ directory
```

### Output Structure

```
docs/
├── ARCHITECTURE.md           # AI-generated architecture overview + Mermaid diagram
├── COMPONENTS.md             # AI-generated per-file component documentation
├── CONSOLIDATED_AST.html     # Interactive cross-file dependency graph (SVG)
└── ast/
    ├── main.ast.html         # Per-file AST visualization (SVG)
    ├── main.md               # Per-file function signatures + docstrings
    ├── utils.ast.html
    ├── utils.md
    └── ...                   # One pair per Python file
```

---

## 🧠 LLM Integration

### Dual Backend Architecture

The `LLMClient` class abstracts over two LLM providers, selectable via the `LLM_BACKEND` environment variable:

```
┌───────────────────────────────────────────────┐
│              LLMClient                         │
│                                                │
│  __init__():                                   │
│    self.backend = env("LLM_BACKEND", "ollama") │
│    self.model   = env("LLM_MODEL", "llama3")   │
│                                                │
│  complete(prompt, max_tokens, temperature):     │
│    ├── backend == "openai" ──▶ OpenAI SDK      │
│    │   chat.completions.create(                │
│    │     model, messages=[{user: prompt}],      │
│    │     max_tokens, temperature)               │
│    │                                            │
│    └── backend == "ollama" ──▶ HTTP POST       │
│        POST http://localhost:11434/api/generate │
│        {model, prompt, stream: false}           │
│        timeout: 300s                            │
└───────────────────────────────────────────────┘
```

### Prompt Templates

#### Component Documentation Prompt

Sent once per file chunk (4000 chars max), temperature 0.2, max_tokens 2048:

```
You are a senior software architect. Analyze the following code and generate
detailed technical documentation for this component. Include:
- Purpose and responsibilities
- Key classes/functions
- Inputs/outputs
- Usage examples (if possible)
- Any dependencies or integration points

Code:
{chunk}
```

#### Architecture Documentation Prompt

Single call with all component summaries concatenated, max_tokens 4096:

```
You are a senior software architect. Given the following component documentation,
generate:
- An overall technical documentation for the repository
- A high-level architecture description
- A detailed flow of the system
- Optionally, a mermaid diagram for the architecture

Component Documentation:
{all_component_summaries}
```

### LLM Parameters

| Parameter | Component Docs | Architecture Docs | Default |
|---|---|---|---|
| Temperature | 0.2 | 0.2 | Low for deterministic output |
| Max Tokens | 2048 | 4096 | Architecture needs more space |
| Chunk Size | 4000 chars | N/A (full concat) | Respects LLM context limits |
| Streaming | Disabled | Disabled | Full response returned |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Installation | Purpose |
|---|---|---|---|
| Python | 3.10+ | [python.org](https://python.org) | Runtime |
| Graphviz | Latest | `brew install graphviz` / `apt install graphviz` | SVG rendering for AST graphs |
| Git | Latest | Pre-installed on most systems | Repository cloning |
| Ollama | Latest | [ollama.com](https://ollama.com) | Local LLM (if using Ollama backend) |

### Step 1: Clone and Install

```bash
git clone https://github.com/maneeshkumar52/github-repo-documentation.git
cd github-repo-documentation

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Graphviz (required for AST graph SVG rendering)
brew install graphviz          # macOS
# sudo apt install graphviz   # Ubuntu/Debian
```

<details>
<summary>📋 Expected Output — Installation</summary>

```
$ pip install -r requirements.txt
Collecting gitpython
  Downloading GitPython-3.1.41-py3-none-any.whl (196 kB)
Collecting openai
  Downloading openai-1.12.0-py3-none-any.whl (226 kB)
Collecting python-dotenv
  Downloading python_dotenv-1.0.1-py3-none-any.whl (19 kB)
Collecting tqdm
  Downloading tqdm-4.66.1-py3-none-any.whl (78 kB)
Collecting networkx
  Downloading networkx-3.2.1-py3-none-any.whl (1.6 MB)
Collecting matplotlib
  Downloading matplotlib-3.8.2-cp311-cp311-macosx_11_0_arm64.whl (7.5 MB)
Collecting pydot
  Downloading pydot-2.0.0-py3-none-any.whl (23 kB)
...
Successfully installed gitpython-3.1.41 openai-1.12.0 ...
```

</details>

### Step 2: Configure LLM Backend

#### Option A: Ollama (Default — Free, Local)

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull llama3
```

No `.env` file needed — defaults to Ollama with Llama3.

#### Option B: OpenAI

```bash
# Create .env file
cat > .env << 'EOF'
LLM_BACKEND=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=sk-your-api-key-here
EOF
```

### Step 3: Generate Documentation

```bash
python main.py https://github.com/username/repository
```

<details>
<summary>📋 Expected Output — Documentation Generation</summary>

```
$ python main.py https://github.com/fastapi/fastapi
2024-01-15 10:30:00 INFO Cloning https://github.com/fastapi/fastapi...
2024-01-15 10:30:12 INFO Cloned repo to /path/to/cloned_repo
2024-01-15 10:30:12 INFO Found 156 relevant files
2024-01-15 10:30:12 INFO Processing 89 Python files for AST analysis...
Processed fastapi/main.py in 0.34 seconds
Processed fastapi/routing.py in 0.51 seconds
Processed fastapi/applications.py in 0.28 seconds
...
2024-01-15 10:30:45 INFO Building consolidated AST graph...
2024-01-15 10:30:47 INFO Saved consolidated AST to docs/CONSOLIDATED_AST.html
2024-01-15 10:30:47 INFO Generating component documentation...
Analyzing: 100%|████████████████████████████| 156/156 [03:42<00:00, 1.43s/file]
2024-01-15 10:34:29 INFO Saved component docs to docs/COMPONENTS.md
2024-01-15 10:34:29 INFO Generating architecture documentation...
2024-01-15 10:34:52 INFO Saved architecture docs to docs/ARCHITECTURE.md
2024-01-15 10:34:52 INFO Documentation complete! Output in docs/
```

</details>

### Step 4: View Results

```bash
# Open the interactive consolidated dependency graph
open docs/CONSOLIDATED_AST.html    # macOS
# xdg-open docs/CONSOLIDATED_AST.html  # Linux

# View architecture documentation
cat docs/ARCHITECTURE.md

# View component documentation
cat docs/COMPONENTS.md

# Browse per-file AST visualizations
ls docs/ast/
```

---

## 📂 Project Structure

```
github-repo-documentation/
├── main.py                     # CLI entry point — orchestrates full pipeline
├── repo_cloner.py              # Git clone operations via GitPython
├── file_traverser.py           # File discovery, AST parsing, graph construction
├── doc_generator.py            # AI-powered per-file documentation generation
├── architecture_builder.py     # Architecture-level documentation synthesis
├── llm_client.py               # Dual-backend LLM abstraction (OpenAI/Ollama)
├── utils.py                    # Logging, output dirs, chunking, markdown writer
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

### Module Responsibility Map

| Module | Lines | Role | Key Functions |
|---|---|---|---|
| `main.py` | 54 | Pipeline orchestrator, CLI entry | `main()`, `process_file_with_timing()` |
| `file_traverser.py` | 219 | File discovery + AST analysis | `get_relevant_files()`, `build_ast_graph()`, `build_consolidated_ast_graph()` |
| `doc_generator.py` | 51 | Per-file AI documentation | `analyze_file()`, `generate_component_docs()` |
| `llm_client.py` | 30 | LLM backend abstraction | `LLMClient.complete()` |
| `architecture_builder.py` | 28 | Architecture synthesis | `generate_architecture_docs()` |
| `utils.py` | 35 | Shared utilities | `chunk_file()`, `save_markdown()`, `setup_logging()` |
| `repo_cloner.py` | 15 | Git operations | `clone_repo()` |
| **Total** | **432** | | |

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `LLM_BACKEND` | `ollama` | No | LLM provider: `openai` or `ollama` |
| `LLM_MODEL` | `llama3` | No | Model name (e.g., `gpt-4`, `llama3`, `mistral`) |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | No | Ollama API endpoint |
| `OPENAI_API_KEY` | None | If `openai` backend | OpenAI API authentication key |

### Hardcoded Constants

| Constant | Value | Location | Purpose |
|---|---|---|---|
| `EXCLUDE_DIRS` | 10 directories | `file_traverser.py` | Directories skipped during traversal |
| `EXCLUDE_FILES` | 32 glob patterns | `file_traverser.py` | File patterns excluded from processing |
| `INCLUDE_EXTS` | 50+ extensions | `file_traverser.py` | File types included for documentation |
| `max_workers` | `8` | `main.py`, `doc_generator.py` | Thread pool concurrency |
| `max_size` | `4000` chars | `utils.py` | Maximum chunk size for LLM input |
| `clone_dir` | `cloned_repo` | `repo_cloner.py` | Default clone target directory |
| `temperature` | `0.2` | `llm_client.py` | LLM response determinism |
| `timeout` | `300` seconds | `llm_client.py` | Ollama HTTP request timeout |

### File Discovery Filters

<details>
<summary>📋 EXCLUDE_DIRS — Directories Skipped</summary>

```python
{'.git', '__pycache__', 'node_modules', 'venv', '.venv',
 'dist', 'build', '.idea', '.vscode', 'env'}
```

</details>

<details>
<summary>📋 EXCLUDE_FILES — File Patterns Excluded</summary>

```python
{'*.pyc', '*.pyo', '*.exe', '*.dll', '*.so', '*.dylib', '*.zip', '*.tar',
 '*.gz', '*.jpg', '*.jpeg', '*.png', '*.gif', '*.pdf', '*.md', '*.rst',
 '*.txt', '*.csv', '*.log', '*.lock', '*.db', '*.sqlite', '*.yml', '*.yaml',
 '*.json', '*.toml', '*.ini', '*.cfg', '*.env', '*.sample', '*.bat', '*.sh',
 '*.ps1', '*.iml'}
```

</details>

<details>
<summary>📋 INCLUDE_EXTS — File Types Documented (50+ extensions)</summary>

```python
{'.py', '.js', '.ts', '.java', '.go', '.cpp', '.c', '.h', '.hpp',
 '.cs', '.rb', '.rs', '.swift', '.kt', '.scala', '.r', '.m', '.mm',
 '.lua', '.pl', '.pm', '.php', '.dart', '.ex', '.exs', '.hs', '.erl',
 '.clj', '.cljs', '.ml', '.fs', '.fsx', '.groovy', '.gvy', '.jl',
 '.nim', '.zig', '.v', '.cr', '.d', '.ada', '.adb', '.ads',
 '.pas', '.pp', '.vb', '.vbs', '.asm', '.s', '.vue', '.jsx', '.tsx',
 '.svelte', '.elm'}
```

</details>

> **Note:** There is a filter conflict — `.md`, `.json`, `.yaml`, `.yml`, `.sh`, `.txt` are in EXCLUDE_FILES, but some of these have no corresponding INCLUDE_EXTS entry. This means configuration files and shell scripts are excluded from documentation.

### Example `.env` File

```bash
# Use OpenAI GPT-4
LLM_BACKEND=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx

# Or use local Ollama (default — no .env needed)
# LLM_BACKEND=ollama
# LLM_MODEL=llama3
# OLLAMA_URL=http://localhost:11434/api/generate
```

---

## 🔧 Design Decisions

### Why These Choices Were Made

| Decision | Alternatives Considered | Rationale |
|---|---|---|
| **Dual LLM backend** vs. OpenAI-only | Single provider lock-in | Flexibility — use free local Ollama or powerful cloud GPT |
| **NetworkX + pydot** vs. D3.js, Graphviz CLI | D3 requires JS runtime; CLI less portable | Python-native graph library with SVG export via pydot |
| **ThreadPoolExecutor(8)** vs. asyncio, multiprocessing | asyncio adds complexity; multiprocessing has pickle issues | Simple, effective parallelism for I/O-bound LLM calls |
| **4000-char chunks** vs. token-based splitting | Token counting requires tiktoken dependency | Character-based is simpler, good enough approximation |
| **ast module (stdlib)** vs. tree-sitter, LibCST | External parsers add dependencies | Zero-dependency Python AST parsing; sufficient for structure extraction |
| **sys.argv** vs. argparse, click, typer | CLI frameworks add complexity for single-arg tool | Minimal — only one required argument |
| **Module-level LLM singletons** vs. dependency injection | DI adds boilerplate for a CLI tool | Simple, direct instantiation; no server lifecycle to manage |
| **Two-pass dependency resolution** vs. import graph analysis | Import analysis misses dynamic calls | Function-level call graph captures actual usage patterns |
| **Destructive clone** (rmtree + re-clone) vs. git pull | Pull can fail on dirty state | Clean slate ensures consistent analysis |

### Architectural Tradeoffs

```
Simplicity ◀──────────────────────────────▶ Completeness

This project optimizes for:
  ✅ Easy to run (one command)       ❌ Python AST only (no other languages)
  ✅ Minimal dependencies             ❌ No incremental updates
  ✅ Clear pipeline stages             ❌ Re-clones on every run
  ✅ Dual LLM backend                  ❌ No caching of LLM results
  ✅ Visual AST output                 ❌ No test suite
```

### AST Graph Construction — Two-Pass Algorithm

The consolidated dependency graph uses a two-pass approach to resolve cross-file function calls:

```
Pass 1 — Function Registry                Pass 2 — Call Resolution
┌──────────────────────┐                  ┌──────────────────────────┐
│ For each .py file:    │                  │ For each .py file:        │
│   Parse AST            │                  │   Walk ast.Call nodes      │
│   Walk FunctionDef     │                  │   Extract callee name:     │
│   Register:            │                  │     ast.Name → direct      │
│     func_name → file   │                  │     ast.Attribute → method │
│                        │                  │   Lookup in registry       │
│ Output: {name: file}  │                  │   If found → add edge      │
└──────────────────────┘                  │     caller_file → callee_file│
                                           └──────────────────────────┘
```

---

## 🗄 Data Contracts

### LLM Client Interface

```python
class LLMClient:
    def __init__(self):
        """
        Reads from environment:
          LLM_BACKEND:    "openai" | "ollama"  (default: "ollama")
          LLM_MODEL:      model name           (default: "llama3")
          OLLAMA_URL:     Ollama endpoint       (default: localhost:11434)
          OPENAI_API_KEY: API key               (default: None)
        """

    def complete(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.2) -> str:
        """Returns LLM completion text, stripped of whitespace."""
```

### File Traverser Interface

```python
def get_relevant_files(root_dir: str) -> list[str]:
    """Returns absolute paths of files matching inclusion filters."""

def build_ast_graph(file_path: str) -> networkx.DiGraph:
    """Parses Python file → AST → NetworkX directed graph with labeled nodes."""

def build_consolidated_ast_graph(file_paths: list[str]) -> networkx.DiGraph:
    """Two-pass cross-file dependency graph. Nodes = files, edges = function calls."""

def extract_function_docs(file_path: str) -> str:
    """Returns markdown with function signatures, args, and docstrings."""
```

### Output File Contracts

| File | Format | Content |
|---|---|---|
| `docs/ARCHITECTURE.md` | Markdown | Architecture overview, system flow, optional Mermaid diagram |
| `docs/COMPONENTS.md` | Markdown | Per-file documentation with `## filename` headers |
| `docs/CONSOLIDATED_AST.html` | HTML + embedded SVG | Interactive cross-file dependency visualization |
| `docs/ast/{name}.ast.html` | HTML + embedded SVG | Per-file AST tree visualization |
| `docs/ast/{name}.md` | Markdown | Function signatures and docstrings |

---

## 📦 Dependencies

| Package | Purpose | Used In |
|---|---|---|
| `gitpython` | Clone GitHub repositories via `git.Repo.clone_from()` | `repo_cloner.py` |
| `openai` | OpenAI API client for GPT chat completions | `llm_client.py` |
| `python-dotenv` | Load `.env` files into `os.environ` | `llm_client.py` |
| `tqdm` | Progress bars for parallel file processing | `doc_generator.py` |
| `requests` | HTTP client for Ollama REST API | `llm_client.py` |
| `networkx` | Directed graph data structures for AST and dependency graphs | `file_traverser.py` |
| `matplotlib` | Required by NetworkX for rendering support | `file_traverser.py` |
| `pydot` | Convert NetworkX graphs to DOT format → SVG via Graphviz | `file_traverser.py` |

### System Dependencies

| Dependency | Required | Installation | Purpose |
|---|---|---|---|
| **Graphviz** | Yes | `brew install graphviz` / `apt install graphviz` | SVG rendering engine used by pydot |
| **Git** | Yes | Pre-installed on most systems | Repository cloning via GitPython |
| **Ollama** | If using Ollama backend | [ollama.com](https://ollama.com) | Local LLM runtime |

> **Note:** `networkx` is listed twice in `requirements.txt` — this is a harmless duplicate but should be cleaned up.

---

## 🐛 Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `Usage: python main.py <github_repo_url>` | Missing or extra arguments | Provide exactly one GitHub URL |
| `Failed to clone repo` | Invalid URL, private repo, or no git | Verify URL is a public repo; ensure `git` is installed |
| `No relevant files found` | Repo has no files matching INCLUDE_EXTS | Check file extensions; adjust filters in `file_traverser.py` |
| `ConnectionError: localhost:11434` | Ollama not running | Start Ollama: `ollama serve` |
| `Model not found` | Ollama model not pulled | Pull model: `ollama pull llama3` |
| `openai.AuthenticationError` | Invalid or missing API key | Set `OPENAI_API_KEY` in `.env` file |
| `pydot.InvocationException` | Graphviz not installed | Install: `brew install graphviz` / `apt install graphviz` |
| SVG graphs are empty | No Python files in the repo | AST graphs only work for `.py` files |
| Timeout on large repos | Ollama taking >300s per chunk | Use faster model or increase timeout in `llm_client.py` |
| `cloned_repo/` keeps growing | Not auto-cleaned | Previous clone is deleted on each run via `shutil.rmtree()` |

### Verifying Prerequisites

```bash
# Check Python version
python3 --version    # Needs 3.10+

# Check Git
git --version

# Check Graphviz
dot -V               # graphviz version X.X.X

# Check Ollama (if using local backend)
curl http://localhost:11434/api/tags
# Expected: {"models": [{"name": "llama3:latest", ...}]}

# Check OpenAI key (if using OpenAI backend)
echo $OPENAI_API_KEY    # Should not be empty
```

### Performance Tips

| Scenario | Recommendation |
|---|---|
| Large repo (>500 files) | Use OpenAI GPT-3.5-turbo for speed; Ollama is slower per-call |
| Many Python files | AST processing is fast; LLM calls dominate runtime |
| Slow Ollama responses | Use a smaller model (e.g., `phi-3`) or increase hardware resources |
| Rate-limited by OpenAI | Reduce `max_workers` from 8 to 2-3 |

---

## 🔒 Security Considerations

| Area | Current State | Recommendation |
|---|---|---|
| API Key Storage | `.env` file (git-ignored) | Use system keychain for production |
| Repository Cloning | Clones to local `cloned_repo/` | Runs arbitrary git commands — only use with trusted URLs |
| LLM Prompts | Source code sent to LLM | Use Ollama for sensitive codebases |
| File System Access | `shutil.rmtree()` on clone dir | Ensure `clone_dir` doesn't point to important directories |
| Dependency Versions | Unpinned in `requirements.txt` | Pin versions for reproducible builds |
| Network Access | Ollama on localhost; OpenAI over HTTPS | No additional network exposure |

---

## ☁️ Azure Production Mapping

For deploying this documentation generator as a service on Azure:

| Local Component | Azure Service | Configuration |
|---|---|---|
| CLI execution | **Azure Container Instances** | On-demand, per-repo execution |
| Ollama + Llama3 | **Azure OpenAI Service** | GPT-4o deployment, managed scaling |
| `cloned_repo/` storage | **Azure Blob Storage** | Temp container, auto-cleanup lifecycle policy |
| `docs/` output | **Azure Blob Storage** | Static website hosting for HTML visualizations |
| Git clone | **Azure DevOps / GitHub API** | Authenticated clone for private repos |
| No auth → | **Azure Entra ID** | Service principal for API access |
| No monitoring → | **Azure Application Insights** | Track LLM latency, error rates |

### Deployment Architecture

```
                    ┌────────────────────┐
                    │  Azure API Gateway  │
                    │  (APIM or Functions)│
                    └─────────┬──────────┘
                              │  POST /generate-docs
                              │  {repo_url: "..."}
                    ┌─────────▼──────────┐
                    │ Azure Container     │
                    │ Instances           │
                    │ (Documentation      │
                    │  Generator)         │
                    └──┬──────────┬──────┘
                       │          │
             ┌─────────▼──┐  ┌──▼──────────┐
             │ Azure Blob  │  │ Azure OpenAI │
             │ Storage     │  │ Service      │
             │ (repos +    │  │ (GPT-4o)     │
             │  docs/)     │  │              │
             └────────────┘  └──────────────┘
```

### Cost Estimation (Per Documentation Run)

| Service | Usage | Estimated Cost |
|---|---|---|
| Container Instances | ~5-15 min compute | ~$0.01-0.05 per run |
| Azure OpenAI (GPT-4o) | ~50-200 chunks × 2K tokens | ~$0.50-5.00 per run |
| Blob Storage | ~10-50 MB per repo | ~$0.001 per run |
| **Total per run** | | **~$0.50-5.05** |

---

## 🚀 Production Checklist

Before using this tool in production workflows:

- [ ] Pin all dependency versions in `requirements.txt`
- [ ] Remove duplicate `networkx` entry from `requirements.txt`
- [ ] Add `argparse` for proper CLI argument handling with `--help`
- [ ] Add LLM response caching to avoid re-processing unchanged files
- [ ] Implement incremental documentation (skip unchanged files)
- [ ] Add support for private repositories (SSH keys / GitHub tokens)
- [ ] Add rate limiting for OpenAI API calls
- [ ] Add test suite (pytest)
- [ ] Add progress reporting for architecture generation step
- [ ] Implement AST analysis for non-Python languages (tree-sitter)
- [ ] Add configurable EXCLUDE_DIRS and INCLUDE_EXTS via CLI flags
- [ ] Clean up `cloned_repo/` directory after documentation is complete
- [ ] Add error recovery for partial LLM failures
- [ ] Add output format options (PDF, Confluence, Notion)
- [ ] Resolve the EXCLUDE_FILES / INCLUDE_EXTS filter conflict

---

## 📄 License

This project is available under the MIT License.

---

<div align="center">

**Built with Python · NetworkX · OpenAI / Ollama · GitPython**

*Automated technical documentation for any GitHub repository*

</div>