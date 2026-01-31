import sqlite3
import pandas as pd

# Wczytanie danych
df1 = pd.read_csv("data/cancer.csv")
df2 = pd.read_csv("data/diabetes.csv")
df3 = pd.read_csv("data/heart.csv")

# Połączenie danych
full_df = pd.concat([df1, df2, df3])

# Usunięcie diplikatów
full_df = full_df.drop_duplicates(subset=["NCT Number"])
print(f"Liczba unikalnych badań: {len(full_df)}")

# Zapisanie do bazy danych
conn = sqlite3.connect("clinical_trials.db")
full_df.to_sql("trials", conn, if_exists="replace", index=False)
conn.close()

print("Baza danych gotowa")
