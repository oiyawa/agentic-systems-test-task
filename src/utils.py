from __future__ import annotations
import json
import os
import tempfile
from typing import Any


def safe_read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception:
        raise


def safe_write_json(path: str, obj: Any, indent: int = 2) -> None:
    dirpath = os.path.dirname(path) or "."
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="tmpjson_", dir=dirpath, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=indent)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        raise


def truncate_text(s: str, max_len: int = 2000) -> str:
    if not isinstance(s, str):
        s = str(s)
    if len(s) <= max_len:
        return s
    head = s[: max_len // 2]
    tail = s[- (max_len // 2):]
    return head + "\n\n...[TRUNCATED]...\n\n" + tail


def normalize_code_block(text: str) -> str:
    import re
    matches = re.findall(r"```python\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()

    match = re.search(r"(def\s+\w+\s*\(.*?\):.*?)$", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ""



def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
