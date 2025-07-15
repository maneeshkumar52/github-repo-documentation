import os
import sys
import time
from repo_cloner import clone_repo
from file_traverser import get_relevant_files, process_python_file, build_consolidated_ast_graph, save_consolidated_ast_graph_html
from doc_generator import generate_component_docs
from architecture_builder import generate_architecture_docs
from utils import setup_logging, ensure_output_dirs
from concurrent.futures import ThreadPoolExecutor, as_completed


def process_file_with_timing(f, output_dir):
    start = time.perf_counter()
    process_python_file(f, output_dir)
    elapsed = time.perf_counter() - start
    print(f"Processed {f} in {elapsed:.2f} seconds")
    return f, elapsed

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <github_repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]
    setup_logging()
    ensure_output_dirs()

    repo_path = clone_repo(repo_url)
    files = get_relevant_files(repo_path)
    if not files:
        print("No relevant source files found in the repository.")
        sys.exit(1)
    # Build consolidated AST graph for all Python files and save as one HTML file
    output_dir = os.path.join("docs", "ast")
    os.makedirs(output_dir, exist_ok=True)
    file_times = {}
    overall_start = time.perf_counter()
    python_files = [f for f in files if f.endswith('.py')]
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file_with_timing, f, output_dir): f for f in python_files}
        for future in as_completed(futures):
            f, elapsed = future.result()
            file_times[f] = elapsed
    overall_elapsed = time.perf_counter() - overall_start
    print(f"Total time for AST/markdown processing: {overall_elapsed:.2f} seconds")
    # Build and save consolidated AST graph
    consolidated_graph = build_consolidated_ast_graph(python_files)
    save_consolidated_ast_graph_html(consolidated_graph, out_path="docs/CONSOLIDATED_AST.html")
    component_docs = generate_component_docs(files)
    generate_architecture_docs(component_docs, files)
    print("Documentation, AST graphs, and consolidated AST tree generated in docs/ directory.")

if __name__ == "__main__":
    main()
