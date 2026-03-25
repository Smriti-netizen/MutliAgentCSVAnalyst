import io
import sys
import traceback

import numpy as np
import pandas as pd


def _blocked(*_args, **_kwargs):
    raise PermissionError("This operation is not allowed in the sandbox.")


_DANGEROUS_NAMES = {
    "open", "exec", "eval", "compile",
    "__import__", "breakpoint", "exit", "quit",
}


def run_sandboxed(code: str, df_path: str,
                  all_df_paths: list[str] | None = None) -> tuple[str, str]:
    """Execute *code* in a restricted namespace and return (stdout, error).

    The namespace exposes ``pd``, ``np``, and one or more DataFrames:
    - ``df`` is always the primary DataFrame (from *df_path*).
    - If *all_df_paths* has multiple files, ``df1``, ``df2``, etc. are also
      available.

    Dangerous builtins are replaced with a stub that raises
    ``PermissionError``.
    """
    df = pd.read_csv(df_path)

    safe_builtins = {k: v for k, v in __builtins__.items()
                     if k not in _DANGEROUS_NAMES}  # type: ignore[union-attr]
    for name in _DANGEROUS_NAMES:
        safe_builtins[name] = _blocked

    namespace: dict = {
        "__builtins__": safe_builtins,
        "pd": pd,
        "np": np,
        "df": df,
    }

    if all_df_paths and len(all_df_paths) > 1:
        for i, path in enumerate(all_df_paths):
            namespace[f"df{i + 1}"] = pd.read_csv(path)

    stdout_capture = io.StringIO()
    old_stdout = sys.stdout

    try:
        sys.stdout = stdout_capture
        exec(code, namespace)  # noqa: S102 – intentional sandboxed exec
        output = stdout_capture.getvalue()
        return (output, "")
    except Exception:
        return ("", traceback.format_exc())
    finally:
        sys.stdout = old_stdout
