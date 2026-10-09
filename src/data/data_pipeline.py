from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Extração_limpa_final.xlsx"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "tasks_dataset_processed.csv"

REQUIRED_COLUMNS = [
    "desenvolvedor",
    "data_criacao",
    "data_conclusao",
    "historico_status",
    "tags",
    "modulo",
    "prioridade",
    "titulo",
    "descricao",
    "sprint",
]


def normalize_column_name(name: object) -> str:
    text = str(name).strip().lower()
    text = text.replace("/", "_")
    text = text.replace("-", "_")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"__+", "_", text)
    text = text.replace("ç", "c").replace("ã", "a").replace("á", "a").replace("à", "a")
    text = text.replace("õ", "o").replace("é", "e").replace("í", "i").replace("ú", "u")
    text = text.replace("ó", "o")
    return text


def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {file_path}")

    df = pd.read_excel(file_path)
    df.columns = [normalize_column_name(column) for column in df.columns]
    return df


def validate_required_columns(df: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes na base: {missing}")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    standardized = df.copy()

    alias_map = {
        "desenvolvedor": "desenvolvedor",
        "developer": "desenvolvedor",
        "criacao": "data_criacao",
        "data_de_criacao": "data_criacao",
        "created_at": "data_criacao",
        "conclusao": "data_conclusao",
        "data_de_conclusao": "data_conclusao",
        "completed_at": "data_conclusao",
        "status_history": "historico_status",
        "historico": "historico_status",
        "tags": "tags",
        "modulo": "modulo",
        "module": "modulo",
        "prioridade": "prioridade",
        "priority": "prioridade",
        "titulo": "titulo",
        "title": "titulo",
        "descricao": "descricao",
        "description": "descricao",
        "sprint": "sprint",
    }

    standardized = standardized.rename(columns={col: alias_map.get(col, col) for col in standardized.columns})
    return standardized


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = standardize_columns(df)
    validate_required_columns(df)

    for column in ["data_criacao", "data_conclusao"]:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    df["lead_time_hours"] = (
        (df["data_conclusao"] - df["data_criacao"]).dt.total_seconds() / 3600.0
    )

    df["lead_time_hours"] = pd.to_numeric(df["lead_time_hours"], errors="coerce")

    for column in ["desenvolvedor", "modulo", "prioridade", "sprint", "tags"]:
        if column in df.columns:
            df[column] = df[column].astype("string").fillna("NA")

    for column in ["titulo", "descricao"]:
        if column in df.columns:
            df[column] = df[column].fillna("")

    return df


def save_processed_dataset(df: pd.DataFrame, output_path: Path = PROCESSED_DATA_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    raw_df = load_raw_data()
    prepared_df = prepare_dataset(raw_df)

    invalid_dates = prepared_df["data_criacao"].isna().sum() + prepared_df["data_conclusao"].isna().sum()
    print(f"Linhas carregadas: {len(prepared_df)}")
    print(f"Colunas processadas: {list(prepared_df.columns)}")
    print(f"Datas inválidas: {invalid_dates}")
    print(f"Lead time mínimo (horas): {prepared_df['lead_time_hours'].min()}")
    print(f"Lead time máximo (horas): {prepared_df['lead_time_hours'].max()}")

    output_path = save_processed_dataset(prepared_df)
    print(f"Base salva em: {output_path}")


if __name__ == "__main__":
    main()
