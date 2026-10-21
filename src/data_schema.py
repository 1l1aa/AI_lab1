"""
Формальная схема проверки данных Fish.csv.
"""

from __future__ import annotations

import pandas as pd

try:
    import pandera.pandas as pa
    from pandera.pandas import Check, Column, DataFrameSchema
    PANDERA_AVAILABLE = True
except ImportError:
    PANDERA_AVAILABLE = False


# ---------------------------------------------------------------------------
# 1. Схема pandera
# ---------------------------------------------------------------------------
if PANDERA_AVAILABLE:
    fish_schema = DataFrameSchema(
        columns={
            "Species": Column(
                str,
                Check.isin(
                    ["Bream", "Parkki", "Perch", "Pike", "Roach", "Smelt", "Whitefish"]
                ),
                nullable=False,
            ),
            "Weight": Column(float, Check.in_range(0.0, 2000.0), nullable=False),
            "Length1": Column(float, Check.in_range(5.0, 100.0), nullable=False),
            "Length2": Column(float, Check.in_range(5.0, 100.0), nullable=False),
            "Length3": Column(float, Check.in_range(5.0, 100.0), nullable=False),
            "Height": Column(float, Check.in_range(1.0, 30.0), nullable=False),
            "Width": Column(float, Check.in_range(0.5, 15.0), nullable=False),
        },
        checks=[
            Check(
                lambda df: (
                    (df["Length1"] <= df["Length2"] + 0.5)
                    & (df["Length2"] <= df["Length3"] + 0.5)
                ).all(),
                error="Нарушена согласованность длин: ожидается L1 <= L2 <= L3 (+0.5)",
            ),
        ],
        coerce=True,
        strict=True,
    )
else:
    fish_schema = None


# ---------------------------------------------------------------------------
# 2. Ручные проверки
# ---------------------------------------------------------------------------
def check_units(df: pd.DataFrame) -> list[str]:
    """Возвращает список нарушений единиц измерения."""
    errors: list[str] = []
    if df["Weight"].max() < 100:
        errors.append(
            f"Weight: максимум {df['Weight'].max():.3f} < 100 — "
            "похоже, единицы сменились с граммов на килограммы"
        )
    for col in ["Length1", "Length2", "Length3"]:
        if df[col].max() > 100:
            errors.append(
                f"{col}: максимум {df[col].max():.3f} > 100 — "
                "похоже, единицы сменились с сантиметров на миллиметры"
            )
    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Возвращает список нарушений диапазонов."""
    errors: list[str] = []
    if df["Weight"].max() > 2000:
        errors.append(f"Weight: максимум {df['Weight'].max()} > 2000 г")
    if df["Weight"].min() < 0:
        errors.append(f"Weight: есть отрицательные значения ({df['Weight'].min()})")
    if df["Length3"].max() > 70 + 0.5:
        errors.append(f"Length3: максимум {df['Length3'].max()} > 70 см")
    return errors


def check_species(df: pd.DataFrame) -> list[str]:
    """Возвращает список нарушений по категории вида."""
    known = {"Bream", "Parkki", "Perch", "Pike", "Roach", "Smelt", "Whitefish"}
    unknown = set(df["Species"].unique()) - known
    if unknown:
        return [f"Неизвестные виды: {sorted(unknown)}"]
    return []


def validate(df: pd.DataFrame) -> None:
    """Полная валидация через pandera + ручные проверки."""
    errors = check_units(df) + check_ranges(df) + check_species(df)

    if PANDERA_AVAILABLE and fish_schema is not None:
        try:
            fish_schema.validate(df)
        except Exception as exc:
            errors.append(f"pandera: {exc}")

    if errors:
        raise ValueError("Схема данных нарушена:\n  - " + "\n  - ".join(errors))


if __name__ == "__main__":
    from pathlib import Path
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "assets" / "data" / "Fish.csv")
    validate(df)
    print("Схема данных: OK")