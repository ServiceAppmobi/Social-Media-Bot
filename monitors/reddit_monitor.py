import urllib.request
import urllib.parse
import urllib.error
import json
import time
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from config import (
    TARGET_SUBREDDITS_BR, KEYWORDS_BR_SERVICE, KEYWORDS_BR_WORK,
    TARGET_SUBREDDITS_MX, KEYWORDS_MX_SERVICE, KEYWORDS_MX_WORK
)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 ServiceAppLeadFinder/2.0"

class RedditMonitor:
    def __init__(self):
        pass

    def _build_search_query(self, keywords: List[str]) -> str:
        """Buduje zapytanie OR ze słów kluczowych dla wyszukiwarki Reddita."""
        phrases = [f'"{kw}"' for kw in keywords[:5]]
        return " OR ".join(phrases)

    def _fetch_via_rss(self, subreddit: str, encoded_query: str, country: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback przez kanał RSS Reddita (przydatny w środowiskach chmurowych jak GitHub Actions)."""
        rss_url = f"https://www.reddit.com/r/{subreddit}/search.rss?q={encoded_query}&sort=new&t=month&restrict_sr=1&limit={limit}"
        req = urllib.request.Request(rss_url, headers={"User-Agent": USER_AGENT})
        posts = []
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    ns = {"atom": "http://www.w3.org/2005/Atom"}
                    for entry in root.findall("atom:entry", ns)[:limit]:
                        entry_id = entry.findtext("atom:id", default="", namespaces=ns)
                        short_id = entry_id.split("_")[-1] if "_" in entry_id else entry_id.rsplit("/", 1)[-1]
                        title = entry.findtext("atom:title", default="", namespaces=ns)
                        link_el = entry.find("atom:link", ns)
                        url = link_el.attrib.get("href", "") if link_el is not None else ""
                        author_el = entry.find("atom:author/atom:name", ns)
                        author = (author_el.text or "anônimo").replace("/u/", "") if author_el is not None else "anônimo"
                        raw_content = entry.findtext("atom:content", default="", namespaces=ns)
                        clean_content = re.sub(r"<[^>]+>", " ", raw_content)
                        clean_content = re.sub(r"\s+", " ", clean_content).strip()

                        if short_id and title:
                            posts.append({
                                "id": f"reddit_{short_id}",
                                "platform": "reddit",
                                "country": country,
                                "source_channel": f"r/{subreddit}",
                                "title": title,
                                "content": clean_content[:1000],
                                "url": url,
                                "author": author,
                                "created_utc": time.time()
                            })
        except Exception as e:
            print(f"[!] Fallback RSS dla r/{subreddit} nie powiódł się: {e}")
        return posts

    def fetch_posts_for_subreddit(self, subreddit: str, query: str, country: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Pobiera najświeższe posty z danego subreddita dla zadanego zapytania."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.reddit.com/r/{subreddit}/search.json?q={encoded_query}&sort=new&t=month&restrict_sr=1&limit={limit}"
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT}
        )
        
        posts = []
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status == 200:
                    payload = json.loads(response.read().decode("utf-8"))
                    children = payload.get("data", {}).get("children", [])
                    for child in children:
                        data = child.get("data", {})
                        if data.get("removed_by_category") or data.get("is_robot_indexable") is False:
                            continue
                        
                        posts.append({
                            "id": f"reddit_{data.get('id')}",
                            "platform": "reddit",
                            "country": country,
                            "source_channel": f"r/{subreddit}",
                            "title": data.get("title", ""),
                            "content": data.get("selftext", ""),
                            "url": f"https://reddit.com{data.get('permalink')}",
                            "author": data.get("author", "anônimo"),
                            "created_utc": data.get("created_utc", 0)
                        })
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                print(f"[!] HTTP {e.code} (JSON) na r/{subreddit} — przełączam na fallback RSS...")
                time.sleep(2)
                return self._fetch_via_rss(subreddit, encoded_query, country, limit)
            else:
                print(f"[!] Błąd HTTP {e.code} dla r/{subreddit}: {e.reason}")
        except Exception as e:
            print(f"[!] Błąd połączenia z r/{subreddit}: {e}")
            
        return posts

    def scan_country(self, country: str, subreddits: List[str], service_keywords: List[str], work_keywords: List[str], limit_per_sub: int = 10) -> List[Dict[str, Any]]:
        """Przeszukuje subreddity dla danego kraju."""
        found = []
        queries = [
            ("SERVICE", self._build_search_query(service_keywords)),
            ("WORK", self._build_search_query(work_keywords))
        ]

        for sub in subreddits:
            for cat, q in queries:
                posts = self.fetch_posts_for_subreddit(sub, q, country=country, limit=limit_per_sub)
                found.extend(posts)
                time.sleep(1.2)
        return found

    def scan_all(self, limit_per_sub: int = 10) -> List[Dict[str, Any]]:
        """Przeszukuje zarówno Brazylię (PT-BR), jak i Meksyk (ES-MX)."""
        all_found = []

        # 1. Skanowanie Brazylii
        print("🇧🇷 Skanowanie społeczności w Brazylii...")
        posts_br = self.scan_country("BR", TARGET_SUBREDDITS_BR, KEYWORDS_BR_SERVICE, KEYWORDS_BR_WORK, limit_per_sub)
        all_found.extend(posts_br)

        # 2. Skanowanie Meksyku
        print("🇲🇽 Skanowanie społeczności w Meksyku...")
        posts_mx = self.scan_country("MX", TARGET_SUBREDDITS_MX, KEYWORDS_MX_SERVICE, KEYWORDS_MX_WORK, limit_per_sub)
        all_found.extend(posts_mx)

        # Usunięcie duplikatów
        unique = {p["id"]: p for p in all_found}.values()
        return list(unique)

    @staticmethod
    def get_mock_posts() -> List[Dict[str, Any]]:
        """Zwraca przykładowe posty z Brazylii i Meksyku do celów testowych."""
        return [
            # Brazylia - Klient
            {
                "id": "mock_reddit_br_001",
                "platform": "reddit",
                "country": "BR",
                "source_channel": "r/saopaulo",
                "title": "Alguém tem indicação de encanador de confiança na Zona Sul?",
                "content": "Boa tarde pessoal, estou com um vazamento chato no banheiro do apartamento e preciso de um encanador urgente que cobre um preço justo na região da Vila Mariana. Se alguém tiver contato de profissional de confiança, agradeço!",
                "url": "https://reddit.com/r/saopaulo/comments/mock_br_001",
                "author": "carlos_sp99",
                "created_utc": time.time() - 3600
            },
            # Brazylia - Fachowiec
            {
                "id": "mock_reddit_br_002",
                "platform": "reddit",
                "country": "BR",
                "source_channel": "r/trampos",
                "title": "Sou eletricista autônomo, como vocês conseguem clientes na internet?",
                "content": "Trabalho há 4 anos com instalações elétricas residenciais e comerciais. O boca a boca está fraco ultimamente. Quais aplicativos ou plataformas vocês usam para divulgar serviço e conseguir renda extra sem tomar golpe?",
                "url": "https://reddit.com/r/trampos/comments/mock_br_002",
                "author": "marcos_eletro",
                "created_utc": time.time() - 7200
            },
            # Meksyk - Klient (CDMX)
            {
                "id": "mock_reddit_mx_001",
                "platform": "reddit",
                "country": "MX",
                "source_channel": "r/MexicoCity",
                "title": "¿Alguien que recomiende un buen plomero o electricista en la alcaldía Cuauhtémoc?",
                "content": "Hola vecinos, estoy remodelando la cocina y busco plomero de confianza para cambiar tuberías y poner una tarja nueva. Si alguien tiene el contacto de alguien que trabaje bien y no cobre excesivo, se los agradecería mucho.",
                "url": "https://reddit.com/r/MexicoCity/comments/mock_mx_001",
                "author": "rodrigo_cdmx",
                "created_utc": time.time() - 4000
            },
            # Meksyk - Fachowiec (Guadalajara)
            {
                "id": "mock_reddit_mx_002",
                "platform": "reddit",
                "country": "MX",
                "source_channel": "r/Guadalajara",
                "title": "Hago trabajos de albañilería, yeso y pintura en ZMG, ¿dónde recomiendan anunciarse?",
                "content": "Buenas tardes amigos. Llevo años trabajando en albañilería y pintura en Guadalajara y Zapopan. ¿Saben de alguna app o grupo confiable para conseguir más chamba de oficio? Me urge conseguir clientes para este mes.",
                "url": "https://reddit.com/r/Guadalajara/comments/mock_mx_002",
                "author": "miguel_constructor",
                "created_utc": time.time() - 5500
            }
        ]
