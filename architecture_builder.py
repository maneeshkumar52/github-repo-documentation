import os
import logging
import time
from llm_client import LLMClient
from utils import save_markdown

llm = LLMClient()

def generate_architecture_docs(component_docs, files):
    try:
        all_summaries = "\n\n".join(component_docs.values())
        prompt = f"""
You are a senior software architect. Given the following component documentation, generate:
- An overall technical documentation for the repository
- A high-level architecture description
- A detailed flow of the system
- Optionally, a mermaid diagram for the architecture

Component Documentation:
{all_summaries}
"""
        start = time.perf_counter()
        doc = llm.complete(prompt, max_tokens=4096)
        elapsed = time.perf_counter() - start
        print(f"Architecture documentation generated in {elapsed:.2f} seconds")
        save_markdown({"ARCHITECTURE": doc}, out_path="docs/ARCHITECTURE.md")
    except Exception as e:
        logging.error(f"Error generating architecture docs: {e}")
