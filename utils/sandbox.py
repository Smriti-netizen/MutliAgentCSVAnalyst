import io
import sys
import traceback

import numpy as np
import pandas as pd


def _blocked(*_args, **_kwargs):
    raise PermissionError("This operation is not allowed in the sandbox.")


# Builtins that generated code must never call.
_DANGEROUS_NAMES = {
    "open", "exec", "eval", "compile",
    "__import__", "breakpoint", "exit", "quit",
}


def run_sandboxed(code: str, df_path: str) -> tuple[str, str]:
    """Execute *code* in a restricted namespace and return (stdout, error).

    The namespace exposes only ``pd`` (pandas), ``np`` (numpy), and ``df``
    (the DataFrame loaded from *df_path*).  Dangerous builtins are replaced
    with a stub that raises ``PermissionError``.

    Returns
    -------
    (output, error) : tuple[str, str]
        *output* contains captured stdout on success; *error* contains the
        formatted traceback on failure.  Exactly one of the two will be
        non-empty.
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
