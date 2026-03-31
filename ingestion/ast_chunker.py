# ingestion/ast_chunker.py
import ast
import os
import re
from dataclasses import dataclass

@dataclass
class CodeChunk:
    chunk_id:   str
    content:    str
    file_path:  str
    chunk_type: str
    name:       str
    start_line: int
    end_line:   int
    language:   str = "python"


# ── Python chunker (unchanged) ───────────────────────────
def chunk_python_file(file_path: str, repo_root: str) -> list[CodeChunk]:
    relative_path = os.path.relpath(file_path, repo_root)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except Exception:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [CodeChunk(
            chunk_id=f"{relative_path}::whole_file",
            content=source[:3000],
            file_path=relative_path,
            chunk_type="module_level",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=source.count("\n") + 1,
            language="python",
        )]

    source_lines = source.splitlines()
    chunks = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = node.end_lineno
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
                language="python",
            ))

    module_level = _extract_module_level(source_lines, tree)
    if module_level.strip():
        chunks.append(CodeChunk(
            chunk_id=f"{relative_path}::module_level",
            content=module_level,
            file_path=relative_path,
            chunk_type="module_level",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=len(source_lines),
            language="python",
        ))

    return chunks


def _extract_module_level(source_lines: list[str], tree: ast.Module) -> str:
    occupied = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for ln in range(node.lineno, node.end_lineno + 1):
                occupied.add(ln)
    return "\n".join(
        line for i, line in enumerate(source_lines, start=1)
        if i not in occupied
    )


# ── JavaScript chunker (regex-based, no heavy deps) ──────
def chunk_javascript_file(file_path: str, repo_root: str) -> list[CodeChunk]:
    """
    Extracts functions, classes, and arrow functions from JS/TS files
    using regex — no tree-sitter dependency needed.
    """
    relative_path = os.path.relpath(file_path, repo_root)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except Exception:
        return []

    lines = source.splitlines()
    chunks = []

    # Patterns to match common JS/TS constructs
    patterns = [
        # regular function declarations: function foo(...) {
        (r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(', "function"),
        # class declarations: class Foo {
        (r'^(?:export\s+)?(?:default\s+)?class\s+(\w+)', "class"),
        # arrow functions / const foo = (...) =>
        (r'^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(.*\)\s*=>', "function"),
        # method shorthand in objects/classes: foo(...) {
        (r'^\s{2,}(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{', "method"),
    ]

    def find_block_end(lines: list[str], start: int) -> int:
        """Finds the closing brace line for a block starting at `start`."""
        depth = 0
        for i in range(start, len(lines)):
            depth += lines[i].count("{") - lines[i].count("}")
            if depth <= 0 and i > start:
                return i
        return min(start + 50, len(lines) - 1)  # fallback

    seen_names = set()

    for i, line in enumerate(lines):
        for pattern, chunk_type in patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(1)
                if name in seen_names:
                    continue
                seen_names.add(name)

                end = find_block_end(lines, i)
                content = "\n".join(lines[i:end + 1])

                chunks.append(CodeChunk(
                    chunk_id=f"{relative_path}::{name}",
                    content=content[:2000],  # cap large functions
                    file_path=relative_path,
                    chunk_type=chunk_type,
                    name=name,
                    start_line=i + 1,
                    end_line=end + 1,
                    language="javascript",
                ))
                break  # only match one pattern per line

    # if no chunks found, store whole file (e.g. config files)
    if not chunks:
        chunks.append(CodeChunk(
            chunk_id=f"{relative_path}::whole_file",
            content=source[:3000],
            file_path=relative_path,
            chunk_type="module_level",
            name=os.path.basename(file_path),
            start_line=1,
            end_line=len(lines),
            language="javascript",
        ))

    return chunks


# ── Main entry point ─────────────────────────────────────
def chunk_repository(py_files: list[str], repo_root: str) -> list[CodeChunk]:
    """Chunks Python files only — for backward compatibility."""
    return _chunk_files(py_files, repo_root, "python")


def chunk_repository_multilang(files_by_lang: dict, repo_root: str) -> list[CodeChunk]:
    """
    Chunks all supported files.
    files_by_lang = {"python": [...], "javascript": [...]}
    """
    all_chunks = []
    seen_ids = set()

    for lang, file_list in files_by_lang.items():
        for file_path in file_list:
            if lang == "python":
                file_chunks = chunk_python_file(file_path, repo_root)
            elif lang == "javascript":
                file_chunks = chunk_javascript_file(file_path, repo_root)
            else:
                continue

            for chunk in file_chunks:
                if chunk.chunk_id not in seen_ids:
                    seen_ids.add(chunk.chunk_id)
                    all_chunks.append(chunk)

    return all_chunks


def _chunk_files(file_list: list[str], repo_root: str, lang: str) -> list[CodeChunk]:
    all_chunks = []
    seen_ids = set()
    for file_path in file_list:
        chunks = chunk_python_file(file_path, repo_root) if lang == "python" else chunk_javascript_file(file_path, repo_root)
        for chunk in chunks:
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                all_chunks.append(chunk)
    return all_chunks