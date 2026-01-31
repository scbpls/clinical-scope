import os
import sqlite3
import pandas as pd

DATABASE = os.path.join("instance", "clinical_trials.db")

# Stworzenie katalogu instancji
if not os.path.exists("instance"):
    os.makedirs("instance")

# Wczytanie danych
df1 = pd.read_csv("data/cancer.csv")
df2 = pd.read_csv("data/diabetes.csv")
df3 = pd.read_csv("data/heart.csv")

# Połączenie danych
full_df = pd.concat([df1, df2, df3])

# Usunięcie diplikatów
full_df = full_df.drop_duplicates(subset=["NCT Number"])

# Zapisanie do bazy danych
print("Zapisywanie danych do bazy...")
conn = sqlite3.connect(DATABASE)
full_df.to_sql("trials", conn, if_exists="replace", index=False)
conn.close()

print("Baza danych gotowa!")
