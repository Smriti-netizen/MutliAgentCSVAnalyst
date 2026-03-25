import os

import pandas as pd


def _profile_single(df_path: str, label: str) -> str:
    """Profile a single CSV file and return a formatted summary."""
    df = pd.read_csv(df_path)

    lines: list[str] = []
    lines.append(f"### {label}")
    lines.append(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
    lines.append("")

    lines.append("Column | Dtype | Nulls | Unique")
    lines.append("-------|-------|-------|-------")
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isnull().sum())
        unique = int(df[col].nunique())
        lines.append(f"{col} | {dtype} | {nulls} | {unique}")

    lines.append("")
    lines.append("Sample rows (first 5):")
    lines.append(df.head(5).to_string(index=False))

    return "\n".join(lines)


def profile_dataset(df_path: str) -> str:
    """Profile a single CSV. Kept for backward compatibility."""
    return _profile_single(df_path, os.path.basename(df_path))


def profile_all_datasets(df_paths: list[str]) -> str:
    """Profile multiple CSVs and return a combined summary.

    Each file gets its own section with a label like df1, df2, etc.
    """
    if len(df_paths) == 1:
        return _profile_single(df_paths[0], "df (single dataset)")

    sections: list[str] = []
    for i, path in enumerate(df_paths):
        label = f"df{i + 1} — {os.path.basename(path)}"
        sections.append(_profile_single(path, label))

    return "\n\n---\n\n".join(sections)
