# ClinicalScope - Inteligentna wyszukiwarka badań klinicznych

Aplikacja webowa służąca do semantycznego przeszukiwania baz danych badań klinicznych (nowotwory, cukrzyca, choroby serca)

## 1. Konfiguracja

### 1.1 Przygotowanie środowiska

```bash
python -m venv .venv
source .venv/bin/activate # Linux/macOS
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 1.2. Inicjalizacja bazy danych i modeli

```bash
# Wczytanie danych z plików CSV do bazy danych w folderze /instance
python init_db.py

# Pierwszy start wygeneruje modele osadzeń w folderze /models
python app.py
```

### 1.3. Uruchomienie

Aplikacja będzie dostępna pod adresem: http://127.0.0.1:5000

## 2. Technologie

- **Backend**:
  - **Flask** - Serwer aplikacji i obsługa logiki
  - **Flask-Caching** - Optymalizacja wydajności poprzez buforowanie wyników wyszukiwania, tłumaczeń i statystyk

- **Baza danych**:
  - **SQLite** - Relacyjna baza danych przechowująca ponad 25 000 rekordów.

- **Silniki danych**:
  - `intfloat/multilingual-e5-small` - Modedl o generowania osadzeń semantycznych
  - **TextBlob** - Analiza polaryzacji tekstu w celu wyznaczenia sentymentu badań
  - **TheFuzz** - Implementacja algorytmu odległości Levenshteina do korekty literówek zapytań
  - **Google Translate API** (`deep-translator`) - Obsługa wielojęzyczności wyników

- **Frontend**:
  - **Bulma CSS** - Responsywna biblioteka UI
  - **Chart.js** - Interaktywne wizualizacje danych z obsługą wtyczek zoom i pan
  - **FontAwesome** - Ikony

## 3. Spełnione kryteria projektowe (133 pkt)

### Architektura i dane (47 pkt)

| Kryterium            | Opis techniczny                                                                                            | Punkty |
| :------------------- | :--------------------------------------------------------------------------------------------------------- | :----- |
| **Aplikacja webowa** | Implementacja backendu w oparciu o framework **Flask**                                                     | 15 pkt |
| **Baza danych**      | Przechowywanie ponad **25 000 rekordów** w relacyjnej bazie **SQLite**                                     | 20 pkt |
| **Źródła danych**    | Pobranie danych z oficjalnego repozytorium **ClinicalTrials.gov**                                          | 5 pkt  |
| **Cechy rekordów**   | Przetwarzanie **18 unikatowych cech** (13 z głównego źródła danych + 5 wygenerowanych dynamicznie)         | 4 pkt  |
| **Jakość danych**    | Tworzenie ulepszonego pola do wyszukiwania, normalizacja lokalizacji oraz wygenerowanie etykiet sentymentu | 3 pkt  |

### Wyszukiwanie (31 pkt)

| Kryterium                | Metodologia                                                                                                        | Punkty |
| :----------------------- | :----------------------------------------------------------------------------------------------------------------- | :----- |
| **Nadawanie wag termom** | Wykorzystanie osadzeń (**embeddings**) modelu E5 oraz trwały **zapis wektorów** do plików `.joblib`                | 15 pkt |
| **Podobieństwo zapytań** | Ocena relewancji z wykorzystaniem **miary cosinusowej**                                                            | 5 pkt  |
| **Korekta błędów**       | Implementacja **odległości Levenshteina** do proponowania korekt w nazwach schorzeń                                | 5 pkt  |
| **Filtrowanie**          | Wykorzystanie **6 filtrów** (słowa kluczowe, status badania, faza badania, typ badania, grupowa wiekowa oraz płeć) | 6 pkt  |

### Analiza i generowanie tekstów (30 pkt)

| Kryterium              | Metodologia                                                                                                                      | Punkty |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------------------- | :----- |
| **Analiza sentymentu** | Automatyczne ocenianie rokowań badań na podstawie polaryzacji opisu za pomocą biblioteki **TextBlob**                            | 10 pkt |
| **Generowanie opisów** | Tworzenie etykiet statusu rokowań badań na podstawie analizy sentymentu                                                          | 10 pkt |
| **Wielojęzyczność**    | Tłumaczenie treści (tytuły, opisy, interwencje oraz lokalizacje) na **język polski** przy wykorzystaniu **API Google Translate** | 10 pkt |

### Wizualizacja i optymalizacja (25 pkt)

| Kryterium            | Metodologia                                                                                                                     | Punkty |
| :------------------- | :------------------------------------------------------------------------------------------------------------------------------ | :----- |
| **Typy wykresów**    | **Wykres liniowy** (dynamika badań), **słupkowy** (fazy badań i liczebność schorzeń) oraz **kołowy** (wielkość grup badawczych) | 12 pkt |
| **Interaktywność**   | Pełna obsługa podpowiedzi na wykresach oraz funkcji przybliżania i oddalania na osiach czasu                                    | 8 pkt  |
| **Pamięć podręczna** | Optymalizacja wydajności przez system **Flask Caching** dla wyników wyszukiwania, tłumaczeń i statystyk                         | 5 pkt  |

## 4. Struktura katalogów

```
clinical-scope/
├── data/                        # Surowe dane źródłowe
│   ├── cancer.csv               # Dane dot. nowotworów
│   ├── diabetes.csv             # Dane dot. cukrzycy
│   └── heart.csv                # Dane dot. chorób serca
├── instance/                    # Instancja bazy danych (generowana lokalnie)
│   └── clinical_trials.db       # Relacyjna baza danych SQLite
├── models/                      # Modele ML i zserializowane dane (generowane lokalnie)
│   ├── embeddings_matrix.joblib # Macierz wektorów osadzeń
│   └── unique_conditions.joblib # Lista unikalnych schorzeń
├── services/                    # Rdzeń logiki biznesowej aplikacji
│   ├── database.py              # Obsługa zapytań SQL i połączeń z bazą
│   └── search.py                # Silnik wyszukiwania semantycznego
├── static/                      # Zasoby statyczne
│   └── css/
│       └── style.css            # Style UI i zmienne systemowe CSS
├── templates/                   # Widoki aplikacji
│   ├── base.html                # Główny układ i importy bibliotek
│   ├── index.html               # Strona główna z wyszukiwarką i filtrami
│   └── stats.html               # Dashboard z interaktywnymi wykresami
├── utils/                       # Słowniki i funkcje pomocnicze
│   ├── dictionaries.py          # Mapowania dla wielojęzyczności i filtrów
│   └── formatters.py            # Formatory danych
├── app.py                       # Serce aplikacji, obsługa tras i pamięci podręcznej
├── init_db.py                   # Skrypt inicjalizujący bazę danych
├── README.md                    # Dokumentacja projektu
└── requirements.txt             # Lista zależności projektu
```
