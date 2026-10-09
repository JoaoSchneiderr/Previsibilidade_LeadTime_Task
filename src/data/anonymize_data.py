from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "Extração_limpa_final.xlsx"
FALLBACK_RAW_FILE = PROJECT_ROOT / "data" / "raw" / "Extração_limpa_final.xlsx"
ANONYMIZED_FILE = PROJECT_ROOT / "data" / "raw" / "Extração_limpa_final_anonimizada.xlsx"
PROCESSED_ANON_FILE = PROJECT_ROOT / "data" / "processed" / "tasks_dataset_anonymized.csv"


def clean_name(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _pseudo_name(prefix: str, index: int) -> str:
    return f"{prefix}_{index:03d}"


def anonymize_column(series: pd.Series, prefix: str) -> pd.Series:
    cleaned = series.map(clean_name)
    unique_values = [value for value in cleaned.unique() if value != ""]
    mapping = {value: _pseudo_name(prefix, idx + 1) for idx, value in enumerate(unique_values)}
    anonymized = cleaned.map(mapping)
    return anonymized


def detect_sensitive_columns(df: pd.DataFrame) -> dict[str, str]:
    columns = {}
    for column in df.columns:
        label = str(column).lower()
        if any(token in label for token in ["cliente", "customer", "nome", "name", "desenvolvedor", "developer", "situacao", "status", "estado", "responsavel", "owner"]):
            if any(token in label for token in ["cliente", "customer", "nome", "name", "desenvolvedor", "developer"]):
                columns[column] = "name"
            else:
                columns[column] = "status"
    return columns


def anonymize_dataset(input_path: Path | None = None, output_path: Path = ANONYMIZED_FILE) -> pd.DataFrame:
    if input_path is None:
        input_path = RAW_FILE if RAW_FILE.exists() else FALLBACK_RAW_FILE

    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

    df = pd.read_excel(input_path)
    sensitive_columns = detect_sensitive_columns(df)

    if not sensitive_columns:
        raise ValueError("Nenhuma coluna sensível foi detectada para anonimização.")

    for column, kind in sensitive_columns.items():
        prefix = "CLIENTE" if kind == "name" else "SITUACAO"
        df[column] = anonymize_column(df[column], prefix)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)

    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_ANON_FILE, index=False)

    print(f"Arquivo original: {input_path}")
    print(f"Arquivo anonimizado: {output_path}")
    print(f"Arquivo processado: {PROCESSED_ANON_FILE}")
    print(f"Colunas anonimizadas: {list(sensitive_columns.keys())}")
    print(df.head(3).to_string(index=False))
    return df


if __name__ == "__main__":
    anonymize_dataset()
