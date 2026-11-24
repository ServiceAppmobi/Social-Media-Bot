# referral.py - ServiceApp Program Polecen - Element 2
# Tylko przygotowuje teksty i linki, nic nie publikuje samo.
# Nagroda: pierwszenstwo do leadow, nie pieniadze. Bez prowizji.

REFERRAL_BASE = "https://serviceapp.mobi/download?ref="

# PRZYKLADOWI UZYTKOWNICY - podmien na prawdziwych
# Format: slug, imie, miasto, usluga, jezyk pt lub es
USERS = [
    ("joao-sao-paulo", "Joao", "Sao Paulo", "eletricista", "pt"),
    ("maria-rio", "Maria", "Rio de Janeiro", "faxina", "pt"),
    ("carlos-meksyk", "Carlos", "Ciudad de Mexico", "plomero", "es"),
]

def referral_link(slug):
    return REFERRAL_BASE + slug

def provider_text(name, city, service, lang):
    if lang == "es":
        return "Hola, soy " + name + " de " + city + ", " + service + ". Yo uso ServiceApp para recibir leads exclusivos, sin competencia por precio y sin comision sobre el pedido. Descarga gratis y pide tu servicio conmigo: " + referral_link(name.lower().replace(" ", "-") + "-" + city.lower().replace(" ", "-")) + " Cuenta oficial ServiceApp"
    else:
        return "Ola, sou " + name + " de " + city + ", " + service + ". Eu uso ServiceApp para receber leads exclusivos, sem competicao por preco e sem comissao sobre o pedido. Baixe gratis e peca seu servico comigo: " + referral_link(name.lower().replace(" ", "-") + "-" + city.lower().replace(" ", "-")) + " Conta oficial ServiceApp"

def client_text(name, city, lang):
    if lang == "es":
        return "Hola, yo uso ServiceApp en " + city + ". No necesitas buscar prestadores, la app lo hace por ti. Espera minima. Descarga gratis aqui: " + referral_link("cliente-" + city.lower().replace(" ", "-")) + " Cuenta oficial ServiceApp"
    else:
        return "Oi, eu uso ServiceApp em " + city + ". Voce nao precisa procurar prestadores, o app faz isso por voce. Espera minima. Baixe gratis aqui: " + referral_link("cliente-" + city.lower().replace(" ", "-")) + " Conta oficial ServiceApp"

if __name__ == "__main__":
    print("## ServiceApp - Program Polecen - do akceptacji")
    print("")
    print("Zasady: Fachowiec poleca klientowi. Klient pobiera z jego linku. Fachowiec dostaje pierwszenstwo do kolejnych leadow w swoim miescie. Bez pieniedzy, bez prowizji.")
    print("")
    for slug, name, city, service, lang in USERS:
        print("### Fachowiec: " + name + " - " + city + " - " + service)
        print("Link polecajacy: " + referral_link(slug))
        print("Tekst do wklejenia w grupie / DM:")
        print(provider_text(name, city, service, lang))
        print("Zaloguj do publikacji: https://www.instagram.com/direct/inbox/")
        print("")
        print("### Klient w tym samym miescie: " + city)
        print("Tekst do wklejenia sasiadowi:")
        print(client_text(name, city, lang))
        print("Zaloguj do publikacji: https://www.instagram.com/direct/inbox/")
        print("")
    print("Zaloguj do sprawdzenia pobran: https://serviceapp.mobi/")
    print("Zaloguj do 【entity-GitHub¦canonical_name=GitHub】 tylko jak chcesz zmienic liste: https://github.com/login")
