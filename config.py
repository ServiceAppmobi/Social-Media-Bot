import os

# ==============================================================================
# CONFIGURAÇÕES GERAIS / USTAWIENIA GŁÓWNE
# ==============================================================================
APP_NAME = os.getenv("APP_NAME") or "ServiceApp"
APP_URL = os.getenv("APP_URL") or "https://serviceapp.mobi"
GOOGLE_PLAY_URL = (
    os.getenv("GOOGLE_PLAY_URL")
    or "https://play.google.com/store/apps/details?id=pl.serviceapp&pli=1"
)

# Wartości marketingowe dla języków docelowych
APP_VALUE_PROPOSITION_BR_CLIENT = (
    "uma plataforma onde você encontra e compara orçamentos de profissionais autônomos "
    "e prestadores de serviços avaliados na sua região"
)
APP_VALUE_PROPOSITION_BR_WORKER = (
    "um aplicativo para autônomos e freelancers encontrarem clientes locais, "
    "receberem pedidos de orçamento e aumentarem a renda sem burocracia"
)
APP_VALUE_PROPOSITION_MX_CLIENT = (
    "una plataforma confiable donde puedes encontrar y comparar cotizaciones de profesionales "
    "y trabajadores de oficio calificados en tu zona"
)
APP_VALUE_PROPOSITION_MX_WORKER = (
    "una app para trabajadores independientes, técnicos y especialistas para conseguir más clientes, "
    "recibir solicitudes de trabajo y generar ingresos extra de forma segura"
)
APP_VALUE_PROPOSITION_EN_CLIENT = (
    "a local services app where you can request free quotes and compare rated plumbers, "
    "electricians, cleaners, and handymen near you"
)
APP_VALUE_PROPOSITION_EN_WORKER = (
    "a mobile app that connects independent tradespeople, technicians, and freelancers "
    "directly with local customers looking for services"
)
APP_VALUE_PROPOSITION_FR_CLIENT = (
    "une application locale pour demander des devis gratuits et comparer des artisans "
    "et professionnels évalués près de chez vous"
)
APP_VALUE_PROPOSITION_FR_WORKER = (
    "une application qui met en relation les travailleurs autonomes et artisans "
    "avec des clients locaux qui recherchent des services"
)
APP_VALUE_PROPOSITION_JA_CLIENT = (
    "お近くの信頼できる水道・電気・清掃・リフォームなどの専門業者を比較し、無料で見積もり依頼できるアプリ"
)
APP_VALUE_PROPOSITION_JA_WORKER = (
    "地元の顧客から直接仕事や見積もり依頼を受け取れる、個人事業主・技術者向けのサービスマッチングアプリ"
)

# ==============================================================================
# RESEND & EMAIL NOTIFICATIONS
# ==============================================================================
RESEND_API_KEY = os.getenv("RESEND_API_KEY") or ""

EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT") or "karolak.pawel@gmail.com"
EMAIL_SENDER = os.getenv("EMAIL_SENDER") or "onboarding@resend.dev"

SMTP_HOST = os.getenv("SMTP_HOST") or "smtp.resend.com"
SMTP_PORT = int(os.getenv("SMTP_PORT") or "465")
SMTP_USER = os.getenv("SMTP_USER") or "resend"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or ""
SMTP_USE_TLS = (os.getenv("SMTP_USE_TLS") or "true").lower() in ("true", "1", "yes")

# ==============================================================================
# TELEGRAM & NTFY PUSH NOTIFICATIONS (Opcjonalne - na iPhone)
# ==============================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or ""
NTFY_TOPIC = os.getenv("NTFY_TOPIC") or ""
NTFY_SERVER = os.getenv("NTFY_SERVER") or "https://ntfy.sh"

# ==============================================================================
# AI / GEMINI API (Interactions API v1 — Free Tier friendly)
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION") or "v1"
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS") or "30")

# ==============================================================================
# GLOBAL MONITORING: AMERYKA PŁD. + AMERYKA PŁN. + SINGAPUR + JAPONIA
# ==============================================================================
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID") or ""
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET") or ""
REDDIT_USER_AGENT = (
    os.getenv("REDDIT_USER_AGENT")
    or "ServiceAppGlobalMonitor/2.2 (+https://serviceapp.mobi)"
)
MAX_POST_AGE_DAYS = int(os.getenv("MAX_POST_AGE_DAYS") or "14")
MASTODON_ENABLED = (os.getenv("MASTODON_ENABLED") or "true").lower() in ("true", "1", "yes")

COUNTRIES = {
    # --- South America (All 12 countries) ---
    "BR": {
        "name": "Brazylia",
        "flag": "🇧🇷",
        "lang": "pt",
        "lang_label": "Português (PT-BR)",
        "badge_color": "#16a34a",
        "subreddits": ["brasil", "saopaulo", "riodejaneiro", "curitiba", "belohorizonte", "trampos", "brdev"],
    },
    "AR": {
        "name": "Argentyna",
        "flag": "🇦🇷",
        "lang": "es",
        "lang_label": "Español (ES-AR)",
        "badge_color": "#0284c7",
        "subreddits": ["argentina", "BuenosAires", "Cordoba"],
    },
    "CO": {
        "name": "Kolumbia",
        "flag": "🇨🇴",
        "lang": "es",
        "lang_label": "Español (ES-CO)",
        "badge_color": "#ca8a04",
        "subreddits": ["Colombia", "Bogota", "medellin"],
    },
    "CL": {
        "name": "Chile",
        "flag": "🇨🇱",
        "lang": "es",
        "lang_label": "Español (ES-CL)",
        "badge_color": "#dc2626",
        "subreddits": ["chile", "Santiago"],
    },
    "PE": {
        "name": "Peru",
        "flag": "🇵🇪",
        "lang": "es",
        "lang_label": "Español (ES-PE)",
        "badge_color": "#b91c1c",
        "subreddits": ["PERU", "Lima"],
    },
    "EC": {
        "name": "Ekwador",
        "flag": "🇪🇨",
        "lang": "es",
        "lang_label": "Español (ES-EC)",
        "badge_color": "#d97706",
        "subreddits": ["ecuador", "Quito"],
    },
    "VE": {
        "name": "Wenezuela",
        "flag": "🇻🇪",
        "lang": "es",
        "lang_label": "Español (ES-VE)",
        "badge_color": "#991b1b",
        "subreddits": ["vzla", "venezuela"],
    },
    "UY": {
        "name": "Urugwaj",
        "flag": "🇺🇾",
        "lang": "es",
        "lang_label": "Español (ES-UY)",
        "badge_color": "#2563eb",
        "subreddits": ["uruguay"],
    },
    "PY": {
        "name": "Paragwaj",
        "flag": "🇵🇾",
        "lang": "es",
        "lang_label": "Español (ES-PY)",
        "badge_color": "#dc2626",
        "subreddits": ["Paraguay"],
    },
    "BO": {
        "name": "Boliwia",
        "flag": "🇧🇴",
        "lang": "es",
        "lang_label": "Español (ES-BO)",
        "badge_color": "#15803d",
        "subreddits": ["BOLIVIA"],
    },
    "GY": {
        "name": "Gujana",
        "flag": "🇬🇾",
        "lang": "en",
        "lang_label": "English (GY)",
        "badge_color": "#15803d",
        "subreddits": ["Guyana"],
    },
    "SR": {
        "name": "Surinam",
        "flag": "🇸🇷",
        "lang": "nl",
        "lang_label": "Nederlands / English (SR)",
        "badge_color": "#166534",
        "subreddits": ["Suriname"],
    },
    # --- North America (Mexico, US, Canada) ---
    "MX": {
        "name": "Meksyk",
        "flag": "🇲🇽",
        "lang": "es",
        "lang_label": "Español (ES-MX)",
        "badge_color": "#dc2626",
        "subreddits": ["mexico", "MexicoCity", "Monterrey", "Guadalajara", "Puebla", "Tijuana", "lacamiseta"],
    },
    "US": {
        "name": "USA",
        "flag": "🇺🇸",
        "lang": "en",
        "lang_label": "English (US)",
        "badge_color": "#1d4ed8",
        "subreddits": ["HomeImprovement", "handyman", "Plumbing", "sidehustle", "sweatystartup"],
    },
    "CA": {
        "name": "Kanada",
        "flag": "🇨🇦",
        "lang": "en",
        "lang_label": "English / Français (CA)",
        "badge_color": "#b91c1c",
        "subreddits": ["canada", "toronto", "vancouver", "montreal", "Calgary"],
    },
    # --- Asia (Singapore & Japan) ---
    "SG": {
        "name": "Singapur",
        "flag": "🇸🇬",
        "lang": "en",
        "lang_label": "English (SG)",
        "badge_color": "#e11d48",
        "subreddits": ["singapore", "askSingapore", "SingaporeRaw"],
    },
    "JP": {
        "name": "Japonia",
        "flag": "🇯🇵",
        "lang": "ja",
        "lang_label": "日本語 / English (JP)",
        "badge_color": "#be123c",
        "subreddits": ["japanlife", "tokyo", "Osaka", "newsokur"],
    },
}


def get_country_info(country_code: str) -> dict:
    code = (country_code or "BR").upper()
    return COUNTRIES.get(
        code,
        {
            "name": code,
            "flag": "🌎",
            "lang": "en",
            "lang_label": "English",
            "badge_color": "#334155",
            "subreddits": [],
        },
    )


# Kompatybilność wsteczna dla stałych
TARGET_SUBREDDITS_BR = COUNTRIES["BR"]["subreddits"]
TARGET_SUBREDDITS_MX = COUNTRIES["MX"]["subreddits"]

MASTODON_TAG_GROUPS = [
    ("BR", "pt", ["emprego", "trampos", "freelancer", "servicos"]),
    ("MX", "es", ["chamba", "trabajo", "empleo", "latam"]),
    ("US", "en", ["handyman", "freelance", "sidehustle", "smallbusiness"]),
    ("SG", "en", ["singapore"]),
    ("JP", "ja", ["副業", "フリーランス", "仕事"]),
]
MASTODON_TAGS_BR = ["emprego", "trampos", "freelancer", "servicos"]
MASTODON_TAGS_MX = ["chamba", "trabajo", "empleo", "latam"]

KEYWORDS_BR_SERVICE = ["preciso de encanador", "preciso de eletricista", "preciso de diarista", "orçamento reforma"]
KEYWORDS_BR_WORK = ["trabalho autônomo", "como conseguir clientes", "procurando trampo", "renda extra"]
KEYWORDS_MX_SERVICE = ["busco plomero", "busco electricista", "recomienden albañil", "cotización para remodelación"]
KEYWORDS_MX_WORK = ["busco chamba", "ofrezco mis servicios", "trabajador independiente", "ingreso extra"]

# ==============================================================================
# 🟢 WHATSAPP GROUPS MONITORING
# ==============================================================================
WHATSAPP_WEBHOOK_PORT = int(os.getenv("WHATSAPP_WEBHOOK_PORT", "8088"))
WHATSAPP_ENABLED = os.getenv("WHATSAPP_ENABLED", "true").lower() in ("true", "1", "yes")

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "1800"))
DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")
