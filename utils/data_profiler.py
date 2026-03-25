import pandas as pd


def profile_dataset(df_path: str) -> str:
    """Extract schema, dtypes, shape, nulls, and sample rows from a CSV.

    Returns a formatted string suitable for inclusion in LLM prompts.
    Only this summary is sent to the model -- never the full dataset.
    """
    df = pd.read_csv(df_path)

    lines: list[str] = []
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
