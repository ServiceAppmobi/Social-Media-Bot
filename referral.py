# referral.py - ServiceApp Program Polecen - wersja automatyczna
# Nic nie musisz edytowac recznie. Bot sam generuje dla kazdego miasta.

REFERRAL_BASE = "https://serviceapp.mobi/download?ref="

# Miasta i uslugi - bot sam robi kombinacje
CITIES = [
    ("sao-paulo", "Sao Paulo", "pt"),
    ("rio", "Rio de Janeiro", "pt"),
    ("belo-horizonte", "Belo Horizonte", "pt"),
    ("curitiba", "Curitiba", "pt"),
    ("meksyk", "Ciudad de Mexico", "es"),
]

SERVICES = [
    ("eletricista", "eletricista", "electricista"),
    ("encanador", "encanador", "plomero"),
    ("faxina", "faxina", "limpieza"),
]

def referral_link(slug):
    return REFERRAL_BASE + slug

if __name__ == "__main__":
    print("## ServiceApp - Program Polecen - gotowe do skopiowania")
    print("")
    print("Zasady: Fachowiec poleca klientowi. Klient pobiera z jego linku. Fachowiec dostaje pierwszenstwo do kolejnych leadow. Bez pieniedzy, bez prowizji.")
    print("")
    for city_slug, city_name, lang in CITIES:
        for pt_service, pt_name, es_name in SERVICES:
            if lang == "es":
                service_name = es_name
                slug = city_slug + "-" + es_name
                text = "Hola, soy prestador de " + city_name + ", " + service_name + ". Yo uso ServiceApp para recibir leads exclusivos, sin competencia por precio y sin comision sobre el pedido. Descarga gratis y pide tu servicio conmigo: " + referral_link(slug) + " Cuenta oficial ServiceApp"
            else:
                service_name = pt_name
                slug = city_slug + "-" + pt_name
                text = "Ola, sou prestador de " + city_name + ", " + service_name + ". Eu uso ServiceApp para receber leads exclusivos, sem competicao por preco e sem comissao sobre o pedido. Baixe gratis e peca seu servico comigo: " + referral_link(slug) + " Conta oficial ServiceApp"
            print("### " + city_name + " - " + service_name)
            print("Link: " + referral_link(slug))
            print("Tekst do wklejenia:")
            print(text)
            print("Zaloguj do publikacji: https://www.instagram.com/direct/inbox/")
            print("")
    print("Zaloguj do sprawdzenia pobran: https://serviceapp.mobi/")
