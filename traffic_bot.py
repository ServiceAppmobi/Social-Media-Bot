# traffic_bot.py - ServiceApp Traffic Bot - efekt jak Google Ads, bez placenia Google
# Wersja automatyczna. Nic nie musisz edytowac recznie.
# Cel: te same slowa co w Google Ads, tylko organicznie.

BASE_DOWNLOAD = "https://serviceapp.mobi/download"

# 10 slow jak z Google Ads: slug, miasto, usluga po portugalsku, usluga po hiszpansku, jezyk
KEYWORDS = [
    ("eletricista-sao-paulo", "Sao Paulo", "eletricista", "electricista", "pt"),
    ("encanador-sao-paulo", "Sao Paulo", "encanador", "plomero", "pt"),
    ("faxina-sao-paulo", "Sao Paulo", "faxina", "limpieza", "pt"),
    ("eletricista-rio", "Rio de Janeiro", "eletricista", "electricista", "pt"),
    ("encanador-rio", "Rio de Janeiro", "encanador", "plomero", "pt"),
    ("faxina-rio", "Rio de Janeiro", "faxina", "limpieza", "pt"),
    ("plomero-meksyk", "Ciudad de Mexico", "encanador", "plomero", "es"),
    ("electricista-meksyk", "Ciudad de Mexico", "eletricista", "electricista", "es"),
    ("limpieza-meksyk", "Ciudad de Mexico", "faxina", "limpieza", "es"),
    ("eletricista-belo", "Belo Horizonte", "eletricista", "electricista", "pt"),
]

if __name__ == "__main__":
    print("## ServiceApp - Traffic Bot - gotowe tresci jak z Google Ads, bez placenia")
    print("")
    print("Zasady: 1 slowo = 1 landing + 1 post + 1 Reels. Wszystko prowadzi do tego samego landingu.")
    print("")
    for slug, city, pt_service, es_service, lang in KEYWORDS:
        if lang == "es":
            service = es_service
            title = service + " en " + city + " - Pide ahora en ServiceApp"
            post = "Necesitas " + service + " en " + city + "? No necesitas buscar prestadores, la app lo hace por ti. Espera minima. Si el prestador acepta, te contacta de inmediato. Descarga gratis: " + BASE_DOWNLOAD + "?kw=" + slug + " Cuenta oficial ServiceApp"
            reels = "Reels 15 sek: Prestador de " + city + " w pracy, tekst na ekranie: Necesitas " + service + " en " + city + "? Descarga ServiceApp. Koniec: przycisk Descargar gratis."
            disclosure = "Cuenta oficial ServiceApp"
        else:
            service = pt_service
            title = service + " em " + city + " - Peca agora no ServiceApp"
            post = "Precisa de " + service + " em " + city + "? Voce nao precisa procurar prestadores, o app faz isso por voce. Espera minima. Se o prestador aceitar, ele entra em contato imediatamente. Baixe gratis: " + BASE_DOWNLOAD + "?kw=" + slug + " Conta oficial ServiceApp"
            reels = "Reels 15 sek: Prestador de " + city + " w pracy, tekst na ekranie: Precisa de " + service + " em " + city + "? Baixe ServiceApp. Koniec: przycisk Baixar gratis."
            disclosure = "Conta oficial ServiceApp"
        link = BASE_DOWNLOAD + "?kw=" + slug
        print("### " + title)
        print("Landing: " + link)
        print("Zaloguj do dodania landingu: https://serviceapp.mobi/")
        print("Post do grupy:")
        print(post)
        print("Zaloguj do publikacji posta: https://www.instagram.com/direct/inbox/")
        print("Reels:")
        print(reels)
        print("Zaloguj do publikacji Reels: https://www.instagram.com/")
        print(disclosure)
        print("")
    print("Zaloguj do 【entity-GitHub¦canonical_name=GitHub】 tylko jak chcesz zmienic liste slow: https://github.com/login")
