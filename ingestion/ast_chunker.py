# ingestion/ast_chunker.py
import ast
import os
from dataclasses import dataclass

@dataclass
class CodeChunk:
    chunk_id: str         # unique ID for ChromaDB
    content: str          # the actual source code of this chunk
    file_path: str        # relative path from repo root
    chunk_type: str       # "function", "class", "module_level"
    name: str             # function/class name, or filename for module-level
    start_line: int
    end_line: int
    language: str = "python"


def chunk_python_file(file_path: str, repo_root: str) -> list[CodeChunk]:
    """
    Parses a Python file with AST and extracts functions and classes as chunks.
    Falls back to whole-file chunking if the file can't be parsed.
    """
    relative_path = os.path.relpath(file_path, repo_root)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except Exception:
        return []

    chunks = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        # unparseable file — store it as one big chunk rather than skip it
        return [CodeChunk(
            chunk_id=f"{relative_path}::whole_file",
            content=source[:3000],  # cap at 3000 chars for very large files
            file_path=relative_path,
            chunk_type="module_level",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=source.count("\n") + 1,
        )]

    source_lines = source.splitlines()

    for node in ast.walk(tree):
        # only top-level functions and classes (not nested)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        # skip nested — only process nodes whose parent is the Module
        # (we'll handle this with a direct child check below)

    # better approach: iterate direct children of the module
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1   # 0-indexed
            end = node.end_lineno     # 1-indexed end — works as slice end
            chunk_source = "\n".join(source_lines[start:end])

            chunk_type = "class" if isinstance(node, ast.ClassDef) else "function"

            chunks.append(CodeChunk(
                chunk_id=f"{relative_path}::{node.name}",
                content=chunk_source,
                file_path=relative_path,
                chunk_type=chunk_type,
                name=node.name,
                start_line=node.lineno,
                end_line=node.end_lineno,
            ))

    # also capture module-level code (imports, constants, top-level logic)
    # that isn't inside any function/class
    module_level_lines = _extract_module_level(source_lines, tree)
    if module_level_lines.strip():
        chunks.append(CodeChunk(
            chunk_id=f"{relative_path}::module_level",
            content=module_level_lines,
            file_path=relative_path,
            chunk_type="module_level",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=len(source_lines),
        ))

    return chunks


def _extract_module_level(source_lines: list[str], tree: ast.Module) -> str:
    """
    Returns lines that are NOT inside any top-level function or class.
    Captures imports, constants, __all__, etc.
    """
    occupied_lines = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for lineno in range(node.lineno, node.end_lineno + 1):
                occupied_lines.add(lineno)

    module_lines = [
        line for i, line in enumerate(source_lines, start=1)
        if i not in occupied_lines
    ]
    return "\n".join(module_lines)


def chunk_repository(py_files: list[str], repo_root: str) -> list[CodeChunk]:
    """
    Chunks all Python files in the repo. Deduplicates by chunk_id.
    """
    all_chunks = []
    seen_ids = set()

    for file_path in py_files:
        file_chunks = chunk_python_file(file_path, repo_root)
        for chunk in file_chunks:
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                all_chunks.append(chunk)

    return all_chunks