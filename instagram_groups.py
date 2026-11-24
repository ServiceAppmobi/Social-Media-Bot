# ServiceApp - Grupy na Instagramie
# Bot tylko przygotowuje wersje robocze, nic nie wysyla sam
# Konto oficjalne ServiceApp

GROUPS = [
    {
        "name": "ServiceApp Brasiliana / Servicos",
        "city": "Brasil",
        "language": "pt-BR",
        "topics": ["procura de prestador", "quanto custa servico", "como escolher prestador", "vaga para prestador"]
    },
    {
        "name": "ServiceApp Rio / Servicos",
        "city": "Rio de Janeiro",
        "language": "pt-BR",
        "topics": ["eletricista Rio", "encanador Rio", "limpeza Rio", "servicos urgentes Rio"]
    },
    {
        "name": "ServiceApp Sao Paulo / Servicos",
        "city": "Sao Paulo",
        "language": "pt-BR",
        "topics": ["eletricista Sao Paulo", "encanador Sao Paulo", "limpeza Sao Paulo", "servicos urgentes Sao Paulo"]
    }
]

# Zasady bezpieczne, zeby nie zablokowalo
MAX_POSTS_PER_DAY = 2
POSTING_HOURS_START = 9  # czas Sao Paulo
POSTING_HOURS_END = 21  # czas Sao Paulo
DISCLOSURE = "Conta oficial ServiceApp"
# Struktura posta: 80% pomoc, 20% zaproszenie
POST_TEMPLATE = """
Pomocna odpowiedz na pytanie, konkretna rada.
Na koncu 1 zdanie zaproszenia do ServiceApp, link w bio.
Na samym koncu: Conta oficial ServiceApp
"""
