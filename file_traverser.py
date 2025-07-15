import os
from fnmatch import fnmatch
import networkx as nx
import ast
from networkx.drawing.nx_pydot import to_pydot

EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'dist', 'build', '.idea', '.vscode', 'env'}
EXCLUDE_FILES = {'*.pyc', '*.pyo', '*.exe', '*.dll', '*.so', '*.dylib', '*.zip', '*.tar', '*.gz', '*.jpg', '*.jpeg', '*.png', '*.gif', '*.pdf', '*.md', '*.rst', '*.txt', '*.csv', '*.log', '*.lock', '*.db', '*.sqlite', '*.yml', '*.yaml', '*.json', '*.toml', '*.ini', '*.cfg', '*.env', '*.sample', '*.bat', '*.sh', '*.ps1', '*.iml'}
# Add more extensions as needed for language support
INCLUDE_EXTS = {
    '.py', '.js', '.ts', '.java', '.go', '.cpp', '.c', '.cs', '.rb', '.php', '.swift', '.kt', '.scala', '.rs', '.m', '.dart', '.html', '.css', '.xml', '.json', '.yml', '.yaml', '.pl', '.sh', '.bat', '.ps1', '.tsx', '.jsx', '.vue', '.sql', '.r', '.jl', '.lua', '.hs', '.erl', '.ex', '.exs', '.fs', '.fsx', '.clj', '.cljs', '.groovy', '.scala', '.vb', '.f90', '.f95', '.f03', '.f08', '.ml', '.mli', '.nim', '.coffee', '.elm', '.purs', '.lisp', '.scm', '.rkt', '.v', '.sv', '.svelte', '.tsx', '.jsx', '.tsx', '.jsx', '.tsx', '.jsx'
}

def is_relevant_file(filename):
    if any(fnmatch(filename, pat) for pat in EXCLUDE_FILES):
        return False
    _, ext = os.path.splitext(filename)
    return ext in INCLUDE_EXTS

def get_relevant_files(root_dir):
    relevant_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fname in filenames:
            if is_relevant_file(fname):
                relevant_files.append(os.path.join(dirpath, fname))
    return relevant_files

# New: Build a graph/tree structure of the file system traversal

def build_file_graph(root_dir):
    G = nx.DiGraph()
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        parent = os.path.relpath(dirpath, root_dir)
        if parent == '.':
            parent = root_dir
        else:
            parent = os.path.join(root_dir, parent)
        for d in dirnames:
            child = os.path.join(dirpath, d)
            G.add_edge(parent, child)
        for fname in filenames:
            if is_relevant_file(fname):
                file_path = os.path.join(dirpath, fname)
                G.add_edge(parent, file_path)
    return G

def build_ast_graph(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception:
        return None
    G = nx.DiGraph()
    def add_nodes(node, parent=None):
        node_id = f"{type(node).__name__}_{id(node)}"
        label = type(node).__name__
        if isinstance(node, ast.FunctionDef):
            label += f"\n{node.name}({', '.join([a.arg for a in node.args.args])})"
        elif isinstance(node, ast.ClassDef):
            label += f"\n{node.name}"
        G.add_node(node_id, label=label)
        if parent:
            G.add_edge(parent, node_id)
        for child in ast.iter_child_nodes(node):
            add_nodes(child, node_id)
    add_nodes(tree)
    return G

def save_ast_graph_html(G, out_path):
    if G is None:
        return
    pdot = to_pydot(G)
    html = f"<html><body>{pdot.create_svg().decode()}</body></html>"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

def extract_function_docs(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except Exception:
        return "Could not parse file."
    docs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            docstring = ast.get_docstring(node) or "No docstring."
            demo = f"def {node.name}({', '.join(args)}): ..."
            docs.append(f"### Function `{node.name}`\n- Arguments: {', '.join(args)}\n- Docstring: {docstring}\n- Demo: `{demo}`\n")
    return '\n'.join(docs) if docs else "No functions found."

def process_python_file(file_path, output_dir):
    ast_graph = build_ast_graph(file_path)
    html_path = os.path.join(output_dir, os.path.basename(file_path) + '.ast.html')
    save_ast_graph_html(ast_graph, html_path)
    md_path = os.path.join(output_dir, os.path.basename(file_path) + '.md')
    function_docs = extract_function_docs(file_path)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(function_docs)

def build_consolidated_ast_graph(file_paths):
    G = nx.DiGraph()
    file_func_map = {}
    func_calls = []
    # First pass: collect all function definitions
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            continue
        file_node = f"File: {os.path.basename(file_path)}"
        G.add_node(file_node)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_id = f"{file_node}:{func_name}"
                file_func_map[func_id] = file_node
                G.add_node(func_id, label=f"{func_name}()")
                G.add_edge(file_node, func_id)
    # Second pass: collect function calls and connect them
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            continue
        file_node = f"File: {os.path.basename(file_path)}"
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_func = node.func.id
                    # Try to find the called function in any file
                    for func_id in file_func_map:
                        if func_id.endswith(f":{called_func}"):
                            # Find parent function (caller)
                            parent_func = None
                            parent = node
                            while parent:
                                parent = getattr(parent, 'parent', None)
                                if isinstance(parent, ast.FunctionDef):
                                    parent_func = parent.name
                                    break
                            if parent_func:
                                caller_id = f"{file_node}:{parent_func}"
                                G.add_edge(caller_id, func_id)
    return G

# Patch ast nodes to have parent references

def ast_add_parent_links(tree):
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

# Update build_consolidated_ast_graph to call ast_add_parent_links after parsing
def build_consolidated_ast_graph(file_paths):
    G = nx.DiGraph()
    file_func_map = {}
    # First pass: collect all function definitions
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            continue
        ast_add_parent_links(tree)  # Patch nodes with parent links
        file_node = f"File: {os.path.basename(file_path)}"
        G.add_node(file_node)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_id = f"{file_node}:{func_name}"
                file_func_map[func_id] = file_node
                G.add_node(func_id, label=f"{func_name}()")
                G.add_edge(file_node, func_id)
    # Second pass: collect function calls and connect them
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            continue
        file_node = f"File: {os.path.basename(file_path)}"
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_func = node.func.id
                    # Try to find the called function in any file
                    for func_id in file_func_map:
                        if func_id.endswith(f":{called_func}"):
                            # Find parent function (caller)
                            parent_func = None
                            parent = node
                            while parent:
                                parent = getattr(parent, 'parent', None)
                                if isinstance(parent, ast.FunctionDef):
                                    parent_func = parent.name
                                    break
                            if parent_func:
                                caller_id = f"{file_node}:{parent_func}"
                                G.add_edge(caller_id, func_id)
    return G

def save_consolidated_ast_graph_html(G, out_path):
    if G is None:
        return
    pdot = to_pydot(G)
    html = f"<html><body>{pdot.create_svg().decode()}</body></html>"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
