from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "tasks_dataset_anonymized.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "tasks_dataset_with_lead_time.csv"


def load_data(file_path: Path = INPUT_PATH) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {file_path}")

    df = pd.read_csv(file_path)
    return df


def ensure_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in ["Criado_dt", "Resolvido_efetivo_dt"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def calculate_lead_time_hours(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared = ensure_datetime_columns(prepared)

    if {"Criado_dt", "Resolvido_efetivo_dt"}.issubset(prepared.columns):
        prepared["lead_time_horas"] = (
            (prepared["Resolvido_efetivo_dt"] - prepared["Criado_dt"]).dt.total_seconds() / 3600.0
        )
    else:
        raise ValueError("Colunas de data ausentes: Criado_dt e Resolvido_efetivo_dt")

    prepared["lead_time_horas"] = pd.to_numeric(prepared["lead_time_horas"], errors="coerce")
    return prepared


def save_processed_data(df: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    df = load_data()
    df = calculate_lead_time_hours(df)

    valid = df["lead_time_horas"].notna().sum()
    invalid = df["lead_time_horas"].isna().sum()
    print(f"Linhas carregadas: {len(df)}")
    print(f"Lead time válido: {valid}")
    print(f"Lead time inválido: {invalid}")
    print(f"Mínimo em horas: {df['lead_time_horas'].min()}")
    print(f"Máximo em horas: {df['lead_time_horas'].max()}")

    output_path = save_processed_data(df)
    print(f"Arquivo salvo em: {output_path}")


if __name__ == "__main__":
    main()
