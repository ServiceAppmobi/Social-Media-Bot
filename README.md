# 🌎 ServiceApp LatAm — Lead Monitor & iPhone Sync Bot

Dedykowany bot w architekturze **Social Listening & Lead Generation (Human-in-the-loop)** do monitorowania dyskusji w **Brazylii 🇧🇷** oraz **Meksyku 🇲🇽** na temat poszukiwania pracy, zleceń i wykonawców usług dla aplikacji **ServiceApp**.

Bot działa **w pełni automatycznie w chmurze (GitHub Actions co 4 godziny)** i synchronizuje wykryte leady bezpośrednio z **iPhone'em** (E-mail przez Resend API, podgląd w aplikacji GitHub Mobile, opcjonalne powiadomienia Push przez `ntfy` lub Telegram, oraz uruchamianie na żądanie przez Apple Skróty).

---

## 🎯 Monitorowane kraje i kanały

### 1. 🇧🇷 Brazylia (Portugalski PT-BR)
* **Fora / Reddit:** `r/brasil`, `r/saopaulo`, `r/riodejaneiro`, `r/trampos`, `r/curitiba`, `r/belohorizonte`, `r/brdev`, `r/ConselhosLegais`, `r/conversas` (z automatycznym fallbackiem RSS).
* **Grupy WhatsApp:** Webhook listener dla grup ogłoszeniowych i zleceń.
* **Słowa kluczowe:** *„preciso de encanador”*, *„indicação de diarista”*, *„trabalho autônomo”*, *„onde divulgar serviços”*, *„orçamento reforma”*.

### 2. 🇲🇽 Meksyk (Hiszpański ES-MX)
* **Fora / Reddit:** `r/mexico`, `r/MexicoCity`, `r/Monterrey`, `r/Guadalajara`, `r/Puebla`, `r/Tijuana`, `r/ChambasMexico`, `r/lacamiseta`, `r/taquerosprogramadores`.
* **Grupy WhatsApp:** Webhook listener dla grup giełdy pracy i zleceń.
* **Słowa kluczowe:** *„busco plomero”*, *„busco electricista”*, *„recomienden albañil”*, *„busco chamba urgente”*, *„dónde conseguir clientes”*.

---

## 📱 Synchronizacja z iPhone (GitHub Actions)

### 1. Sekrety w repozytorium GitHub
W GitHub otwórz **Settings → Secrets and variables → Actions → New repository secret** i ustaw:

| Sekret | Wymagany? | Przykładowa wartość |
| --- | --- | --- |
| `RESEND_API_KEY` | **Tak** (e-mail) | Twój klucz API z [resend.com/api-keys](https://resend.com/api-keys) |
| `EMAIL_RECIPIENT` | **Tak** | `karolak.pawel@gmail.com` (lub po weryfikacji DNS: `pawel.karolak@serviceapp.mobi`) |
| `EMAIL_SENDER` | Opcjonalny | `onboarding@resend.dev` (lub `noreply@serviceapp.mobi` po weryfikacji domeny) |
| `APP_NAME` | Opcjonalny | `ServiceApp` |
| `APP_URL` | Opcjonalny | `https://serviceapp.mobi` |
| `GEMINI_API_KEY` | Opcjonalny | Klucz Google Gemini dla spersonalizowanych odpowiedzi AI |
| `NTFY_TOPIC` | Opcjonalny | Nazwa prywatnego kanału w aplikacji **ntfy** na iOS (natywny Push!) |
| `TELEGRAM_BOT_TOKEN` | Opcjonalny | Token bota Telegram |
| `TELEGRAM_CHAT_ID` | Opcjonalny | ID czatu Telegram |

> **Deduplikacja w chmurze:** Workflow automatycznie zapisuje i przywraca bazę `leads.db` w GitHub Actions Cache (`leads-db-*`), dzięki czemu te same wątki nie są wysyłane ponownie przy kolejnych skanowaniach.

### 2. Podgląd i uruchamianie na żądanie z iPhone'a (GitHub Mobile)
1. Zainstaluj aplikację **GitHub** z App Store na iPhone.
2. Otwórz repozytorium `ServiceAppmobi/Social-Media-Bot` → zakładka **Actions** → **🇧🇷🇲🇽 ServiceApp LatAm Lead Monitor**.
3. Każdy wykonany cykl wyświetla gotowy raport Markdown (klikane linki do wątków + gotowe odpowiedzi do skopiowania) w sekcji **Summary**.
4. Kliknij **Run workflow**, aby ręcznie odpalić tryb `live`, `mock`, `test-email` lub `test-push`.

### 3. Szybkie powiadomienia Push na iPhone (`ntfy` — opcjonalnie, 1 minuta)
1. Zainstaluj darmową aplikację **ntfy** z App Store.
2. Kliknij `+` i wpisz unikalną, trudną do odgadnięcia nazwę tematu (np. `serviceapp-leads-twójlosowyciąg`).
3. Dodaj tę samą nazwę jako sekret `NTFY_TOPIC` w GitHub Secrets.
4. Kliknięcie powiadomienia na ekranie blokady iPhone'a otworzy bezpośrednio wątek klienta.

### 4. Uruchamianie jednym przyciskiem z ekranu głównego iPhone'a (Apple Skróty / Shortcuts)
Możesz dodać kafelek „Skanuj Leady” na ekran główny iPhone'a:
1. Otwórz aplikację **Skróty (Shortcuts)** na iPhone → `+` (Nowy skrót).
2. Dodaj akcję **Pobierz zawartość URL** (`Get Contents of URL`):
   - **URL:** `https://api.github.com/repos/ServiceAppmobi/Social-Media-Bot/actions/workflows/serviceapp-bot.yml/dispatches`
   - **Metoda:** `POST`
   - **Nagłówki:**
     - `Authorization`: `Bearer TWOJ_GITHUB_TOKEN`
     - `Accept`: `application/vnd.github+json`
     - `X-GitHub-Api-Version`: `2022-11-28`
   - **Treść (JSON):** `{"ref": "main", "inputs": {"mode": "live"}}`
3. Dodaj akcję **Pokaż powiadomienie**: `🚀 Skanowanie ServiceApp uruchomione!`.
4. Kliknij ikonę udostępniania → **Do ekranu początkowego**.

---

## 📧 Weryfikacja domeny `serviceapp.mobi` w Resend
Aby wysyłać raporty z firmowego adresu `noreply@serviceapp.mobi` na dowolny adres odbiorcy:
1. Wejdź na [resend.com/domains](https://resend.com/domains) → **Add Domain** → `serviceapp.mobi`.
2. Dodaj wskazane rekordy DNS (DKIM, SPF, MX) u rejestratora domeny.
3. Po weryfikacji zmień `EMAIL_SENDER` na `noreply@serviceapp.mobi` oraz `EMAIL_RECIPIENT` na `pawel.karolak@serviceapp.mobi` w GitHub Secrets i lokalnym `.env`.

---

## 🚀 Uruchamianie lokalne (macOS / Linux)

Skopiuj `.env.example` do `.env` i uzupełnij swój `RESEND_API_KEY`:

```bash
cp .env.example .env
```

Dostępne komendy:
```bash
# Test demonstracyjny (bez wysyłki i bez zapisu)
python3 main.py --mock --dry-run

# Test demonstracyjny + wysłanie raportu e-mail
python3 main.py --mock

# Wysłanie testowego e-maila przez Resend
python3 main.py --test-email

# Wysłanie testowego powiadomienia Push (ntfy) na iPhone
python3 main.py --test-push

# Test połączenia z Google Gemini Interactions API (gemini-4-hydrogen)
python3 main.py --test-gemini

# Uruchomienie testów integracji Gemini API (zero zależności)
python3 -m unittest test_gemini_integration.py -v

# Skanowanie na żywo (Brazylia & Meksyk)
python3 main.py

# Statystyki zapisanych leadów
python3 main.py --stats

# Nasłuchiwanie webhooka grup WhatsApp
python3 main.py --whatsapp-listener
```
