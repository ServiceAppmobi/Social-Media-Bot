# ServiceApp - Generator wersji roboczych na kazdy dzien
# Bot tylko przygotowuje, nic nie wysyla sam

from datetime import date
from instagram_groups import GROUPS
from ai_prompt import build_prompt, NEIGHBORHOODS

# Rotacja: dzien 1 Sao Paulo, dzien 2 Rio, dzien 3 Brasiliana, i tak w kolko
def get_todays_group():
    today = date.today()
    index = today.toordinal() % len(GROUPS)
    return GROUPS[index]

def make_draft():
    group = get_todays_group()
    city = group["city"]
    topic = group["topics"][0]
    # Przykladowe pytanie z grupy, w prawdziwym uzyciu podmieniasz na prawdziwe pytanie
    question = f"Preciso de {topic} hoje em {city}, como escolher?"
    prompt = build_prompt(group["name"], city, topic, question)

    neighborhoods = NEIGHBORHOODS.get(city, ["Centro"])
    draft = f"""
GRUPA: {group["name"]}
MIASTO: {city}
DZIELNICA DO UZYCIA: {neighborhoods[0]}
TEMAT: {topic}

PROMPT DLA AI:
{prompt}

WERSJA ROBOCZA DO ZATWIERDZENIA:
Oi! Para {topic} em {city}, vale pedir 2-3 orcamentos e conferir avaliacao e foto do servico.
Pergunta se atende hoje em {neighborhoods[0]}, qual e o valor da visita e se o material esta incluso.
Se voce quiser, pode ver prestadores verificados em {city} no ServiceApp, link na bio.
Conta oficial ServiceApp
"""
    return draft

if __name__ == "__main__":
    print(make_draft())
    print("\n--- KONIEC ---")
    print("Skopiuj wersje robocza, sprawdz i wklej do grupy na Instagramie.")
