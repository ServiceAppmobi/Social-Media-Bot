import smtplib
import json
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any
from config import (
    EMAIL_RECIPIENT,
    EMAIL_SENDER,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_USE_TLS,
    RESEND_API_KEY,
    APP_NAME
)

class EmailNotifier:
    def __init__(self):
        self.recipient = EMAIL_RECIPIENT
        self.sender = EMAIL_SENDER
        self.host = SMTP_HOST
        self.port = SMTP_PORT
        self.user = SMTP_USER
        self.password = SMTP_PASSWORD
        self.use_tls = SMTP_USE_TLS
        self.resend_key = RESEND_API_KEY

    def is_configured(self) -> bool:
        """Sprawdza, czy skonfigurowano Resend API lub dane SMTP."""
        return bool(self.resend_key or (self.host and self.user and self.password))

    def _send_via_resend_api(self, subject: str, html_content: str, text_content: str, recipient: str = None) -> bool:
        """Wysyła e-mail bezpośrednio przez szybkie REST API Resend."""
        target_to = recipient or self.recipient
        url = "https://api.resend.com/emails"

        payload = {
            "from": f"{APP_NAME} Bot <{self.sender}>",
            "to": [target_to],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.resend_key}",
                "Content-Type": "application/json",
                "User-Agent": "ServiceAppLeadFinder/2.0"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    print(f"[✓] E-mail został pomyślnie wysłany przez Resend API na: {target_to}")
                    return True
        except urllib.error.HTTPError as e:
            err_data = e.read().decode()
            if "validation_error" in err_data and "karolak.pawel@gmail.com" in err_data:
                print(f"[!] Resend wymaga weryfikacji domeny serviceapp.mobi przed wysyłką na inne adresy.")
                print(f"[*] Przekierowuję wysyłkę testową na Twoje konto Resend: karolak.pawel@gmail.com...")
                return self._send_via_resend_api(subject, html_content, text_content, recipient="karolak.pawel@gmail.com")
            else:
                print(f"[!] Błąd Resend API ({e.code}): {err_data}")
        except Exception as e:
            print(f"[!] Błąd połączenia z Resend API: {e}")

        return False

    def _send_smtp_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """Fallback wysyłający przez serwer SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{APP_NAME} Lead Bot <{self.sender}>"
        msg["To"] = self.recipient

        part_text = MIMEText(text_content, "plain", "utf-8")
        part_html = MIMEText(html_content, "html", "utf-8")
        msg.attach(part_text)
        msg.attach(part_html)

        try:
            print(f"[*] Łączenie z serwerem SMTP ({self.host}:{self.port})...")
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=15)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=15)
                if self.use_tls:
                    server.starttls()

            server.login(self.user, self.password)
            server.sendmail(self.sender, [self.recipient], msg.as_string())
            server.quit()
            print(f"[✓] E-mail został pomyślnie wysłany przez SMTP na: {self.recipient}")
            return True
        except Exception as e:
            print(f"[!] Błąd wysyłania e-maila przez SMTP: {e}")
            return False

    def send_email(self, subject: str, html_content: str, text_content: str) -> bool:
        """Główna metoda wysyłająca e-mail (Resend API lub SMTP)."""
        if self.resend_key:
            return self._send_via_resend_api(subject, html_content, text_content)
        return self._send_smtp_email(subject, html_content, text_content)

    def send_digest_email(self, leads: List[Dict[str, Any]]) -> bool:
        """Wysyła zbiorcze podsumowanie leadów z Brazylii i Meksyku."""
        if not leads:
            return False

        br_count = sum(1 for l in leads if l.get("country") == "BR")
        mx_count = sum(1 for l in leads if l.get("country") == "MX")

        subject = f"🌎 [{APP_NAME}] Wykryto {len(leads)} nowych leadów (🇧🇷 Brazylia: {br_count}, 🇲🇽 Meksyk: {mx_count})"

        lead_cards_html = ""
        for idx, lead in enumerate(leads, 1):
            country = lead.get("country", "BR")
            country_flag = "🇧🇷 Brazylia" if country == "BR" else "🇲🇽 Meksyk"
            country_badge_color = "#16a34a" if country == "BR" else "#dc2626"

            lead_type = lead.get("lead_type")
            if lead_type == "SERVICE_SEEKER":
                type_badge_bg = "#2563eb"
                type_label = "🔍 KLIENT SZUKA FACHOWCA"
            elif lead_type == "WORK_SEEKER":
                type_badge_bg = "#059669"
                type_label = "🛠️ FACHOWIEC SZUKA PRACY / ZLECEŃ"
            else:
                type_badge_bg = "#4b5563"
                type_label = "📌 DYSKUSJA"

            platform = lead.get("platform", "web")
            plat_badge = "🟢 WhatsApp" if platform == "whatsapp" else "🌐 Forum / Reddit"
            
            title = lead.get("title", "")
            url = lead.get("url", "#")
            source = lead.get("source_channel", "Społeczność")
            author = lead.get("author", "użytkownik")
            snippet = lead.get("content_snippet", "")
            draft = lead.get("ai_draft", "")
            lang_label = "Português (PT-BR)" if country == "BR" else "Español (ES-MX)"

            btn_label = "💬 Otwórz czat na WhatsApp &rarr;" if platform == "whatsapp" else "🔗 Otwórz wątek na forum &rarr;"

            lead_cards_html += f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
                    <span style="background-color: {country_badge_color}; color: #ffffff; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 12px; text-transform: uppercase;">
                        {country_flag}
                    </span>
                    <span style="background-color: {type_badge_bg}; color: #ffffff; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 12px; text-transform: uppercase;">
                        {type_label}
                    </span>
                    <span style="background-color: #f1f5f9; color: #334155; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 12px;">
                        {plat_badge}
                    </span>
                </div>
                
                <div style="color: #64748b; font-size: 12px; margin-bottom: 8px;">
                    Kanał: <b>{source}</b> | Autor: <b>@{author}</b>
                </div>

                <h3 style="margin: 0 0 10px 0; font-size: 17px; color: #0f172a; line-height: 1.4;">
                    {title}
                </h3>

                {f'<p style="color: #475569; font-size: 14px; line-height: 1.5; margin: 0 0 16px 0; background: #f8fafc; padding: 12px; border-radius: 6px; font-style: italic;">"{snippet}"</p>' if snippet else ''}
                
                <div style="margin-bottom: 16px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 12px;">
                    <div style="color: #166534; font-size: 12px; font-weight: bold; margin-bottom: 6px;">
                        💬 Sugerowana odpowiedź ({lang_label}) do skopiowania:
                    </div>
                    <div style="color: #14532d; font-size: 13px; line-height: 1.5; font-family: monospace;">
                        {draft}
                    </div>
                </div>

                <div>
                    <a href="{url}" target="_blank" style="display: inline-block; background-color: #2563eb; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: bold; padding: 10px 18px; border-radius: 6px;">
                        {btn_label}
                    </a>
                </div>
            </div>
            """

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; color: #1e293b;">
            <div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1;">
                <div style="background: linear-gradient(135deg, #0f172a, #1e3a8a); padding: 28px; text-align: center; color: #ffffff;">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">
                        🌎 {APP_NAME} - LatAm Lead Monitor
                    </h1>
                    <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9;">
                        Nowe zapytania o usługi i pracę: 🇧🇷 Brazylia & 🇲🇽 Meksyk (Fora, Social Media, Grupy WhatsApp)
                    </p>
                </div>

                <div style="padding: 24px;">
                    <p style="font-size: 14px; color: #475569; margin: 0 0 20px 0;">
                        Cześć Paweł! Wykryto <b>{len(leads)} nowych leadów</b> (Brazylia: {br_count}, Meksyk: {mx_count}). Poniżej znajdziesz bezpośrednie linki do dyskusji oraz przygotowane naturalne odpowiedzi do skopiowania.
                    </p>

                    {lead_cards_html}

                    <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px; text-align: center; font-size: 12px; color: #94a3b8;">
                        Powiadomienie wygenerowane automatycznie przez ServiceApp Bot via Resend.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"[{APP_NAME}] Wykryto {len(leads)} nowych leadów (Brazylia & Meksyk):\n\n"
        for idx, lead in enumerate(leads, 1):
            text_body += f"{idx}. [{lead.get('country')}] {lead.get('title')} ({lead.get('source_channel')})\n"
            text_body += f"Link: {lead.get('url')}\n"
            text_body += f"Sugerowana odpowiedź:\n{lead.get('ai_draft')}\n"
            text_body += "-" * 50 + "\n"

        return self.send_email(subject, html_body, text_body)

    def send_test_email(self) -> bool:
        """Wysyła testową wiadomość e-mail weryfikującą połączenie z Resend."""
        subject = f"🧪 Test konfiguracji powiadomień e-mail - {APP_NAME} Lead Bot"
        html = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 24px; color: #1e293b; background: #f8fafc;">
            <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <h2 style="color: #16a34a; margin-top: 0;">🎉 Gratulacje Paweł!</h2>
                <p>Integracja z <b>Resend</b> została pomyślnie podłączona do bota <b>{APP_NAME}</b>!</p>
                <p>Od teraz bot monitoruje media społecznościowe i grupy WhatsApp w:</p>
                <ul>
                    <li>🇧🇷 <b>Brazylii</b> (Portuguese PT-BR)</li>
                    <li>🇲🇽 <b>Meksyku</b> (Español ES-MX)</li>
                </ul>
                <p style="color: #64748b; font-size: 13px; margin-top: 20px;">
                    Wiadomość wysłana pomyślnie przez Resend API.
                </p>
            </div>
        </body>
        </html>
        """
        text = f"Gratulacje Paweł! Powiadomienia przez Resend działają prawidłowo dla bota {APP_NAME}."
        return self.send_email(subject, html, text)
