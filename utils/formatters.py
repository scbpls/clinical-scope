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

            # Przetłumaczenie każdego kawałka osobno
            translated_parts = [
                mapping.get(p.strip(), p.strip()) for p in parts if p.strip()
            ]

            return ", ".join(translated_parts)

    return mapping.get(text, text)


def clean_locations(text):
    """Wyciąga nazwy krajów z lokalizacji"""
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
