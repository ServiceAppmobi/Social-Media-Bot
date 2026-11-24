# translator.py - ServiceApp Translator BR <-> MX <-> PL
# Bezpieczna automatyzacja: tylko przygotowuje wersje robocze, nic nie publikuje.
# Ty akceptujesz i wklejasz recznie.

# 1. OFICJALNY DOPISek - zawsze taki sam
DISCLOSURE = {
    "pt": "Conta oficial ServiceApp",
    "es": "Cuenta oficial ServiceApp",
    "pl": "Konto oficjalne ServiceApp",
}

# 2. SLOWNICZEK ServiceApp - te zdania zawsze tlumaczymy tak samo
# Klucz po portugalsku -> wersja hiszpanska i polska
GLOSSARY = [
    {
        "pt": "leads exclusivos",
        "es": "leads exclusivos",
        "pl": "ekskluzywne zlecenia",
    },
    {
        "pt": "sem competicao por preco",
        "es": "sin competencia por precio",
        "pl": "bez konkurencji cenowej",
    },
    {
        "pt": "so quem aceita o pedido recebe os detalhes",
        "es": "solo quien acepta el pedido recibe los detalles",
        "pl": "tylko ten kto zaakceptuje zlecenie dostaje szczegoly",
    },
    {
        "pt": "app gratis",
        "es": "app gratis",
        "pl": "darmowa aplikacja",
    },
    {
        "pt": "sem assinatura",
        "es": "sin suscripcion",
        "pl": "bez abonamentu",
    },
    {
        "pt": "sem comissao sobre o pedido",
        "es": "sin comision sobre el pedido",
        "pl": "bez prowizji od zlecenia",
    },
    {
        "pt": "voce nao precisa procurar prestadores",
        "es": "no necesitas buscar prestadores",
        "pl": "nie musisz szukac fachowcow",
    },
    {
        "pt": "o app faz isso por voce",
        "es": "la app lo hace por ti",
        "pl": "aplikacja robi to za Ciebie",
    },
    {
        "pt": "espera minima",
        "es": "espera minima",
        "pl": "minimalne oczekiwanie",
    },
    {
        "pt": "se o prestador aceitar o pedido, ele entra em contato imediatamente",
        "es": "si el prestador acepta el pedido, te contacta de inmediato",
        "pl": "jak fachowiec zaakceptuje zlecenie, od razu sie z Toba kontaktuje",
    },
]

# 3. SZYBKIE TLUMACZENIE slowniczkiem - podmienia tylko znane zdania
def translate_with_glossary(text, target="es"):
    result = text
    for item in GLOSSARY:
        if target == "es":
            result = result.replace(item["pt"], item["es"])
        if target == "pl":
            result = result.replace(item["pt"], item["pl"])
    # Podmien dopisek na koncu
    if target == "es":
        result = result.replace(DISCLOSURE["pt"], DISCLOSURE["es"])
    if target == "pl":
        result = result.replace(DISCLOSURE["pt"], DISCLOSURE["pl"])
    return result

# 4. GOTOWY PROMPT DO AI - wklejasz go do Meta AI i dostajesz pelne tlumaczenie
def build_ai_prompt(text, target="es"):
    if target == "es":
        lang_name = "hiszpanski dla Meksyku, prosty, grzeczny, bez slangu"
        disclosure = DISCLOSURE["es"]
    else:
        lang_name = "polski, prosty, grzeczny"
        disclosure = DISCLOSURE["pl"]

    glossary_text = "\n".join([f"- {g['pt']} -> {g[target]}" for g in GLOSSARY])

    return f"""Przetlumacz ten post ServiceApp na {lang_name}.
Zachowaj sens, krotkie zdania, max 1-2 posty dziennie, dzien, ton pomocny.
Nie dodawaj obietnic, cen, ani falszywych opinii.
Uzyj dokladnie tych zwrotow z slowniczka:
{glossary_text}
Na koncu dodaj: {disclosure}

Tekst do przetlumaczenia:
{text}
"""

# 5. WSZYSTKIE 3 WERSJE NA RAZ
def make_all_versions(draft_pt):
    return {
        "pt": draft_pt,
        "es": translate_with_glossary(draft_pt, "es"),
        "pl": translate_with_glossary(draft_pt, "pl"),
        "prompt_es": build_ai_prompt(draft_pt, "es"),
        "prompt_pl": build_ai_prompt(draft_pt, "pl"),
    }

# 6. PRZYKLAD - TU WKLEJASZ SWOJ TEKST
# Jak chcesz przetlumaczyc nowy post, podmien tylko ten tekst ponizej
DRAFT_PT = """Precisa de um eletricista em Sao Paulo? Voce nao precisa procurar prestadores, o app faz isso por voce. Espera minima. Se o prestador aceitar o pedido, ele entra em contato imediatamente. App gratis, sem assinatura, sem comissao sobre o pedido. Conta oficial ServiceApp"""

if __name__ == "__main__":
    versions = make_all_versions(DRAFT_PT)
    print("=== BR - PORTUGUES ===")
    print(versions["pt"])
    print("\n=== MX - HISZPANSKI - wersja robocza ===")
    print(versions["es"])
    print("\n=== PL - POLSKI - do sprawdzenia ===")
    print(versions["pl"])
    print("\n=== PROMPT DO AI - HISZPANSKI - skopiuj i wklej do Meta AI ===")
    print(versions["prompt_es"])
