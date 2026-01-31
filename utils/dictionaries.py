statuses_map = {
    "ACTIVE_NOT_RECRUITING": "Aktywne (zamknięta)",
    "APPROVED_FOR_MARKETING": "Zatwierdzone do obrotu",
    "AVAILABLE": "Dostępne",
    "COMPLETED": "Zakończone",
    "ENROLLING_BY_INVITATION": "Na zaproszenie",
    "NOT_YET_RECRUITING": "Jeszcze nie rekrutuje",
    "NO_LONGER_AVAILABLE": "Już niedostępne",
    "RECRUITING": "Rekrutacja otwarta",
    "SUSPENDED": "Zawieszone",
    "TEMPORARILY_NOT_AVAILABLE": "Tymczasowo niedostępne",
    "TERMINATED": "Przerwane",
    "UNKNOWN": "Status nieznany",
    "WITHDRAWN": "Wycofane",
}

phases_map = {
    "EARLY_PHASE1": "Wczesna faza 1",
    "PHASE1": "Faza 1",
    "PHASE2": "Faza 2",
    "PHASE3": "Faza 3",
    "PHASE4": "Faza 4",
}

types_map = {
    "EXPANDED_ACCESS": "Rozszerzony dostęp",
    "INTERVENTIONAL": "Interwencyjne",
    "OBSERVATIONAL": "Obserwacyjne",
}

age_map = {"CHILD": "Dzieci", "ADULT": "Dorośli", "OLDER_ADULT": "Seniorzy"}

sex_map = {"ALL": "Wszystkie", "FEMALE": "Kobiety", "MALE": "Mężczyźni"}

statuses_colors_map = {
    # Pozytywne
    "APPROVED_FOR_MARKETING": "is-success is-light",
    "AVAILABLE": "is-success is-light",
    "RECRUITING": "is-success is-light",
    # Informacyjne
    "ACTIVE_NOT_RECRUITING": "is-info is-light",
    "COMPLETED": "is-info is-light",
    "ENROLLING_BY_INVITATION": "is-info is-light",
    # Negatywne
    "NO_LONGER_AVAILABLE": "is-danger is-light",
    "SUSPENDED": "is-danger is-light",
    "TERMINATED": "is-danger is-light",
    "WITHDRAWN": "is-danger is-light",
    # Ostrzegające
    "NOT_YET_RECRUITING": "is-warning is-light",
    "TEMPORARILY_NOT_AVAILABLE": "is-warning is-light",
    # Nieznane
    "UNKNOWN": "is-white border-grey",
}
