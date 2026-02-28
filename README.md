# ClinicalScope - Intelligent clinical trials search engine

A web application for semantic search of clinical trials databases (cancer, diabetes, heart diseases)

## 1. Configuration

### 1.1 Environment setup

```bash
python -m venv .venv
source .venv/bin/activate # Linux/macOS
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 1.2. Database and models initialization

```bash
# Load data from CSV files into the database in the /instance folder
python init_db.py

# The first start will generate embedding models in the /models folder
python app.py
```

### 1.3. Running

The application will be available at: http://127.0.0.1:5000

## 2. Technologies

- **Backend**:
  - **Flask** - Application server and logic handling
  - **Flask-Caching** - Performance optimization through caching of search results, translations and statistics

- **Baza danych**:
  - **SQLite** - Relational database storing over 160,000 records

- **Silniki danych**:
  - `intfloat/multilingual-e5-small` - Model for generating semantic embeddings
  - **TextBlob** - Text polarity analysis to determine trial sentiment
  - **TheFuzz** - Implementation of the Levenshtein distance algorithm to correct query typos
  - **Google Translate API** (`deep-translator`) - Multilingual results support

- **Frontend**:
  - **Bulma CSS** - Responsive UI library
  - **Chart.js** - Interactive data visualizations with zoom and pan plugin support
  - **FontAwesome** - Icons

## 3. Key features

### Architecture and data

| Feature             | Technical description                                                                      |
| :------------------ | :----------------------------------------------------------------------------------------- |
| **Web application** | Backend implementation based on the **Flask** framework                                    |
| **Database**        | Storing over **160,000 records** in a relational **SQLite** database                       |
| **Data sources**    | Fetching data from the official **ClinicalTrials.gov** repository                          |
| **Record features** | Processing **18 unique features** (13 from the main data source + 5 dynamically generated) |
| **Data quality**    | Creating an enhanced search field, normalizing locations and generating sentiment labels   |

### Search

| Feature              | Methodology                                                                                       |
| :------------------- | :------------------------------------------------------------------------------------------------ |
| **Term weighting**   | Utilization of E5 model **embeddings** and persistent **vector storage** in `.joblib` files       |
| **Query similarity** | Relevance assessment using the **cosine similarity measure**                                      |
| **Error correction** | Implementation of **Levenshtein distance** to propose corrections in condition names              |
| **Filtering**        | Utilization of **6 filters** (keywords, study status, study phase, study type, age group and sex) |
| **Data export**      | Downloading the currently displayed page of search results to a **CSV file**                      |

### Analysis and text generation

| Feature                    | Methodology                                                                                                                                 |
| :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| **Sentiment analysis**     | Automated assessment of trial prognoses based on description polarity using the **TextBlob** library                                        |
| **Description generation** | Creating trial prognosis status labels based on sentiment analysis                                                                          |
| **Multilingualism**        | Native **Polish** user interface with an on-demand option to translate selected content into **English** using the **Google Translate API** |

### Visualization and optimization

| Feature           | Methodology                                                                                                                    |
| :---------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Chart types**   | **Line chart** (trials dynamics), **bar chart** (trial phases and condition frequencies) and **pie chart** (study group sizes) |
| **Interactivity** | Full support for chart tooltips and zoom in/out functions on timelines                                                         |
| **Caching**       | Performance optimization via the **Flask Caching** system for search results, translations and statistics                      |

## 4. Struktura katalogów

```
clinical-scope/
├── data/                        # Raw source data
│   ├── cancer.csv               # Data regarding cancer
│   ├── diabetes.csv             # Data regarding diabetes
│   └── heart.csv                # Data regarding heart diseases
├── instance/                    # Database instance (generated locally)
│   └── clinical_trials.db       # Relational SQLite database
├── models/                      # ML models and serialized data (generated locally)
│   ├── embeddings_matrix.joblib # Embeddings vector matrix
│   └── unique_conditions.joblib # List of unique conditions
├── services/                    # Core application business logic
│   ├── database.py              # Handling SQL queries and database connections
│   └── search.py                # Semantic search engine
├── static/                      # Static assets
│   └── css/
│       └── style.css            # UI styles and CSS system variables
├── templates/                   # Application views
│   ├── base.html                # Main layout and library imports
│   ├── index.html               # Home page with search engine and filters
│   └── stats.html               # Dashboard with interactive charts
├── utils/                       # Dictionaries and helper functions
│   ├── dictionaries.py          # Mappings for multilingualism and filters
│   └── formatters.py            # Data formatters
├── app.py                       # Application heart, routes handling and caching
├── init_db.py                   # Database initialization script
├── README.md                    # Project documentation
└── requirements.txt             # List of project dependencies
```
