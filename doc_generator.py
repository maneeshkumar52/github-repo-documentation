import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import chunk_file, save_markdown
from dotenv import load_dotenv
from tqdm import tqdm
from llm_client import LLMClient

load_dotenv()
llm = LLMClient()


def analyze_file(filepath):
    start = time.perf_counter()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        # Chunk large files for LLM context limits
        chunks = chunk_file(filepath, max_size=4000)
        docs = []
        for chunk in chunks:
            prompt = f"""
You are a senior software architect. Analyze the following code and generate detailed technical documentation for this component. Include:
- Purpose and responsibilities
- Key classes/functions
- Inputs/outputs
- Usage examples (if possible)
- Any dependencies or integration points

Code:
{chunk}
"""
            doc = llm.complete(prompt)
            docs.append(doc)
        elapsed = time.perf_counter() - start
        print(f"LLM processed {filepath} in {elapsed:.2f} seconds")
        return filepath, "\n".join(docs)
    except Exception as e:
        logging.error(f"Error analyzing {filepath}: {e}")
        return filepath, f"Error: {e}"

def generate_component_docs(files):
    docs = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(analyze_file, f): f for f in files}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Documenting components"):
            filepath, doc = future.result()
            docs[filepath] = doc
    save_markdown(docs, out_path="docs/COMPONENTS.md")
    return docs
