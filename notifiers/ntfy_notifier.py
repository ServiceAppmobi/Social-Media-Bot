import urllib.request
import urllib.error
from typing import Dict, Any
from config import NTFY_TOPIC, NTFY_SERVER, APP_NAME


class NtfyNotifier:
    """Wysyła natywne powiadomienia Push na iPhone przez aplikację ntfy."""

    def __init__(self, topic: str = NTFY_TOPIC, server: str = NTFY_SERVER):
        self.topic = topic.strip()
        self.server = server.rstrip("/")

    def is_configured(self) -> bool:
        return bool(self.topic)

    def send_push(self, title: str, message: str, click_url: str = "", priority: str = "default") -> bool:
        if not self.is_configured():
            return False

        url = f"{self.server}/{self.topic}"
        headers = {
            "Title": title.encode("ascii", "ignore").decode("ascii") or f"{APP_NAME} Lead",
            "Priority": priority,
            "Tags": "bell,briefcase",
            "User-Agent": "ServiceAppLeadFinder/2.0",
        }
        if click_url:
            headers["Click"] = click_url

        req = urllib.request.Request(
            url,
            data=message.encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            print(f"[!] Błąd wysyłania powiadomienia ntfy: {e}")
            return False

    def notify_lead(self, lead: Dict[str, Any]) -> bool:
        country_code = (lead.get("country") or "BR").upper()
        lead_type = "Klient" if lead.get("lead_type") == "SERVICE_SEEKER" else "Fachowiec"
        title = f"[{APP_NAME} {country_code}] {lead_type}: {lead.get('source_channel', '')}"
        body = (
            f"{lead.get('title', '')}\n\n"
            f"Sugerowana odpowiedź:\n{lead.get('ai_draft', '')}"
        )
        return self.send_push(title=title, message=body, click_url=lead.get("url", ""))

    def send_test_push(self) -> bool:
        return self.send_push(
            title=f"{APP_NAME} Bot - Test iPhone Push",
            message="Powiadomienia Push z GitHub Actions na iPhone działają prawidłowo!",
            priority="high",
        )
