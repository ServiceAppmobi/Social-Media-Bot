import json
import time
import unittest
from unittest.mock import patch

from monitors.mastodon_monitor import MastodonMonitor
from monitors.reddit_monitor import RedditMonitor


class _FakeHTTPResponse:
    def __init__(self, payload, status=200):
        self._body = json.dumps(payload).encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestRedditMonitor(unittest.TestCase):
    def test_fetches_recent_posts_via_arctic_shift_without_auth(self):
        captured = {}
        now = time.time()

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            return _FakeHTTPResponse(
                {
                    "data": [
                        {
                            "id": "abc123",
                            "subreddit": "saopaulo",
                            "title": "Preciso de encanador urgente",
                            "selftext": "Vazamento na cozinha na Zona Sul",
                            "permalink": "/r/saopaulo/comments/abc123/preciso_de_encanador/",
                            "author": "joao_sp",
                            "created_utc": now - 600,
                        },
                        {
                            "id": "old999",
                            "subreddit": "saopaulo",
                            "title": "Post antigo",
                            "selftext": "De um ano atrás",
                            "permalink": "/r/saopaulo/comments/old999/post_antigo/",
                            "author": "old_user",
                            "created_utc": now - (30 * 86400),
                        },
                    ]
                }
            )

        monitor = RedditMonitor(client_id="", client_secret="", max_age_days=14)
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            posts = monitor.fetch_posts_for_subreddit("saopaulo", country="BR", limit=50)

        self.assertIn("arctic-shift.photon-reddit.com/api/posts/search", captured["url"])
        self.assertIn("subreddit=saopaulo", captured["url"])
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], "reddit_abc123")
        self.assertEqual(posts[0]["country"], "BR")
        self.assertEqual(posts[0]["source_channel"], "r/saopaulo")
        self.assertEqual(posts[0]["url"], "https://reddit.com/r/saopaulo/comments/abc123/preciso_de_encanador/")


class TestMastodonMonitor(unittest.TestCase):
    def test_filters_language_and_strips_html(self):
        def fake_urlopen(req, timeout=None):
            return _FakeHTTPResponse(
                [
                    {
                        "id": "m1",
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "language": "es",
                        "content": "<p>Busco <strong>plomero</strong> en CDMX urgente</p>",
                        "url": "https://mastodon.social/@ana/1",
                        "account": {"acct": "ana@mastodon.social"},
                    },
                    {
                        "id": "m2",
                        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "language": "en",
                        "content": "<p>Unrelated English post</p>",
                        "url": "https://mastodon.social/@bob/2",
                        "account": {"acct": "bob@mastodon.social"},
                    },
                ]
            )

        monitor = MastodonMonitor(max_age_days=14)
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            posts = monitor.scan_tag("mastodon.social", "chamba", country="MX", limit=10)

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], "mastodon_m1")
        self.assertEqual(posts[0]["country"], "MX")
        self.assertEqual(posts[0]["content"], "Busco plomero en CDMX urgente")


if __name__ == "__main__":
    unittest.main()
