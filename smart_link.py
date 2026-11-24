# smart_link.py - ServiceApp Smart Link + QR - Element 1
# Tylko przygotowuje linki i strone, nic nie publikuje samo.

# WAZNE: Podmien te 2 linki na prawdziwe z Twoich kont, jak je masz.
# Jak ich nie masz, zostaw tak jak jest, strona bedzie kierowac na serviceapp.mobi
APP_STORE_URL = "https://apps.apple.com/app/serviceapp"
PLAY_URL = "https://play.google.com/store/apps/details?id=mobi.serviceapp"
BASE_DOWNLOAD_URL = "https://serviceapp.mobi/download"

# Miasta i uslugi - do QR
CITIES = [
    ("sao-paulo", "Sao Paulo - Brazylia"),
    ("rio", "Rio de Janeiro - Brazylia"),
    ("belo-horizonte", "Belo Horizonte - Brazylia"),
    ("curitiba", "Curitiba - Brazylia"),
    ("meksyk", "Ciudad de Mexico - Meksyk"),
]

def qr_url(city_slug):
    link = BASE_DOWNLOAD_URL + "?city=" + city_slug
    return "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" + link

def build_download_html():
    html = """<!DOCTYPE html>
<html lang="pt">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Pobierz ServiceApp</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 40px;">
<h1>ServiceApp - Pobierz za darmo</h1>
<p>Bez abonamentu. Bez prowizji od zlecenia. Tylko zaakceptowane zlecenia.</p>
<p><a href="APP_STORE_URL" style="display:block; margin: 12px; padding: 16px; background: #000; color: #fff; border-radius: 12px; text-decoration: none;">Pobierz z App Store</a></p>
<p><a href="PLAY_URL" style="display:block; margin: 12px; padding: 16px; background: #1a73e8; color: #fff; border-radius: 12px; text-decoration: none;">Pobierz z Google Play</a></p>
<p style="font-size: 12px; color: #666;">Conta oficial ServiceApp / Cuenta oficial ServiceApp</p>
<script>
var ua = navigator.userAgent || "";
if (/iPad|iPhone|iPod/.test(ua)) { window.location.href = "APP_STORE_URL"; }
else if (/Android/.test(ua)) { window.location.href = "PLAY_URL"; }
</script>
</body></html>"""
    html = html.replace("APP_STORE_URL", APP_STORE_URL).replace("PLAY_URL", PLAY_URL)
    with open("download.html", "w", encoding="utf-8") as f:
        f.write(html)
    return "download.html"

if __name__ == "__main__":
    print("## ServiceApp - Smart Link + QR - do akceptacji")
    print("")
    print("Smart link do wklejenia wszedzie: " + BASE_DOWNLOAD_URL)
    print("Zaloguj do App Store zeby skopiowac prawdziwy link: https://appstoreconnect.apple.com/")
    print("Zaloguj do Google Play zeby skopiowac prawdziwy link: https://play.google.com/console/")
    print("")
    for slug, name in CITIES:
        print("### " + name)
        print("Link: " + BASE_DOWNLOAD_URL + "?city=" + slug)
        print("QR do druku: " + qr_url(slug))
        print("Zaloguj do publikacji: https://www.instagram.com/direct/inbox/")
        print("")
    print("Plik strony: " + build_download_html())
    print("Zaloguj do 【entity-GitHub¦canonical_name=GitHub】 tylko jak chcesz zmienic linki: https://github.com/login")
