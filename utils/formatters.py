from textblob import TextBlob


def clean_text(text):
    """Czyści surowy tekst z separatorów i podkreślników"""
    if not text:
        return ""

    text = text.replace("_", " ")

    separators = ["|", "/"]

    for sep in separators:
        if sep in text:
            parts = [p.strip() for p in text.split(sep) if p.strip()]

            text = ", ".join(parts)

    return text


def translate_complex_text(text, mapping):
    """Tłumaczy tekst używając mapowania, zachowując separatory"""
    if not text:
        return ""

    if text in mapping:
        return mapping[text]

    separators = ["|", "/", ","]

    for sep in separators:
        if sep in text:
            parts = text.split(sep)

            translated_parts = [
                mapping.get(p.strip(), p.strip()) for p in parts if p.strip()
            ]

            return ", ".join(translated_parts)

    return mapping.get(text, text)


def clean_locations(text):
    """Wyciąga nazwy lokalizacji"""
    if not text:
        return ""

    unique_countries = set()
    sites = text.split("|")

    for site in sites:
        parts = site.split(",")

        if parts:
            country = parts[-1].strip()

            # Usunięcie danych kontaktowych
            if (
                country
                and not any(char.isdigit() for char in country)
                and "Contact" not in country
            ):
                unique_countries.add(country)

    if not unique_countries:
        return text[:100] + "..." if len(text) > 100 else text

    return ", ".join(sorted(list(unique_countries)))


def get_sentiment_info(text):
    """Analizuje wydźwięk tekstu"""
    if not text or len(text) < 10:
        return {"label": "Neutralny", "class": "is-light", "icon": "fa-minus"}

    analysis = TextBlob(text)
    score = analysis.sentiment.polarity  # od -1.0 (negatywny) do 1.0 (pozytywny)

    if score > 0.1:
        return {
            "label": "Obiecujący",
            "class": "is-success is-light",
            "icon": "fa-face-smile",
        }
    elif score < -0.1:
        return {
            "label": "Wymaga uwagi",
            "class": "is-danger is-light",
            "icon": "fa-triangle-exclamation",
        }
    else:
        return {
            "label": "Neutralny",
            "class": "is-white border-grey",
            "icon": "fa-circle-info",
        }
