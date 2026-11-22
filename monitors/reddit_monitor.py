import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from config import (
    KEYWORDS_BR_SERVICE,
    KEYWORDS_BR_WORK,
    KEYWORDS_MX_SERVICE,
    KEYWORDS_MX_WORK,
    MAX_POST_AGE_DAYS,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    TARGET_SUBREDDITS_BR,
    TARGET_SUBREDDITS_MX,
)

ARCTIC_SHIFT_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_OAUTH_BASE = "https://oauth.reddit.com"


class RedditMonitor:
    """
    Pobiera najnowsze wątki z brazylijskich (PT-BR) i meksykańskich (ES-MX) subredditów.

    Tryb 1 (opcjonalny): Oficjalne Reddit OAuth API (jeśli ustawiono REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET).
    Tryb 2 (domyślny, 0 zł, bez klucza): Publiczne API Arctic Shift (nie jest blokowane 403/429 na GitHub Actions).
    """

    def __init__(
        self,
        client_id: str = REDDIT_CLIENT_ID,
        client_secret: str = REDDIT_CLIENT_SECRET,
        user_agent: str = REDDIT_USER_AGENT,
        max_age_days: int = MAX_POST_AGE_DAYS,
    ):
        self.client_id = (client_id or "").strip()
        self.client_secret = (client_secret or "").strip()
        self.user_agent = user_agent
        self.max_age_days = max_age_days
        self._oauth_token: Optional[str] = None

    def _has_oauth_credentials(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def _get_oauth_token(self) -> Optional[str]:
        if self._oauth_token:
            return self._oauth_token
        if not self._has_oauth_credentials():
            return None

        auth_raw = f"{self.client_id}:{self.client_secret}".encode("utf-8")
        auth_b64 = base64.b64encode(auth_raw).decode("ascii")
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")
        req = urllib.request.Request(
            REDDIT_TOKEN_URL,
            data=data,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "User-Agent": self.user_agent,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    self._oauth_token = payload.get("access_token")
                    return self._oauth_token
        except Exception as exc:
            print(f"[!] Nie udało się pobrać tokenu Reddit OAuth ({exc}). Przełączam na Arctic Shift.")
        return None

    def _normalize_post(self, data: Dict[str, Any], subreddit: str, country: str) -> Optional[Dict[str, Any]]:
        post_id = data.get("id")
        title = (data.get("title") or "").strip()
        if not post_id or not title:
            return None

        if data.get("removed_by_category") or data.get("is_robot_indexable") is False:
            return None

        selftext = (data.get("selftext") or "").strip()
        if selftext in ("[removed]", "[deleted]"):
            selftext = ""

        created_utc = float(data.get("created_utc") or 0)
        if created_utc and self.max_age_days > 0:
            cutoff = time.time() - (self.max_age_days * 86400)
            if created_utc < cutoff:
                return None

        permalink = data.get("permalink") or f"/r/{subreddit}/comments/{post_id}/"
        if not permalink.startswith("http"):
            url = f"https://reddit.com{permalink}"
        else:
            url = permalink

        return {
            "id": f"reddit_{post_id}",
            "platform": "reddit",
            "country": country,
            "source_channel": f"r/{data.get('subreddit') or subreddit}",
            "title": title,
            "content": selftext[:1500],
            "url": url,
            "author": data.get("author") or "anônimo",
            "created_utc": created_utc,
        }

    def _fetch_via_oauth(self, subreddit: str, country: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        token = self._get_oauth_token()
        if not token:
            return None

        url = f"{REDDIT_OAUTH_BASE}/r/{urllib.parse.quote(subreddit)}/new?limit={min(limit, 100)}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    children = payload.get("data", {}).get("children", [])
                    posts = []
                    for child in children:
                        item = self._normalize_post(child.get("data", {}), subreddit, country)
                        if item:
                            posts.append(item)
                    return posts
        except Exception as exc:
            print(f"[!] Reddit OAuth błąd dla r/{subreddit}: {exc}")
        return None

    def _fetch_via_arctic_shift(self, subreddit: str, country: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera najświeższe posty subreddita przez bezpłatne publiczne API Arctic Shift."""
        params: Dict[str, Any] = {
            "subreddit": subreddit,
            "limit": min(limit, 100),
            "sort": "desc",
        }
        if self.max_age_days > 0:
            params["after"] = int(time.time() - (self.max_age_days * 86400))

        url = f"{ARCTIC_SHIFT_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        posts: List[Dict[str, Any]] = []
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    payload = json.loads(resp.read().decode("utf-8"))
                    for raw_post in payload.get("data") or []:
                        item = self._normalize_post(raw_post, subreddit, country)
                        if item:
                            posts.append(item)
        except urllib.error.HTTPError as exc:
            print(f"[!] Arctic Shift HTTP {exc.code} dla r/{subreddit}: {exc.reason}")
        except Exception as exc:
            print(f"[!] Arctic Shift błąd dla r/{subreddit}: {exc}")
        return posts

    def fetch_posts_for_subreddit(self, subreddit: str, country: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera najnowsze posty z danego subreddita (OAuth lub darmowy Arctic Shift)."""
        if self._has_oauth_credentials():
            oauth_posts = self._fetch_via_oauth(subreddit, country=country, limit=limit)
            if oauth_posts is not None:
                return oauth_posts
        return self._fetch_via_arctic_shift(subreddit, country=country, limit=limit)

    def scan_country(
        self,
        country: str,
        subreddits: List[str],
        service_keywords: Optional[List[str]] = None,
        work_keywords: Optional[List[str]] = None,
        limit_per_sub: int = 100,
    ) -> List[Dict[str, Any]]:
        """Przeszukuje najnowsze wpisy ze wszystkich subredditów dla danego kraju."""
        found: List[Dict[str, Any]] = []
        for sub in subreddits:
            posts = self.fetch_posts_for_subreddit(sub, country=country, limit=limit_per_sub)
            found.extend(posts)
            time.sleep(0.35)
        return found

    def scan_all(self, limit_per_sub: int = 100) -> List[Dict[str, Any]]:
        """Przeszukuje społeczności Reddit w Brazylii (PT-BR) i Meksyku (ES-MX)."""
        all_found: List[Dict[str, Any]] = []
        mode_label = "Reddit OAuth API" if self._has_oauth_credentials() else "Arctic Shift Public Reddit API"
        print(f"    [Źródło Reddit: {mode_label} | okno: ostatnie {self.max_age_days} dni]")

        print("🇧🇷 Skanowanie społeczności Reddit w Brazylii...")
        posts_br = self.scan_country("BR", TARGET_SUBREDDITS_BR, KEYWORDS_BR_SERVICE, KEYWORDS_BR_WORK, limit_per_sub)
        print(f"    -> Pobrano {len(posts_br)} świeżych wpisów z Brazylii")
        all_found.extend(posts_br)

        print("🇲🇽 Skanowanie społeczności Reddit w Meksyku...")
        posts_mx = self.scan_country("MX", TARGET_SUBREDDITS_MX, KEYWORDS_MX_SERVICE, KEYWORDS_MX_WORK, limit_per_sub)
        print(f"    -> Pobrano {len(posts_mx)} świeżych wpisów z Meksyku")
        all_found.extend(posts_mx)

        unique = {p["id"]: p for p in all_found}.values()
        return list(unique)

    @staticmethod
    def get_mock_posts() -> List[Dict[str, Any]]:
        """Zwraca przykładowe posty z Brazylii i Meksyku do celów testowych."""
        return [
            {
                "id": "mock_reddit_br_001",
                "platform": "reddit",
                "country": "BR",
                "source_channel": "r/saopaulo",
                "title": "Alguém tem indicação de encanador de confiança na Zona Sul?",
                "content": "Boa tarde pessoal, estou com um vazamento chato no banheiro do apartamento e preciso de um encanador urgente que cobre um preço justo na região da Vila Mariana. Se alguém tiver contato de profissional de confiança, agradeço!",
                "url": "https://reddit.com/r/saopaulo/comments/mock_br_001",
                "author": "carlos_sp99",
                "created_utc": time.time() - 3600,
            },
            {
                "id": "mock_reddit_br_002",
                "platform": "reddit",
                "country": "BR",
                "source_channel": "r/trampos",
                "title": "Sou eletricista autônomo, como vocês conseguem clientes na internet?",
                "content": "Trabalho há 4 anos com instalações elétricas residenciais e comerciais. O boca a boca está fraco ultimamente. Quais aplicativos ou plataformas vocês usam para divulgar serviço e conseguir renda extra sem tomar golpe?",
                "url": "https://reddit.com/r/trampos/comments/mock_br_002",
                "author": "marcos_eletro",
                "created_utc": time.time() - 7200,
            },
            {
                "id": "mock_reddit_mx_001",
                "platform": "reddit",
                "country": "MX",
                "source_channel": "r/MexicoCity",
                "title": "¿Alguien que recomiende un buen plomero o electricista en la alcaldía Cuauhtémoc?",
                "content": "Hola vecinos, estoy remodelando la cocina y busco plomero de confianza para cambiar tuberías y poner una tarja nueva. Si alguien tiene el contacto de alguien que trabaje bien y no cobre excesivo, se los agradecería mucho.",
                "url": "https://reddit.com/r/MexicoCity/comments/mock_mx_001",
                "author": "rodrigo_cdmx",
                "created_utc": time.time() - 4000,
            },
            {
                "id": "mock_reddit_mx_002",
                "platform": "reddit",
                "country": "MX",
                "source_channel": "r/Guadalajara",
                "title": "Hago trabajos de albañilería, yeso y pintura en ZMG, ¿dónde recomiendan anunciarse?",
                "content": "Buenas tardes amigos. Llevo años trabajando en albañilería y pintura en Guadalajara y Zapopan. ¿Saben de alguna app o grupo confiable para conseguir más chamba de oficio? Me urge conseguir clientes para este mes.",
                "url": "https://reddit.com/r/Guadalajara/comments/mock_mx_002",
                "author": "miguel_constructor",
                "created_utc": time.time() - 5500,
            },
        ]
