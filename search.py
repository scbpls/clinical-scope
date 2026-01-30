import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

DATABASE = "clinical_trials.db"


class SearchEngine:
    def __init__(self):
        self.vectorizer = None
        self.matrix = None
        self.df = None

        print("Ładowanie danych i trenowanie modelu TF-IDF...")
        self._load_and_train()
        print("Model gotowy!")

    def _load_and_train(self):
        try:
            conn = sqlite3.connect(DATABASE)
            self.df = pd.read_sql(
                'SELECT "NCT Number", "Study Title", "Brief Summary" FROM trials', conn
            )
            conn.close()

            self.df["Combined_Text"] = (
                self.df["Study Title"].fillna("")
                + " "
                + self.df["Brief Summary"].fillna("")
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


search_engine = SearchEngine()
