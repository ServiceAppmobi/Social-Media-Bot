import urllib.request
import urllib.parse
import json
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN, chat_id: str = TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Wysyła wiadomość tekstową przez Telegram Bot API."""
        if not self.is_configured():
            print("[!] Telegram nie jest skonfigurowany (brak TELEGRAM_BOT_TOKEN lub TELEGRAM_CHAT_ID w config/.env).")
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            print(f"[!] Błąd wysyłania na Telegram: {e}")
            return False

    def notify_lead(self, lead: dict) -> bool:
        """Formatuje lead i wysyła estetyczne powiadomienie na Telegram."""
        lead_type = lead.get("lead_type")
        if lead_type == "SERVICE_SEEKER":
            type_label = "🔍 <b>KLIENT SZUKA FACHOWCA / USŁUGI</b>"
        elif lead_type == "WORK_SEEKER":
            type_label = "🛠️ <b>WYKONAWCA SZUKA ZLECEŃ / PRACY</b>"
        else:
            type_label = "📌 <b>NOWA DYSKUSJA</b>"

        country = lead.get("country", "BR")
        country_header = "🇧🇷 BRAZYLIA" if country == "BR" else "🇲🇽 MEKSYK"

        title = lead.get("title", "Brak tytułu").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        url = lead.get("url", "#")
        source = lead.get("source_channel", "Forum").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        author = lead.get("author", "użytkownik").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        draft = lead.get("ai_draft", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        message = (
            f"{country_header} | <b>NOWY LEAD DLA SERVICEAPP</b>\n\n"
            f"<b>Status:</b> {type_label}\n"
            f"<b>Kanał:</b> <code>{source}</code> | <b>Autor:</b> @{author}\n\n"
            f"📌 <b>Temat:</b>\n<i>{title}</i>\n\n"
            f"🔗 <b>Link do wątku:</b>\n<a href='{url}'>{url}</a>\n\n"
            f"💬 <b>Sugerowana naturalna odpowiedź (kliknij aby skopiować):</b>\n"
            f"<code>{draft}</code>\n\n"
            f"<i>💡 Wskazówka: Wejdź w link, przejrzyj kontekst i wklej odpowiedź z oficjalnego profilu lub profilu ambasadora.</i>"
        )

        return self.send_message(message, parse_mode="HTML")

    def send_test_alert(self) -> bool:
        """Wysyła testową wiadomość weryfikacyjną."""
        test_msg = (
            "🚀 <b>Test Bota ServiceApp Lead Finder!</b>\n\n"
            "Połączenie z Twoim Telegramem działa bez zarzutu.\n"
            "Od teraz bot będzie przysyłał tutaj powiadomienia o nowych zapytaniach o pracę i fachowców w Brazylii."
        )
        return self.send_message(test_msg, parse_mode="HTML")
