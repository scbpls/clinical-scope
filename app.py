from flask import Flask, render_template, request, url_for
import pandas as pd

from database import (
    get_db,
    close_connection,
    fetch_trials_paginated,
    fetch_unique_options,
)
from search import search_engine
from utils.dictionaries import (
    phases_map,
    statuses_map,
    sex_map,
    types_map,
    age_map,
    statuses_colors_map,
)
from utils.formatters import translate_complex_text, clean_locations

app = Flask(__name__)

app.teardown_appcontext(close_connection)


@app.context_processor
def utility_processor():
    def url_replace(**kwargs):
        args = request.args.copy()

        for key, value in kwargs.items():
            args[key] = value

        return url_for(request.endpoint, **args)

    def get_status_class(status_key):
        return statuses_colors_map.get(status_key, "is-white border-grey")

    return dict(url_replace=url_replace, get_status_class=get_status_class)


@app.route("/")
def index():
    conn = get_db()

    # Parametry
    page = request.args.get("page", 1, type=int)
    per_page = 20
    query_text = request.args.get("q", "")

    # Zebranie filtrów w słownik
    filters = {
        "q": query_text,
        "status": request.args.getlist("status"),
        "phase": request.args.getlist("phase"),
        "type": request.args.getlist("type"),
        "sex": request.args.getlist("sex"),
        "age": request.args.getlist("age"),
    }

    # Wyszukiwarka AI dla tekstów
    matching_ids = search_engine.get_relevant_ids(query_text) if query_text else []

    # Pobranie danych z bazy
    trials_data, total_pages, total_results = fetch_trials_paginated(
        conn, filters, matching_ids, page, per_page
    )

    # Sformatowanie wyników do wyświetlenia
    trials = []

    for r in trials_data:
        r["Status Key"] = r.get("Study Status", "")

        # Przetłumaczenie list
        r["Phases"] = translate_complex_text(r.get("Phases", ""), phases_map)
        r["Study Status"] = translate_complex_text(
            r.get("Study Status", ""), statuses_map
        )
        r["Study Type"] = translate_complex_text(r.get("Study Type", ""), types_map)
        r["Sex"] = translate_complex_text(r.get("Sex", ""), sex_map)
        r["Age"] = translate_complex_text(r.get("Age", ""), age_map)

        # Oczyszczenie i sformatowanie list
        r["Conditions"] = translate_complex_text(r.get("Conditions", ""), {})
        r["Interventions"] = translate_complex_text(r.get("Interventions", ""), {})
        r["Locations"] = clean_locations(r.get("Locations", ""))
        r["Brief Summary"] = r.get("Brief Summary", "") or "Brak szczegółowego opisu."

        trials.append(r)

    # Pobranie opcji do filtrów
    statuses_raw = fetch_unique_options(conn, "Study Status")
    types_raw = fetch_unique_options(conn, "Study Type")
    sex_raw = fetch_unique_options(conn, "Sex")

    # Rozdzielenie opcji dla faz
    raw_phases = fetch_unique_options(conn, "Phases")
    unique_phases = set()

    for p in raw_phases:
        for part in p.replace("/", "|").split("|"):
            if part.strip():
                unique_phases.add(part.strip())

    phases_raw = sorted(list(unique_phases))

    # Opcje wieków
    age_raw = ["CHILD", "ADULT", "OLDER_ADULT"]

    return render_template(
        "index.html",
        trials=trials,
        statuses=statuses_raw,
        phases=phases_raw,
        types=types_raw,
        sexes=sex_raw,
        ages=age_raw,
        current_q=query_text,
        current_status=filters["status"],
        current_phase=filters["phase"],
        current_type=filters["type"],
        current_sex=filters["sex"],
        current_age=filters["age"],
        phases_map=phases_map,
        statuses_map=statuses_map,
        sex_map=sex_map,
        types_map=types_map,
        age_map=age_map,
        page=page,
        total_pages=total_pages,
        total_results=total_results,
    )


@app.route("/stats")
def stats():
    conn = get_db()

    # 1. Wykres: Dynamika rozpoczętych badań
    try:
        df_time = pd.read_sql('SELECT "Start Date", "Study Type" FROM trials', conn)
        df_time["Start Date"] = pd.to_datetime(df_time["Start Date"], errors="coerce")
        df_time["Year"] = df_time["Start Date"].dt.year
        df_time["SimpleType"] = df_time["Study Type"].map(lambda x: types_map.get(x, x))

        current_year = pd.Timestamp.now().year
        df_time = df_time[
            (df_time["Year"] > 1950) & (df_time["Year"] <= current_year + 5)
        ]

        # Główne dane
        timeline_counts = df_time["Year"].value_counts().sort_index()
        timeline_labels = [str(int(y)) for y in timeline_counts.index.tolist()]
        timeline_values = timeline_counts.values.tolist()

        # Szczegółowe dane
        timeline_details = {}
        grouped = df_time.groupby(["Year", "SimpleType"]).size().unstack(fill_value=0)

        for year in timeline_counts.index:
            year_str = str(int(year))

            if year in grouped.index:
                timeline_details[year_str] = grouped.loc[year].to_dict()
            else:
                timeline_details[year_str] = {}

    except Exception:
        timeline_labels = []
        timeline_values = []
        timeline_details = {}

    # 2. Wykres: Liczebność faz badań
    phases = ["EARLY_PHASE1", "PHASE1", "PHASE2", "PHASE3", "PHASE4"]
    phase_labels = [phases_map.get(p, p) for p in phases]
    phase_values = []

    for p in phases:
        try:
            res = pd.read_sql(
                f"SELECT COUNT(*) FROM trials WHERE Phases LIKE '%{p}%'", conn
            )
            phase_values.append(int(res.iloc[0, 0]))
        except Exception:
            phase_values.append(0)

    # 3. Wykres: Wielkość grup badawczych
    enrollment_labels = ["Małe (<100)", "Średnie (100-500)", "Duże (>500)"]
    enrollment_values = [0, 0, 0]

    try:
        df_enroll = pd.read_sql("SELECT Enrollment FROM trials", conn)
        df_enroll["Enrollment"] = pd.to_numeric(
            df_enroll["Enrollment"], errors="coerce"
        )
        df_enroll = df_enroll.dropna()

        enrollment_values[0] = len(df_enroll[df_enroll["Enrollment"] < 100])
        enrollment_values[1] = len(
            df_enroll[
                (df_enroll["Enrollment"] >= 100) & (df_enroll["Enrollment"] <= 500)
            ]
        )
        enrollment_values[2] = len(df_enroll[df_enroll["Enrollment"] > 500])
    except Exception:
        enrollment_values = [0, 0, 0]

    # 4. Wykres: Najpopularniejsze choroby
    try:
        df_conditions = pd.read_sql("SELECT Conditions FROM trials", conn)
        top_conditions = (
            df_conditions["Conditions"]
            .str.split("|")
            .explode()
            .str.strip()
            .value_counts()
            .head(10)
        )

        conditions_labels = top_conditions.index.tolist()
        conditions_values = top_conditions.values.tolist()
    except Exception:
        conditions_labels = []
        conditions_values = []

    return render_template(
        "stats.html",
        timeline_labels=timeline_labels,
        timeline_values=timeline_values,
        timeline_details=timeline_details,
        phase_labels=phase_labels,
        phase_values=phase_values,
        enrollment_labels=enrollment_labels,
        enrollment_values=enrollment_values,
        conditions_labels=conditions_labels,
        conditions_values=conditions_values,
    )


if __name__ == "__main__":
    app.run(debug=True)
