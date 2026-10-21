"""
Тесты-«сторожа» для схемы данных Fish.csv.

Запуск:
    pytest tests/ -v
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from src.data_schema import (
    check_species,
    check_units,
    check_ranges,
    validate,
)

# Ищем файл в папке assets/data/
DATA_PATH = Path(__file__).resolve().parents[1] / "assets" / "data" / "Fish.csv"

@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)

# --- Сторожевые тесты (реагируют на смену единиц / диапазона) --------------

def test_weight_units_not_changed(df: pd.DataFrame) -> None:
    assert df["Weight"].max() >= 100, (
        f"Weight.max() = {df['Weight'].max()} — похоже, единицы сменились на килограммы"
    )

def test_length_units_not_changed(df: pd.DataFrame) -> None:
    assert df["Length3"].max() <= 100, (
        f"Length3.max() = {df['Length3'].max()} — похоже, единицы сменились на миллиметры"
    )

def test_weight_range_not_expanded(df: pd.DataFrame) -> None:
    assert df["Weight"].min() >= 0
    assert df["Weight"].max() <= 2000, "Weight выходит за допустимый диапазон [0; 2000] г"

def test_length3_range_not_expanded(df: pd.DataFrame) -> None:
    assert df["Length3"].min() >= 5
    assert df["Length3"].max() <= 70, "Length3 выходит за допустимый диапазон [5; 70] см"

def test_species_known(df: pd.DataFrame) -> None:
    assert not check_species(df), check_species(df)

def test_schema_valid(df: pd.DataFrame) -> None:
    validate(df)

def test_detects_broken_units(df: pd.DataFrame) -> None:
    df_broken = df.copy()
    df_broken["Weight"] = df_broken["Weight"] / 1000.0
    assert check_units(df_broken), "check_units не заметил смену единиц Weight"
    with pytest.raises(ValueError):
        validate(df_broken)

def test_detects_broken_range(df: pd.DataFrame) -> None:
    df_broken = df.copy()
    df_broken.loc[0, "Weight"] = 5000.0
    assert check_ranges(df_broken), "check_ranges не заметил выход за диапазон"