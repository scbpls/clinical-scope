import sqlite3
import pandas as pd
import math
from flask import g

DATABASE = "clinical_trials.db"


def get_db():
    """Otwiera połączenie z bazą danych"""
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row

    return db


def close_connection(exception):
    """Zamyka połączenie z bazą danych"""
    db = getattr(g, "_database", None)

    if db is not None:
        db.close()


def get_chart_data(query_sql, connection, mapping=None):
    """Pobiera dane do wykresów"""
    try:
        df = pd.read_sql(query_sql, connection)

        if df.empty:
            return [], []

        values = [int(x) for x in df["count"]]
        labels = df.iloc[:, 0].tolist()

        if mapping:
            labels = [mapping.get(label, label) for label in labels]

        return values, labels
    except Exception:
        return [], []


def build_search_query(filters, matching_ids=None):
    """Buduje dynamicznie zapytanie SQL na podstawie filtrów"""
    conditions = ["1=1"]
    params = []

    # 1. Filtrowanie po ID
    if filters.get("q"):
        if matching_ids:
            placeholders = ",".join("?" * len(matching_ids))
            conditions.append(f'"NCT Number" IN ({placeholders})')
            params.extend(matching_ids)
        else:
            conditions.append("1=0")

    # 2. Filtry typu checkbox
    for key, col_name in [
        ("status", "Study Status"),
        ("type", "Study Type"),
        ("sex", "Sex"),
    ]:
        values = filters.get(key)
        if values:
            placeholders = ",".join("?" * len(values))
            conditions.append(f'"{col_name}" IN ({placeholders})')
            params.extend(values)

    # 3. Filtry tekstowe
    for key, col_name in [("phase", "Phases"), ("age", "Age")]:
        values = filters.get(key)

        if values:
            or_conditions = [f"{col_name} LIKE ?" for _ in values]
            conditions.append(f"({' OR '.join(or_conditions)})")

            for v in values:
                params.append(f"%{v}%")

    return " AND ".join(conditions), params


def fetch_trials_paginated(conn, filters, matching_ids, page, per_page):
    """Pobiera stronę wyników oraz całkowitą liczbę stron"""
    where_clause, params = build_search_query(filters, matching_ids)

    # Zapytanie o licznik
    count_sql = f"SELECT COUNT(*) FROM trials WHERE {where_clause}"
    total_results = conn.execute(count_sql, params).fetchone()[0]
    total_pages = math.ceil(total_results / per_page)

    # Zapytanie o dane
    offset = (page - 1) * per_page
    data_sql = f"SELECT * FROM trials WHERE {where_clause} LIMIT ? OFFSET ?"
    data_params = params + [per_page, offset]

    cursor = conn.cursor()
    cursor.execute(data_sql, data_params)
    rows = cursor.fetchall()

    return [dict(row) for row in rows], total_pages, total_results


def fetch_unique_options(conn, column):
    """Pobiera unikalne wartości do filtrów"""
    try:
        query = f'SELECT DISTINCT "{column}" FROM trials WHERE "{column}" IS NOT NULL AND "{column}" != \'\' ORDER BY "{column}"'

        return [row[0] for row in conn.execute(query)]
    except Exception:
        return []
