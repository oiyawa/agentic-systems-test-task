import subprocess
import tempfile
import os
import sys
import shutil

try:
    import resource
except Exception:
    resource = None

def _write_temp_test_file(candidate_code: str, test_code: str):
    if not candidate_code.strip():
        raise ValueError("Candidate code is empty")

    td = tempfile.mkdtemp(prefix="llm_fix_")
    file_path = os.path.join(td, "candidate.py")
    test_path = os.path.join(td, "test_candidate.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(candidate_code)
        f.write("\n")
    with open(test_path, "w", encoding="utf-8") as f:
        f.write("import pytest\nfrom candidate import *\n\n")
        f.write(test_code)
        f.write("\n")
    return td, file_path, test_path

def _preexec_limit():
    if resource is None:
        return
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (300 * 1024 * 1024, 300 * 1024 * 1024))

def run_tests_in_sandbox(candidate_code: str, test_code: str, timeout: int = 10):
    try:
        td, file_path, test_path = _write_temp_test_file(candidate_code, test_code)
    except ValueError as e:
        return False, "", str(e)

    try:
        cmd = [sys.executable, "-m", "pytest", "-q", test_path]
        proc = subprocess.run(
            cmd,
            cwd=td,
            capture_output=True,
            text=True,
            timeout=timeout,
            preexec_fn=_preexec_limit if hasattr(os, "posix") else None,
        )
        passed = proc.returncode == 0
        return passed, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return False, "", f"TimeoutExpired: {e}"
    except Exception as e:
        return False, "", str(e)
    finally:
        try:
            shutil.rmtree(td)
        except Exception:
            pass
