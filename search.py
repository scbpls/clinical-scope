import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from thefuzz import process, fuzz

DATABASE = "clinical_trials.db"


class SearchEngine:
    def __init__(self):
        self.vectorizer = None
        self.matrix = None
        self.df = None
        self.unique_conditions = []

        self._load_and_train()

    def _load_and_train(self):
        try:
            conn = sqlite3.connect(DATABASE)
            self.df = pd.read_sql(
                'SELECT "NCT Number", "Study Title", "Brief Summary" FROM trials', conn
            )
            cond_df = pd.read_sql("SELECT Conditions FROM trials", conn)
            conn.close()

            self.df["Combined_Text"] = (
                self.df["Study Title"].fillna("")
                + " "
                + self.df["Brief Summary"].fillna("")
            )

            self.unique_conditions = list(
                set(
                    cond_df["Conditions"]
                    .str.split("|")
                    .explode()
                    .str.strip("., ")
                    .str.capitalize()
                    .dropna()
                )
            )

            self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
            self.matrix = self.vectorizer.fit_transform(self.df["Combined_Text"])
        except Exception:
            self.df = pd.DataFrame()

    def get_relevant_ids(self, query_text, top_n=50):
        """Zwraca listę ID badań najlepiej pasujących do zapytania"""
        if not query_text or self.vectorizer is None:
            return []

        try:
            query_vec = self.vectorizer.transform([query_text])
            cosine_sim = linear_kernel(query_vec, self.matrix).flatten()
            # Posortowanie wyników malejąco po trafności
            related_docs_indices = cosine_sim.argsort()[: -top_n - 1 : -1]

            return self.df.iloc[related_docs_indices]["NCT Number"].tolist()
        except Exception:
            return []

    def get_suggestion(self, query_text):
        """Zwraca sugestię poprawki"""
        if not query_text or not self.unique_conditions:
            return None

        best_match, score = process.extractOne(
            query_text, self.unique_conditions, scorer=fuzz.WRatio
        )

        if 80 <= score <= 95:
            return best_match

        return None


search_engine = SearchEngine()
