# translator.py - ServiceApp Translator BR <-> MX <-> PL

DISCLOSURE_PT = "Conta oficial ServiceApp"
DISCLOSURE_ES = "Cuenta oficial ServiceApp"
DISCLOSURE_PL = "Konto oficjalne ServiceApp"

GLOSSARY = [
    ("leads exclusivos", "leads exclusivos", "ekskluzywne zlecenia"),
    ("sem competicao por preco", "sin competencia por precio", "bez konkurencji cenowej"),
    ("so quem aceita o pedido recebe os detalhes", "solo quien acepta el pedido recibe los detalles", "tylko ten kto zaakceptuje zlecenie dostaje szczegoly"),
    ("app gratis", "app gratis", "darmowa aplikacja"),
    ("sem assinatura", "sin suscripcion", "bez abonamentu"),
    ("sem comissao sobre o pedido", "sin comision sobre el pedido", "bez prowizji od zlecenia"),
    ("voce nao precisa procurar prestadores", "no necesitas buscar prestadores", "nie musisz szukac fachowcow"),
    ("o app faz isso por voce", "la app lo hace por ti", "aplikacja robi to za Ciebie"),
    ("espera minima", "espera minima", "minimalne oczekiwanie"),
]

def translate_with_glossary(text, target):
    result = text
    for pt, es, pl in GLOSSARY:
        if target == "es":
            result = result.replace(pt, es)
        if target == "pl":
            result = result.replace(pt, pl)
    if target == "es":
        result = result.replace(DISCLOSURE_PT, DISCLOSURE_ES)
    if target == "pl":
        result = result.replace(DISCLOSURE_PT, DISCLOSURE_PL)
    return result

def build_ai_prompt(text, target):
    if target == "es":
        lang_name = "hiszpanski dla Meksyku, prosty, grzeczny"
        disclosure = DISCLOSURE_ES
    else:
        lang_name = "polski, prosty, grzeczny"
        disclosure = DISCLOSURE_PL
    lines = []
    lines.append("Przetlumacz ten post ServiceApp na " + lang_name + ".")
    lines.append("Zachowaj sens, krotkie zdania, ton pomocny.")
    lines.append("Na koncu dodaj: " + disclosure)
    lines.append("")
    lines.append("Tekst do przetlumaczenia:")
    lines.append(text)
    return "\n".join(lines)

DRAFT_PT = "Precisa de um eletricista em Sao Paulo? Voce nao precisa procurar prestadores, o app faz isso por voce. Espera minima. App gratis, sem assinatura, sem comissao sobre o pedido. Conta oficial ServiceApp"

if __name__ == "__main__":
    es = translate_with_glossary(DRAFT_PT, "es")
    pl = translate_with_glossary(DRAFT_PT, "pl")
    print("## ServiceApp - tlumaczenia do akceptacji")
    print("")
    print("### BR - PORTUGUES")
    print(DRAFT_PT)
    print("")
    print("### MX - HISZPANSKI - wersja robocza")
    print(es)
    print("")
    print("### PL - POLSKI - do sprawdzenia")
    print(pl)
    print("")
    print("### PROMPT DO AI - HISZPANSKI - skopiuj do Meta AI")
    print(build_ai_prompt(DRAFT_PT, "es"))
