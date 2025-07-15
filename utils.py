import os
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )

def ensure_output_dirs():
    os.makedirs("docs", exist_ok=True)

def chunk_file(filepath, max_size=4000):
    # Chunk by lines for large files, keeping context
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    chunks = []
    chunk = []
    size = 0
    for line in lines:
        size += len(line)
        chunk.append(line)
        if size >= max_size:
            chunks.append(''.join(chunk))
            chunk = []
            size = 0
    if chunk:
        chunks.append(''.join(chunk))
    return chunks if chunks else [''.join(lines)]

def save_markdown(docs_dict, out_path):
    with open(out_path, 'w', encoding='utf-8') as f:
        for k, v in docs_dict.items():
            f.write(f"## {os.path.basename(k)}\n\n{v}\n\n")
