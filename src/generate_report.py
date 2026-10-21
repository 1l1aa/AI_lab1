"""
Простой, но современный автоматический HTML-отчёт для лабораторной №1.
"""

from __future__ import annotations

import base64
import html
from pathlib import Path
from string import Template
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "assets" / "data" / "Fish.csv"
FIG_DIR = PROJECT_ROOT / "reports" / "figures"
OUT_PATH = PROJECT_ROOT / "reports" / "html" / "lab01_auto_report.html"

# ---------------------------------------------------------------------------
# Современный CSS (без внешних CDN, файл остается легким)
# ---------------------------------------------------------------------------
TEMPLATE = Template(
    """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>FishGrow — EDA Report</title>
<style>
:root {
    --bg-color: #f8fafc;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --card-bg: #ffffff;
    --primary: #3b82f6;
    --border: #e2e8f0;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-main);
    line-height: 1.6;
    margin: 0;
    padding: 40px 20px;
}
.container {
    max-width: 1000px;
    margin: 0 auto;
}
header {
    margin-bottom: 40px;
    text-align: center;
}
h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 10px;
    color: #0f172a;
}
.subtitle {
    color: var(--text-muted);
    font-size: 1rem;
}
h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-top: 40px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--border);
    color: #0f172a;
}
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow-x: auto;
    margin-bottom: 24px;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
th {
    background-color: #f1f5f9;
    font-weight: 600;
    text-align: left;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    color: #334155;
}
td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
}
tr:last-child td { border-bottom: none; }
tr:hover { background-color: #f8fafc; }
.figure-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
}
figure {
    margin: 0;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
}
figcaption {
    text-align: center;
    font-size: 0.85rem;
    color: var(--text-muted);
    margin-top: 12px;
    font-weight: 500;
}
.badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #dbeafe;
    color: #1e40af;
}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>FishGrow: Автоматический EDA-отчёт</h1>
        <div class="subtitle">
            <span class="badge">Дополнение к ЛР №1</span> &nbsp;|&nbsp; 
            Данные: <code>Fish.csv</code> &nbsp;|&nbsp; 
            Строк: $n_rows &nbsp;|&nbsp; 
            Столбцов: $n_cols
        </div>
    </header>

    <h2>1. Паспорт данных</h2>
    <div class="card">
        $schema_table
    </div>

    <h2>2. Пропуски и уникальные значения</h2>
    <div class="card">
        $missing_table
    </div>

    <h2>3. Описательные статистики</h2>
    <div class="card">
        $describe_table
    </div>

    <h2>4. Распределение видов</h2>
    <div class="card">
        $species_table
    </div>

    <h2>5. Автоматические проверки качества</h2>
    <div class="card">
        $checks_table
    </div>

    <h2>6. Ключевые визуализации</h2>
    <div class="figure-grid">
        $figures_html
    </div>

    <p style="text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-top: 40px;">
        Отчёт сгенерирован скриптом <code>src/generate_report.py</code>.
        Глубокий анализ с выводами находится в <code>01-eda.ipynb</code> и <code>lab01-report.md</code>.
    </p>
</div>
</body>
</html>
"""
)

def df_to_html(df: pd.DataFrame, index: bool = False) -> str:
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].map(lambda v: html.escape(str(v)))
    header = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = ""
    for _, row in df.iterrows():
        body += "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"

def fig_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")

def build_schema_table(df: pd.DataFrame) -> pd.DataFrame:
    roles = {
        "Species": "признак (группирующий)", "Weight": "целевая переменная",
        "Length1": "признак (вертикальная длина)", "Length2": "признак (диагональная длина)",
        "Length3": "признак (поперечная длина)", "Height": "признак (высота)", "Width": "признак (ширина)",
    }
    units = {"Species": "—", "Weight": "граммы", "Length1": "см", "Length2": "см", "Length3": "см", "Height": "см", "Width": "см"}
    return pd.DataFrame({
        "Поле": df.columns,
        "Тип": [str(t) for t in df.dtypes],
        "Единицы": [units.get(c, "—") for c in df.columns],
        "Назначение": [roles.get(c, "—") for c in df.columns],
        "Пропуски": [int(df[c].isna().sum()) for c in df.columns],
        "Уникальных": [int(df[c].nunique(dropna=False)) for c in df.columns],
    })

def build_checks_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("Полные дубликаты", int(df.duplicated().sum())),
        ("Неположительный Weight", int((df["Weight"] <= 0).sum())),
        ("Неположительные длины", int((df[["Length1", "Length2", "Length3", "Height", "Width"]] <= 0).sum().sum())),
        ("Неизвестные виды", int((~df["Species"].isin(["Bream", "Parkki", "Perch", "Pike", "Roach", "Smelt", "Whitefish"])).sum())),
        ("Length3 > 70 см", int((df["Length3"] > 70).sum())),
        ("Weight > 2000 г", int((df["Weight"] > 2000).sum())),
    ]
    # Подсветим нулевые значения зеленым, а не нулевые — красным (чтобы сразу бросалось в глаза)
    df_checks = pd.DataFrame(rows, columns=["Проверка", "Нарушений"])
    df_checks["Нарушений"] = df_checks["Нарушений"].apply(
        lambda x: f"<span style='color: #16a34a; font-weight: 600;'>{x}</span>" if x == 0 
        else f"<span style='color: #dc2626; font-weight: 600;'>{x}</span>"
    )
    return df_checks

def build_figures_html() -> str:
    names = [
        ("01_weight_distribution.png", "Распределение Weight"),
        ("02_species_distribution.png", "Численность и масса по видам"),
        ("04_correlation_matrix.png", "Корреляционная матрица"),
        ("06_weight_outliers.png", "Выбросы по IQR"),
    ]
    parts = []
    for fname, caption in names:
        path = FIG_DIR / fname
        if not path.exists():
            parts.append(f"<div class='card' style='text-align:center; color:red;'>Нет файла: {html.escape(fname)}</div>")
            continue
        b64 = fig_to_base64(path)
        parts.append(
            f"<figure><img alt='{html.escape(caption)}' src='data:image/png;base64,{b64}'/>"
            f"<figcaption>{html.escape(caption)}</figcaption></figure>"
        )
    return "\n".join(parts)

def main() -> None:
    df = pd.read_csv(DATA_PATH)
    schema_table = df_to_html(build_schema_table(df))
    missing_table = df_to_html(pd.DataFrame({
        "Поле": df.columns,
        "Пропусков": [int(df[c].isna().sum()) for c in df.columns],
        "Доля, %": [round(float(df[c].isna().mean() * 100), 2) for c in df.columns],
    }))
    describe_table = df_to_html(df.describe().T.round(3).reset_index().rename(columns={"index": "Поле"}))
    species_table = df_to_html(df["Species"].value_counts().rename_axis("Вид").reset_index(name="Кол-во"))
    checks_table = df_to_html(build_checks_table(df))
    figures_html = build_figures_html()

    html_out = TEMPLATE.substitute(
        n_rows=len(df), n_cols=df.shape[1],
        schema_table=schema_table, missing_table=missing_table,
        describe_table=describe_table, species_table=species_table,
        checks_table=checks_table, figures_html=figures_html,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html_out, encoding="utf-8")
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"Отчёт сохранён: {OUT_PATH} ({size_kb:.1f} КБ)")

if __name__ == "__main__":
    main()