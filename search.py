import os
import sqlite3
import joblib
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from thefuzz import process, fuzz

DATABASE = "clinical_trials.db"


class SearchEngine:
    def __init__(self):
        self.matrix_path = "embeddings_matrix.joblib"
        self.conditions_path = "unique_conditions.joblib"

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.matrix = None
        self.df = None
        self.unique_conditions = []

        print("Inicjalizacja silnika wyszukiwania semantycznego...")
        self._load_and_train()
        print("Silnik gotowy!")

    def _load_and_train(self):
        """Ładuje osadzenia z dysku lub generuje nowe"""
        cache_exists = os.path.exists(self.matrix_path) and os.path.exists(
            self.conditions_path
        )

        if cache_exists:
            print("Wczytywanie zapisanych osadzeń i słownika...")
            self.matrix = joblib.load(self.matrix_path)
            self.unique_conditions = joblib.load(self.conditions_path)

            conn = sqlite3.connect(DATABASE)
            self.df = pd.read_sql('SELECT "NCT Number" FROM trials', conn)
            conn.close()

            return

        try:
            print("Generowanie osadzeń...")
            conn = sqlite3.connect(DATABASE)
            full_df = pd.read_sql(
                'SELECT "NCT Number", "Study Title", "Brief Summary", "Conditions" FROM trials',
                conn,
            )
            conn.close()

            # Przygotowanie tekstu
            full_df["Combined_Text"] = (
                full_df["Study Title"].fillna("")
                + " "
                + full_df["Brief Summary"].fillna("")
            )

            # Słownik podpowiedzi
            self.unique_conditions = list(
                set(
                    full_df["Conditions"]
                    .str.split("|")
                    .explode()
                    .str.strip("., ")
                    .str.capitalize()
                    .dropna()
                )
            )

            # Generowanie osadzeń
            sentences = full_df["Combined_Text"].tolist()
            self.matrix = self.model.encode(sentences, convert_to_tensor=True)
            self.df = full_df[["NCT Number"]]

            # Zapisanie na dysk
            joblib.dump(self.matrix, self.matrix_path)
            joblib.dump(self.unique_conditions, self.conditions_path)
            print("Osadzenia zostały wygenerowane i zapisane")
        except Exception as e:
            print(f"Błąd podczas generowania osadzeń: {e}")
            self.df = pd.DataFrame()

    def get_relevant_ids(self, query_text, top_n=50):
        """Wyszukiwanie semantyczne (miara cosinusowa)"""
        if not query_text or self.matrix is None:
            return []

        try:
            # Zwektoryzowanie zapytania
            query_vec = self.model.encode(query_text, convert_to_tensor=True)

            # Obliczenie podobieństwa cosinusowego
            cosine_scores = util.cos_sim(query_vec, self.matrix)[0]

            # Pobranie indeksów najlepszych wyników
            top_results = torch.topk(cosine_scores, k=min(top_n, len(cosine_scores)))
            indices = top_results.indices.tolist()

            return self.df.iloc[indices]["NCT Number"].tolist()
        except Exception as e:
            print(f"Błąd wyszukiwania semantycznego: {e}")
            return []

    def get_suggestion(self, query_text):
        """Zwraca sugestię poprawki (odległość Levenshteina)"""
        if not query_text or not self.unique_conditions:
            return None

        # Znalezienie najlepszego dopasowania
        best_match, score = process.extractOne(
            query_text, self.unique_conditions, scorer=fuzz.WRatio
        )

        # Przedział punktowy dla sugestii literówek
        if 80 <= score <= 95:
            return best_match

        return None


search_engine = SearchEngine()
