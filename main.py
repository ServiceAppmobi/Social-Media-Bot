#!/usr/bin/env python3
"""
ServiceApp LatAm Lead Monitor & Smart Response Assistant
========================================================
Monitor dyskusji w mediach społecznościowych i grupach WhatsApp:
- 🇧🇷 Brazylia (PT-BR)
- 🇲🇽 Meksyk (ES-MX)

Wysyła estetyczne raporty e-mail z office@serviceapp.mobi na pawel.karolak@serviceapp.mobi.
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Załaduj zmienne środowiskowe z .env jeśli plik istnieje (nie nadpisuje zmiennych z GitHub Secrets)
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

load_env_file()

from config import POLL_INTERVAL_SECONDS, EMAIL_RECIPIENT, EMAIL_SENDER, GEMINI_MODEL
from database import init_db, is_post_seen, save_lead, mark_notified, get_stats
from monitors.reddit_monitor import RedditMonitor
from monitors.mastodon_monitor import MastodonMonitor
from monitors.whatsapp_monitor import WhatsAppMonitor
from analyzer import PostAnalyzer
from gemini_client import GeminiAPIError, GeminiClient
from notifiers.telegram_notifier import TelegramNotifier
from notifiers.email_notifier import EmailNotifier
from notifiers.ntfy_notifier import NtfyNotifier
from notifiers.console_notifier import ConsoleNotifier


def write_github_summary(total_scanned: int, new_leads: list):
    """Zapisuje czytelny raport Markdown do $GITHUB_STEP_SUMMARY (widoczny w aplikacji GitHub na iPhone)."""
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    br_count = sum(1 for l in new_leads if l.get("country") == "BR")
    mx_count = sum(1 for l in new_leads if l.get("country") == "MX")

    lines = [
        "# 🌎 ServiceApp LatAm Lead Monitor — Raport",
        "",
        f"- **Data (UTC):** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"- **Przeanalizowano wpisów:** {total_scanned}",
        f"- **Nowych leadów:** **{len(new_leads)}** (🇧🇷 Brazylia: {br_count} | 🇲🇽 Meksyk: {mx_count})",
        "",
    ]

    if not new_leads:
        lines.append("_Brak nowych, nieprzetworzonych leadów w tym cyklu._")
    else:
        for idx, lead in enumerate(new_leads, 1):
            flag = "🇧🇷 Brazylia" if lead.get("country") == "BR" else "🇲🇽 Meksyk"
            role = "🔍 Klient szuka fachowca" if lead.get("lead_type") == "SERVICE_SEEKER" else "🛠️ Fachowiec szuka zleceń"
            lines.extend([
                f"### {idx}. [{flag}] {lead.get('title', 'Bez tytułu')}",
                f"- **Typ:** {role} | **Kanał:** `{lead.get('source_channel')}` | **Autor:** `@{lead.get('author')}`",
                f"- **Link:** {lead.get('url')}",
                "",
                "**Sugerowana odpowiedź do skopiowania:**",
                "```text",
                lead.get("ai_draft", ""),
                "```",
                "",
            ])

    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        print(f"[!] Nie udało się zapisać GITHUB_STEP_SUMMARY: {e}")


def process_posts(posts, analyzer, telegram, emailer, ntfy=None, dry_run=False):
    found_count = 0
    new_leads = []

    for post in posts:
        post_id = post["id"]
        title = post["title"]
        content = post.get("content", "")
        country = post.get("country", "BR")

        # Sprawdzenie deduplikacji
        if is_post_seen(post_id) and not dry_run:
            continue

        found_count += 1
        lead_type, draft_reply = analyzer.analyze_post(title, content, country=country)

        if lead_type != "IRRELEVANT":
            lead_data = {
                "post_id": post_id,
                "platform": post.get("platform", "web"),
                "country": country,
                "source_channel": post.get("source_channel", "forum"),
                "title": title,
                "url": post.get("url", ""),
                "author": post.get("author", "anônimo"),
                "content_snippet": content[:300],
                "lead_type": lead_type,
                "ai_draft": draft_reply
            }

            new_leads.append(lead_data)
            # Podgląd w konsoli
            ConsoleNotifier.print_lead(lead_data)

            # Zapis w bazie
            if not dry_run:
                save_lead(
                    post_id=lead_data["post_id"],
                    platform=lead_data["platform"],
                    source_channel=lead_data["source_channel"],
                    title=lead_data["title"],
                    url=lead_data["url"],
                    author=lead_data["author"],
                    content_snippet=lead_data["content_snippet"],
                    lead_type=lead_data["lead_type"],
                    ai_draft=lead_data["ai_draft"],
                    country=lead_data["country"],
                    notified=0
                )

                # Opcjonalny alert Telegram (iPhone)
                if telegram.is_configured():
                    telegram.notify_lead(lead_data)

                # Opcjonalny natywny Push na iPhone (ntfy)
                if ntfy and ntfy.is_configured():
                    ntfy.notify_lead(lead_data)

    # Wysłanie zbiorczego e-maila
    if new_leads and not dry_run:
        print(f"\n[*] Przygotowano {len(new_leads)} leadów (Brazylia & Meksyk) do wysłania z {EMAIL_SENDER} na {EMAIL_RECIPIENT}...")
        if emailer.is_configured():
            success = emailer.send_digest_email(new_leads)
            if success:
                for l in new_leads:
                    mark_notified(l["post_id"])
        else:
            print("[i] Wysyłka e-mail nie została jeszcze skonfigurowana.")
            print(f"    Leady zapisano w lokalnej bazie. Aby włączyć wysyłkę na {EMAIL_RECIPIENT},")
            print("    ustaw RESEND_API_KEY (lub dane SMTP) w pliku .env albo GitHub Secrets.")

    return found_count, new_leads

def run_pipeline(mock=False, dry_run=False):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔎 Rozpoczynam skanowanie mediów i grup (🇧🇷 Brazylia & 🇲🇽 Meksyk)...")
    init_db()

    analyzer = PostAnalyzer()
    telegram = TelegramNotifier()
    emailer = EmailNotifier()
    ntfy = NtfyNotifier()
    reddit = RedditMonitor()
    mastodon = MastodonMonitor()

    posts = []
    if mock:
        print("[i] Tryb demonstracyjny: przetwarzanie przykładowych postów z forów i grup WhatsApp (BR & MX)...")
        posts.extend(reddit.get_mock_posts())
        posts.extend(WhatsAppMonitor.get_mock_group_messages())
    else:
        print("[*] Skanowanie publicznych wątków i forów (Brazylia & Meksyk)...")
        posts.extend(reddit.scan_all())
        posts.extend(mastodon.scan_all())

    total_scanned = len(posts)
    processed, new_leads = process_posts(posts, analyzer, telegram, emailer, ntfy=ntfy, dry_run=dry_run)
    write_github_summary(total_scanned, new_leads)

    print(f"\n[✓] Zakończono cykl skanowania.")
    print(f"    - Przeanalizowano wpisów: {total_scanned}")
    print(f"    - Zakwalifikowane jako lead dla ServiceApp: {len(new_leads)}")
    print(f"    - Odbiorca powiadomień: {EMAIL_RECIPIENT} (z adresu: {EMAIL_SENDER})")

def handle_incoming_whatsapp_message(data):
    """Callback dla webhooka WhatsApp na żywo."""
    init_db()
    analyzer = PostAnalyzer()
    telegram = TelegramNotifier()
    emailer = EmailNotifier()
    ntfy = NtfyNotifier()

    print(f"\n[🟢 WhatsApp] Otrzymano nową wiadomość z grupy: {data.get('source_channel')}")
    process_posts([data], analyzer, telegram, emailer, ntfy=ntfy, dry_run=False)

def main():
    parser = argparse.ArgumentParser(description="ServiceApp LatAm Lead Monitor (Brazylia & Meksyk)")
    parser.add_argument("--dry-run", action="store_true", help="Uruchamia jednorazowo bez zapisywania i bez wysyłki")
    parser.add_argument("--mock", action="store_true", help="Uruchamia na przykładowych rzeczywistych danych (Reddit + WhatsApp dla BR i MX)")
    parser.add_argument("--daemon", action="store_true", help="Uruchamia w pętli co określony interwał (tryb ciągły)")
    parser.add_argument("--whatsapp-listener", action="store_true", help="Uruchamia serwer webhooka nasłuchujący grup WhatsApp w tle")
    parser.add_argument("--test-email", action="store_true", help="Wysyła testową wiadomość e-mail przez Resend/SMTP")
    parser.add_argument("--test-telegram", action="store_true", help="Wysyła testowy komunikat na Telegram")
    parser.add_argument("--test-push", action="store_true", help="Wysyła testowe powiadomienie Push (ntfy) na iPhone")
    parser.add_argument("--test-gemini", action="store_true", help="Sprawdza połączenie z Google Gemini Interactions API")
    parser.add_argument("--stats", action="store_true", help="Wyświetla statystyki z podziałem na Brazylię i Meksyk")

    args = parser.parse_args()

    if args.stats:
        init_db()
        stats = get_stats()
        print("\n📊 STATYSTYKI LEADÓW SERVICEAPP (Brazylia & Meksyk):")
        print(f"  • Wszystkich zapisanych leadów:       {stats['total']}")
        print(f"  • 🇧🇷 Leady z Brazylii:                 {stats['brazil']}")
        print(f"  • 🇲🇽 Leady z Meksyku:                  {stats['mexico']}")
        print(f"  • 🔍 Klienci szukający fachowców:     {stats['service_seekers']}")
        print(f"  • 🛠️ Wykonawcy szukający pracy:       {stats['work_seekers']}")
        print(f"  • Wysłane raporty:                    {stats['notified']}")
        print(f"  • Nadawca:                            {EMAIL_SENDER}")
        print(f"  • Odbiorca:                           {EMAIL_RECIPIENT}")
        return

    if args.test_email:
        emailer = EmailNotifier()
        if not emailer.is_configured():
            print("[!] Błąd: Brak konfiguracji RESEND_API_KEY lub SMTP_PASSWORD w pliku .env / GitHub Secrets.")
            sys.exit(1)
        print(f"[*] Wysyłam testowy e-mail z {EMAIL_SENDER} na adres {emailer.recipient}...")
        if emailer.send_test_email():
            print(f"[✓] Sukces! Sprawdź skrzynkę odbiorczą na {emailer.recipient}.")
        else:
            print("[!] Błąd: Nie udało się wysłać e-maila. Sprawdź poprawność danych Resend/SMTP.")
            sys.exit(1)
        return

    if args.test_telegram:
        telegram = TelegramNotifier()
        if not telegram.is_configured():
            print("[!] Błąd: Brak TELEGRAM_BOT_TOKEN lub TELEGRAM_CHAT_ID w pliku .env / GitHub Secrets.")
            sys.exit(1)
        print("[*] Wysyłam testowy komunikat na Telegram...")
        if telegram.send_test_alert():
            print("[✓] Sukces! Sprawdź aplikację Telegram.")
        else:
            print("[!] Błąd: Nie udało się wysłać wiadomości na Telegram.")
            sys.exit(1)
        return

    if args.test_push:
        ntfy = NtfyNotifier()
        if not ntfy.is_configured():
            print("[!] Błąd: Brak NTFY_TOPIC w pliku .env / GitHub Secrets.")
            sys.exit(1)
        print(f"[*] Wysyłam testowe powiadomienie Push (ntfy) na temat: {ntfy.topic}...")
        if ntfy.send_test_push():
            print("[✓] Sukces! Sprawdź aplikację ntfy na iPhone.")
        else:
            print("[!] Błąd: Nie udało się wysłać powiadomienia Push.")
            sys.exit(1)
        return

    if args.test_gemini:
        gemini = GeminiClient()
        if not gemini.is_configured():
            print("[!] Błąd: Brak GEMINI_API_KEY w pliku .env / GitHub Secrets.")
            print("    Wygeneruj klucz w Google AI Studio: https://aistudio.google.com/apikey")
            sys.exit(1)
        print(f"[*] Testuję połączenie z Gemini Interactions API ({gemini.api_version}, model: {gemini.default_model})...")
        try:
            interaction = gemini.health_check()
            tokens = interaction.usage.get("total_tokens")
            token_info = f" | tokeny: {tokens}" if tokens is not None else ""
            print(f"[✓] Sukces! Status: {interaction.status} | Odpowiedź: {interaction.output_text!r}{token_info}")
        except GeminiAPIError as exc:
            print(f"[!] Błąd połączenia z Gemini API: {exc}")
            sys.exit(1)
        return

    if args.whatsapp_listener:
        wpp = WhatsAppMonitor()
        wpp.start_webhook_listener(handle_incoming_whatsapp_message)
        return

    if args.daemon:
        print(f"[🚀] Uruchamianie w trybie ciągłym (odpytywanie co {POLL_INTERVAL_SECONDS} sekund)...")
        print(f"     Obszar: 🇧🇷 Brazylia & 🇲🇽 Meksyk | Raporty: {EMAIL_RECIPIENT}")
        print("     Naciśnij Ctrl+C, aby zatrzymać.\n")
        try:
            while True:
                run_pipeline(mock=args.mock, dry_run=args.dry_run)
                print(f"[*] Następne sprawdzenie za {POLL_INTERVAL_SECONDS}s...")
                time.sleep(POLL_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n[!] Zatrzymano bota.")
    else:
        run_pipeline(mock=args.mock, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
