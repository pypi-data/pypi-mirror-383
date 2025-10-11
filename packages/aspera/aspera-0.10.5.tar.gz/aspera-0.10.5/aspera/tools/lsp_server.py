"""
ASPERA LSP Server (Base)
=========================
Diagnostiche parser + completion concetti/segnali.

Uso:
  python -m aspera.tools.lsp_server
  oppure entrypoint: `aspera-lsp`
"""

from __future__ import annotations

from typing import Any, List, Dict, Set, Tuple
import os
from urllib.parse import urlparse, unquote
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_RENAME,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DefinitionParams,
    RenameParams,
    Location,
    WorkspaceEdit,
    TextEdit,
    CompletionParams,
    CompletionItem,
    CompletionList,
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)


from aspera.lang.parser import parse_aspera, ParseError, parse_aspera_with_macros
from aspera.lang.module_loader import load_module_with_imports


class AsperaLsp(LanguageServer):
    CMD_NAME = "aspera_lsp"

    def __init__(self) -> None:
        super().__init__("aspera-lsp", "0.10.0")


ls = AsperaLsp()

# Indici per URI → simboli noti
URI_INDEX: Dict[str, Dict[str, Set[str]]] = {}
URI_DEFS: Dict[str, Dict[str, Tuple[int, int]]] = {}
URI_TEXT: Dict[str, str] = {}
GLOBAL_DEFS: Dict[str, List[Tuple[str, int, int]]] = {}


def _uri_to_path(uri: string) -> str:  # type: ignore[name-defined]
    try:
        p = urlparse(uri)
        if p.scheme != "file":
            return ""
        path = unquote(p.path)
        if os.name == "nt" and path.startswith("/"):
            path = path[1:]
        return path
    except Exception:
        return ""


def _path_to_uri(path: str) -> str:
    try:
        from pathlib import Path
        return Path(path).resolve().as_uri()
    except Exception:
        if os.name == "nt":
            return "file:///" + path.replace("\\", "/")
        return "file://" + path


@ls.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: AsperaLsp, params: DidOpenTextDocumentParams):  # type: ignore
    text = params.text_document.text or ""
    URI_TEXT[params.text_document.uri] = text
    _index_symbols(params.text_document.uri, text)
    _validate_and_publish(ls, params.text_document.uri, text)


@ls.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: AsperaLsp, params: DidChangeTextDocumentParams):  # type: ignore
    text = params.content_changes[0].text if params.content_changes else ""
    URI_TEXT[params.text_document.uri] = text
    _index_symbols(params.text_document.uri, text)
    _validate_and_publish(ls, params.text_document.uri, text)


def _validate_and_publish(ls: AsperaLsp, uri: str, text: str) -> None:
    diagnostics: List[Diagnostic] = []
    try:
        # parse semplice; in futuro: usare module loader su path
        parse_aspera(text)
    except ParseError as e:
        # prova a estrarre linea/col dal messaggio
        line = 0
        col = 0
        try:
            # messaggi formattati nel parser contengono "at line X, column Y"
            msg = str(e)
            if " at line " in msg and ", column " in msg:
                part = msg.split(" at line ")[1]
                line = int(part.split(", column ")[0]) - 1
                col = int(part.split(", column ")[1].split("\n")[0]) - 1
        except Exception:
            line = 0
            col = 0
        diagnostics.append(
            Diagnostic(
                range=Range(start=Position(line=line, character=col), end=Position(line=line, character=col + 1)),
                message=str(e),
                severity=DiagnosticSeverity.Error,
                source="aspera-parser",
            )
        )
    ls.publish_diagnostics(uri, diagnostics)


def _index_symbols(uri: str, text: str) -> None:
    """Costruisce indice semantico (concepts, signals, state) per completamento."""
    concepts: Set[str] = set()
    signals: Set[str] = set()
    state_keys: Set[str] = set()

    # Preferisci parsing via file con import+macro, altrimenti inline
    ast = None
    path = _uri_to_path(uri)
    try:
        if path and os.path.exists(path):
            ast = load_module_with_imports(path)
        else:
            try:
                ast = parse_aspera_with_macros(text)
            except Exception:
                ast = parse_aspera(text)
    except Exception:
        ast = None

    try:
        if isinstance(ast, dict):
            for node in ast.get("nodes", []):
                t = node.get("type")
                if t == "concept":
                    name = node.get("name")
                    if isinstance(name, str):
                        concepts.add(name)
                    sigs = node.get("signals", [])
                    if isinstance(sigs, list):
                        for s in sigs:
                            if isinstance(s, str):
                                signals.add(s)
                elif t == "state":
                    entries = node.get("entries", {})
                    if isinstance(entries, dict):
                        for k in entries.keys():
                            if isinstance(k, str):
                                state_keys.add(k)
    except Exception:
        pass

    URI_INDEX[uri] = {
        "concepts": concepts,
        "signals": signals,
        "state": state_keys,
    }

    # Definitions (best-effort scan)
    defs: Dict[str, Tuple[int, int]] = {}
    try:
        lines = text.splitlines()
        # concept declarations
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("concept "):
                rest = stripped[len("concept "):]
                name = ""
                if rest.startswith('"'):
                    try:
                        name = rest.split('"')[1]
                    except Exception:
                        name = rest.replace("{", "").strip('" {}')
                else:
                    name = rest.replace("{", "").strip(' {}')
                if name:
                    col = line.find(name)
                    defs[f"concept.{name}"] = (i, max(col, 0))
        # state entries
        in_state = False
        for i, line in enumerate(lines):
            if line.strip().startswith("state") and "{" in line:
                in_state = True
                continue
            if in_state:
                if "}" in line:
                    in_state = False
                    continue
                if ":" in line:
                    key = line.strip().split(":")[0]
                    if key and all(c not in key for c in ' {}\"'):
                        col = line.find(key)
                        defs[f"state.{key}"] = (i, max(col, 0))
        # signals inside signals: ["..."] lines
        for i, line in enumerate(lines):
            if "signals:" in line:
                start = line.find("signals:")
                part = line[start:]
                tokens = []
                tmp = ""
                in_q = False
                for ch in part:
                    if ch == '"':
                        in_q = not in_q
                        if not in_q and tmp:
                            tokens.append(tmp)
                            tmp = ""
                        continue
                    if in_q:
                        tmp += ch
                for tok in tokens:
                    col = line.find(tok, start)
                    defs[f"signals.{tok}"] = (i, max(col, 0))
    except Exception:
        pass
    URI_DEFS[uri] = defs
    _update_global_defs_for_uri(uri, defs)


def _update_global_defs_for_uri(uri: str, defs: Dict[str, Tuple[int, int]]) -> None:
    # Rimuovi posizioni precedenti per questo uri
    try:
        for sym in list(GLOBAL_DEFS.keys()):
            GLOBAL_DEFS[sym] = [p for p in GLOBAL_DEFS[sym] if p[0] != uri]
            if not GLOBAL_DEFS[sym]:
                del GLOBAL_DEFS[sym]
    except Exception:
        pass
    # Aggiungi le nuove posizioni
    for sym, (line, col) in defs.items():
        GLOBAL_DEFS.setdefault(sym, []).append((uri, line, col))


def _workspace_root(ls: AsperaLsp, fallback_uri: str) -> str:
    if getattr(ls.workspace, "root_path", None):
        return ls.workspace.root_path  # type: ignore[attr-defined]
    p = _uri_to_path(fallback_uri)
    return os.path.dirname(p) if p else os.getcwd()


def _scan_workspace(ls: AsperaLsp, root: str, limit: int = 1000) -> None:
    count = 0
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".aspera"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                uri = _path_to_uri(path)
                _index_symbols(uri, text)
            except Exception:
                pass
            count += 1
            if count >= limit:
                return


def _extract_prefix(text: str, line: int, ch: int) -> Tuple[str, str]:
    """Ritorna (head, partial) tra {concept., signals., state.} e la parte già digitata."""
    try:
        lines = text.splitlines()
        if line < 0 or line >= len(lines):
            return "", ""
        prefix = lines[line][:ch]
        heads = ["concept.", "signals.", "state."]
        best = ("", "")
        for h in heads:
            i = prefix.rfind(h)
            if i != -1:
                partial = prefix[i + len(h) :]
                # interrompi se c'è spazio dopo head
                if " " in partial or "\t" in partial:
                    continue
                best = (h, partial)
        return best
    except Exception:
        return "", ""


@ls.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls: AsperaLsp, params: CompletionParams):  # type: ignore
    items: List[CompletionItem] = []
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    text = URI_TEXT.get(uri, doc.source if doc else "")
    head, partial = _extract_prefix(text, params.position.line, params.position.character)

    index = URI_INDEX.get(uri, {})
    if head == "concept.":
        for name in sorted(index.get("concepts", [])):
            if not partial or name.startswith(partial):
                items.append(CompletionItem(label=name))
    elif head == "signals.":
        for name in sorted(index.get("signals", [])):
            if not partial or name.startswith(partial):
                items.append(CompletionItem(label=name))
    elif head == "state.":
        for name in sorted(index.get("state", [])):
            if not partial or name.startswith(partial):
                items.append(CompletionItem(label=name))
    else:
        # fallback: heads + parole chiave
        for h in ["concept.", "signals.", "state.", "threshold("]:
            items.append(CompletionItem(label=h))
        for kw in [
            "concept",
            "associate",
            "state",
            "inference",
            "intention",
            "explain",
            "mode",
            "when",
            "then",
            "priority",
            "confidence",
        ]:
            items.append(CompletionItem(label=kw))

    return CompletionList(is_incomplete=False, items=items)


def _word_at(text: str, line: int, ch: int) -> str:
    try:
        s = text.splitlines()[line]
        l = ch
        r = ch
        while l > 0 and (s[l - 1].isalnum() or s[l - 1] in "_."):
            l -= 1
        n = len(s)
        while r < n and (s[r].isalnum() or s[r] in "_."):
            r += 1
        return s[l:r]
    except Exception:
        return ""


def _symbol_from_cursor(text: str, line: int, ch: int) -> str:
    token = _word_at(text, line, ch)
    if token.startswith("concept.") or token.startswith("signals.") or token.startswith("state."):
        return token.rstrip(",);] }")
    try:
        s = text.splitlines()[line].strip()
        if s.startswith("concept "):
            parts = s[len("concept "):].replace("{", " ").strip().split()
            name = parts[0].strip('"') if parts else ""
            if name:
                return f"concept.{name}"
    except Exception:
        pass
    return ""


@ls.feature(TEXT_DOCUMENT_DEFINITION)
def goto_definition(ls: AsperaLsp, params: DefinitionParams):  # type: ignore
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    text = URI_TEXT.get(uri, doc.source if doc else "")
    sym = _symbol_from_cursor(text, params.position.line, params.position.character)
    if not sym:
        return None
    pos = URI_DEFS.get(uri, {}).get(sym)
    if pos:
        line, col = pos
        return Location(uri=uri, range=Range(start=Position(line=line, character=col), end=Position(line=line, character=col + len(sym.split(".")[-1]))))
    # Fallback globale
    root = _workspace_root(ls, uri)
    if sym not in GLOBAL_DEFS:
        _scan_workspace(ls, root)
    locs = GLOBAL_DEFS.get(sym)
    if not locs:
        return None
    g_uri, line, col = locs[0]
    return Location(uri=g_uri, range=Range(start=Position(line=line, character=col), end=Position(line=line, character=col + len(sym.split(".")[-1]))))


@ls.feature(TEXT_DOCUMENT_RENAME)
def rename_symbol(ls: AsperaLsp, params: RenameParams):  # type: ignore
    import re

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    text = URI_TEXT.get(uri, doc.source if doc else "")
    sym = _symbol_from_cursor(text, params.position.line, params.position.character)
    if not sym:
        return None
    new_name = params.new_name
    if sym.startswith("concept."):
        kind = "concept"
    elif sym.startswith("signals."):
        kind = "signals"
    elif sym.startswith("state."):
        kind = "state"
    else:
        return None
    old = sym.split(".", 1)[1]

    changes: Dict[str, List[TextEdit]] = {}

    def compute_edits(file_text: str) -> List[TextEdit]:
        edits: List[TextEdit] = []
        lines = file_text.splitlines()

        def add(pattern: str, repl: str):
            for li, line in enumerate(lines):
                for m in re.finditer(pattern, line):
                    start = m.start(1)
                    end = m.end(1)
                    edits.append(
                        TextEdit(
                            range=Range(
                                start=Position(line=li, character=start),
                                end=Position(line=li, character=end),
                            ),
                            new_text=repl,
                        )
                    )

        if kind == "concept":
            add(r"\bconcept\.(" + re.escape(old) + r")\b", new_name)
            add(r"\bconcept\s+\"?(" + re.escape(old) + r")\"?\s*\{", new_name)
            add(r"concept:\s*\"?(" + re.escape(old) + r")\"?", new_name)
        elif kind == "signals":
            add(r"\bsignals\.(" + re.escape(old) + r")\b", new_name)
            add(r"signals:\s*\[[^\]]*\b\"?(" + re.escape(old) + r")\"?\b", new_name)
        elif kind == "state":
            add(r"\bstate\.(" + re.escape(old) + r")\b", new_name)
            add(r"^\s*(" + re.escape(old) + r")\s*:\s*", new_name)
        return edits

    # file corrente
    cur_edits = compute_edits(text)
    if cur_edits:
        changes[uri] = cur_edits

    # altri file nel workspace
    root = _workspace_root(ls, uri)
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".aspera"):
                continue
            path = os.path.join(dirpath, fn)
            cur_uri = _path_to_uri(path)
            if cur_uri == uri:
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    ft = f.read()
                e = compute_edits(ft)
                if e:
                    changes[cur_uri] = e
            except Exception:
                pass

    if not changes:
        return None
    return WorkspaceEdit(changes=changes)


def run() -> None:
    ls.start_io()


if __name__ == "__main__":
    run()


