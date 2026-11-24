# ServiceApp - Generator stron SEO na miasto + usluge
# Bot tylko przygotowuje wersje robocza, nic nie publikuje sam

from datetime import date

CITIES = [
    {"city": "Sao Paulo", "state": "SP", "areas": ["Pinheiros", "Vila Mariana", "Moema", "Jardins", "Tatuape", "Barra Funda"]},
    {"city": "Rio de Janeiro", "state": "RJ", "areas": ["Copacabana", "Barra da Tijuca", "Botafogo", "Tijuca", "Ipanema", "Centro"]},
    {"city": "Belo Horizonte", "state": "MG", "areas": ["Savassi", "Centro", "Buritis", "Pampulha"]},
    {"city": "Curitiba", "state": "PR", "areas": ["Batel", "Centro", "Agua Verde", "Boa Vista"]},
    {"city": "Porto Alegre", "state": "RS", "areas": ["Moinhos de Vento", "Centro", "Petropolis", "Boa Vista"]},
]

SERVICES = [
    {"service": "eletricista", "question": "Quanto custa um eletricista"},
    {"service": "encanador", "question": "Quanto custa um encanador"},
    {"service": "limpeza", "question": "Quanto custa limpeza residencial"},
    {"service": "diarista", "question": "Como contratar diarista"},
    {"service": "pintor", "question": "Quanto custa pintar apartamento"},
    {"service": "pedreiro", "question": "Como contratar pedreiro"},
]

def get_todays_page():
    today = date.today()
    city = CITIES[today.toordinal() % len(CITIES)]
    service = SERVICES[today.toordinal() % len(SERVICES)]
    return city, service

def make_seo_page():
    city, service = get_todays_page()
    city_name = city["city"]
    areas = ", ".join(city["areas"][:3])
    s = service["service"]
    q = service["question"]

    page = f"""
TYTUL SEO: {s.capitalize()} em {city_name} - {city["state"]} | ServiceApp

META OPIS: Precisa de {s} em {city_name}? Veja prestadores verificados em {areas}, pecao orcamento em 10-20 segundos, sem mensalidade. Baixe ServiceApp.

H1: {s.capitalize()} em {city_name} - {city["state"]}

WSTEP:
Precisa de {s} hoje em {city_name}? Em bairros como {areas} tem muitos prestadores, mas o preco e a qualidade mudam muito.
Aqui voce aprende como escolher e como pedir orcamento rapido pelo ServiceApp.

H2: {q} em {city_name}?
O valor depende do tipo de servico, da urgencia e do bairro. Peca 2-3 orcamentos, pergunta se a visita esta inclusa e se o material esta incluso.

H2: Como escolher {s} em {city_name}?
1. Confira avaliacao e foto de servico parecido
2. Pergunta se atende hoje em {city["areas"][0]}
3. Pergunta valor fechado, nao so por hora

H2: Areas atendidas em {city_name}
{areas} e toda a cidade de {city_name} - {city["state"]}.

H2: FAQ
P: O ServiceApp cobra mensalidade? O: Nao, sem mensalidade, sem % do servico.
P: Como pedir? O: Crie solicitacao em 10-20 segundos, escolha grupo e tipo de servico.
P: E seguro? O: Prestadores verificados, com avaliacao.

CTA NA KONCU:
Baixe ServiceApp, crie sua solicitacao e receba orcamentos de prestadores verificados em {city_name}.
Conta oficial ServiceApp
"""
    return page

if __name__ == "__main__":
    print(make_seo_page())
    print("\n--- KONIEC ---")
    print("Skopiuj, sprawdz i wklej jako nowa strona lub artykul.")
