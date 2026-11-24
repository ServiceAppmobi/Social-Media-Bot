# ServiceApp - Prompt dla AI do pisania postow
# Bot tylko przygotowuje wersje robocze, nic nie wysyla sam

NEIGHBORHOODS = {
    "Sao Paulo": ["Pinheiros", "Vila Mariana", "Moema", "Jardins", "Tatuape", "Barra Funda"],
    "Rio de Janeiro": ["Copacabana", "Barra da Tijuca", "Botafogo", "Tijuca", "Ipanema", "Centro"],
    "Brasil": ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]
}

# Zasady dla AI - wazne, zeby nie zablokowalo
AI_RULES = """
1. Pisz po portugalsku brazylijskim, pt-BR, prosto i ludzko.
2. 80% tekstu to prawdziwa pomoc, konkretna rada.
3. 20% to 1 zdanie zaproszenia do ServiceApp, bez nachalnej reklamy.
4. Nie wstawiaj linku w poscie, tylko zdanie: link w bio.
5. Nie udawaj zwyklego uzytkownika, nie wymyslaj falszywych opinii.
6. Na koncu zawsze: Conta oficial ServiceApp
7. Kazdy post inny, inne slowa, inne dzielnice, bez kopiuj wklej.
"""

def build_prompt(group_name, city, topic, question):
    # group_name: nazwa grupy z instagram_groups.py
    # city: Sao Paulo, Rio de Janeiro albo Brasil
    # topic: np. eletricista Sao Paulo
    # question: pytanie z grupy
    prompt = f"""
Jesteś asystentem oficjalnego konta ServiceApp.
Grupa: {group_name}
Miasto: {city}
Temat: {topic}
Pytanie z grupy: {question}

Napisz odpowiedz po pt-BR, ktora:
- najpierw pomaga, daje 3 konkretne rady
- wspomina 1 dzielnice z miasta: {city}
- na koncu ma 1 zdanie: mozesz tez sprawdzic zweryfikowanych prestadores w ServiceApp, link w bio
- na samym koncu: Conta oficial ServiceApp

Zasady:
{AI_RULES}
"""
    return prompt

# Przyklad, jak to wyglada dla Sao Paulo
EXAMPLE_SAO_PAULO = """
Pytanie: Preciso de eletricista hoje em Pinheiros, quanto custa?

Odpowiedz robocza:
Oi! Em Pinheiros, para um servico simples de eletricista, vale pedir 2-3 orcamentos e conferir se o profissional tem avaliacao e foto do servico.
Pergunta se ele atende hoje, qual e o valor da visita e se o material esta incluso.
Se voce quiser, pode ver prestadores verificados em Sao Paulo no ServiceApp, link na bio.
Conta oficial ServiceApp
"""
