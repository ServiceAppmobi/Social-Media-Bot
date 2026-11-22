import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List

from config import (
    MASTODON_ENABLED,
    MASTODON_TAG_GROUPS,
    MAX_POST_AGE_DAYS,
    REDDIT_USER_AGENT,
)


def _strip_html(raw_html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", raw_html or "", flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_iso_timestamp(ts: str) -> float:
    if not ts:
        return 0.0
    try:
        cleaned = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned).timestamp()
    except Exception:
        return 0.0


class MastodonMonitor:
    """
    Monitoruje publiczne, darmowe API Mastodona (zero kluczy API, zero kosztów)
    dla społeczności brazylijskich (PT-BR) i meksykańskich/LatAm (ES-MX).
    """

    def __init__(self, max_age_days: int = MAX_POST_AGE_DAYS):
        self.max_age_days = max_age_days
        self.user_agent = REDDIT_USER_AGENT

    def _fetch_json(self, url: str) -> List[Dict[str, Any]]:
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data if isinstance(data, list) else []
        except urllib.error.HTTPError as exc:
            print(f"[!] Mastodon HTTP {exc.code} dla {url}: {exc.reason}")
        except Exception as exc:
            print(f"[!] Mastodon błąd dla {url}: {exc}")
        return []

    def _normalize_status(
        self,
        status: Dict[str, Any],
        country: str,
        source_channel: str,
        allowed_langs: tuple,
    ) -> Dict[str, Any]:
        lang = (status.get("language") or "").lower()
        if lang and not any(lang.startswith(prefix) for prefix in allowed_langs):
            return {}

        text = _strip_html(status.get("content", ""))
        if not text:
            return {}

        created_utc = _parse_iso_timestamp(status.get("created_at", ""))
        if created_utc and self.max_age_days > 0:
            cutoff = time.time() - (self.max_age_days * 86400)
            if created_utc < cutoff:
                return {}

        account = status.get("account") or {}
        author = account.get("acct") or account.get("username") or "usuario"
        status_id = status.get("id") or ""
        post_url = status.get("url") or ""
        if not status_id or not post_url:
            return {}

        title = text[:95] + ("..." if len(text) > 95 else "")
        return {
            "id": f"mastodon_{status_id}",
            "platform": "mastodon",
            "country": country,
            "source_channel": source_channel,
            "title": title,
            "content": text[:1500],
            "url": post_url,
            "author": author,
            "created_utc": created_utc,
        }

    def scan_tag(self, instance: str, tag: str, country: str, limit: int = 30, lang: str = "") -> List[Dict[str, Any]]:
        url = f"https://{instance}/api/v1/timelines/tag/{urllib.parse.quote(tag)}?limit={min(limit, 40)}"
        if lang:
            allowed_langs = (lang,)
        else:
            allowed_langs = ("pt",) if country == "BR" else ("es",) if country in ("MX", "AR", "CO", "CL", "PE", "EC", "VE", "UY", "PY", "BO") else ("ja", "en") if country == "JP" else ("en",)
        results: List[Dict[str, Any]] = []
        for st in self._fetch_json(url):
            item = self._normalize_status(st, country, f"Mastodon #{tag}", allowed_langs)
            if item:
                results.append(item)
        return results

    def scan_local_public(self, instance: str, country: str, limit: int = 40) -> List[Dict[str, Any]]:
        url = f"https://{instance}/api/v1/timelines/public?local=true&limit={min(limit, 40)}"
        allowed_langs = ("pt",) if country == "BR" else ("es",)
        results: List[Dict[str, Any]] = []
        for st in self._fetch_json(url):
            item = self._normalize_status(st, country, f"Mastodon ({instance})", allowed_langs)
            if item:
                results.append(item)
        return results

    def scan_all(self) -> List[Dict[str, Any]]:
        if not MASTODON_ENABLED:
            return []

        all_found: List[Dict[str, Any]] = []
        print("🐘 Skanowanie publicznych kanałów Mastodon (Ameryki + Singapur + Japonia)...")

        # Brazylia: lokalna instancja bolha.us
        all_found.extend(self.scan_local_public("bolha.us", country="BR", limit=40))

        for country, lang, tags in MASTODON_TAG_GROUPS:
            for tag in tags:
                all_found.extend(self.scan_tag("mastodon.social", tag, country=country, limit=25, lang=lang))
                time.sleep(0.2)

        unique = {p["id"]: p for p in all_found}.values()
        posts = list(unique)
        print(f"    -> Pobrano {len(posts)} świeżych wpisów z Mastodona")
        return posts
