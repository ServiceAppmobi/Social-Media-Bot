import os
import json

# ==============================================================================
# CONFIGURAÇÕES GERAIS / USTAWIENIA GŁÓWNE
# ==============================================================================

APP_NAME = os.getenv("APP_NAME") or "ServiceApp"
APP_URL = os.getenv("APP_URL") or "https://serviceapp.mobi"

# Wartości marketingowe dla Brazylii (PT-BR)
APP_VALUE_PROPOSITION_BR_CLIENT = (
    "uma plataforma onde você encontra e compara orçamentos de profissionais autônomos "
    "e prestadores de serviços avaliados na sua região"
)
APP_VALUE_PROPOSITION_BR_WORKER = (
    "um aplicativo para autônomos e freelancers encontrarem clientes locais, "
    "receberem pedidos de orçamento e aumentarem a renda sem burocracia"
)

# Wartości marketingowe dla Meksyku (ES-MX)
APP_VALUE_PROPOSITION_MX_CLIENT = (
    "una plataforma confiable donde puedes encontrar y comparar cotizaciones de profesionales "
    "y trabajadores de oficio calificados en tu zona"
)
APP_VALUE_PROPOSITION_MX_WORKER = (
    "una app para trabajadores independientes, técnicos y especialistas para conseguir más clientes, "
    "recibir solicitudes de chamba y generar ingresos extra de forma segura"
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
# AI / GEMINI API (Interactions API v1 — opcjonalne)
# ==============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite"
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION") or "v1"
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT_SECONDS") or "30")

# ==============================================================================
# 🇧🇷 MONITORING SOCIAL MEDIA - BRAZYLIA (PT-BR)
# ==============================================================================
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID") or ""
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET") or ""
REDDIT_USER_AGENT = (
    os.getenv("REDDIT_USER_AGENT")
    or "ServiceAppLatAmMonitor/2.1 (+https://serviceapp.mobi)"
)
MAX_POST_AGE_DAYS = int(os.getenv("MAX_POST_AGE_DAYS") or "14")

MASTODON_ENABLED = (os.getenv("MASTODON_ENABLED") or "true").lower() in ("true", "1", "yes")
MASTODON_TAGS_BR = ["emprego", "trampos", "freelancer", "servicos"]
MASTODON_TAGS_MX = ["chamba", "trabajo", "empleo", "mexico"]

TARGET_SUBREDDITS_BR = [
    "brasil",
    "saopaulo",
    "riodejaneiro",
    "curitiba",
    "belohorizonte",
    "trampos",
    "brdev",
    "ConselhosLegais",
    "conversas"
]

KEYWORDS_BR_SERVICE = [
    "preciso de encanador",
    "preciso de eletricista",
    "preciso de diarista",
    "preciso de pintor",
    "indicação de pedreiro",
    "indicação de diarista",
    "alguém indica pintor",
    "alguém indica eletricista",
    "orçamento reforma",
    "procuro profissional para",
    "contratar serviço de",
    "alguém conhece quem faça"
]

KEYWORDS_BR_WORK = [
    "preciso de renda extra",
    "procurando trampo",
    "trabalho autônomo",
    "como conseguir clientes serviços",
    "onde divulgar meu trabalho",
    "procurando bico",
    "precisando trabalhar urgente",
    "faço serviços de"
]

# ==============================================================================
# 🇲🇽 MONITORING SOCIAL MEDIA - MEKSYK (ES-MX)
# ==============================================================================
TARGET_SUBREDDITS_MX = [
    "mexico",
    "MexicoCity",
    "Monterrey",
    "Guadalajara",
    "Puebla",
    "Tijuana",
    "ChambasMexico",
    "lacamiseta",
    "taquerosprogramadores"
]

KEYWORDS_MX_SERVICE = [
    "busco plomero",
    "busco electricista",
    "recomienden albañil",
    "busco señora de limpieza",
    "recomienden pintor",
    "alguien que haga trabajos de",
    "cotización para remodelación",
    "busco técnico de confianza",
    "recomienden cerrajero",
    "necesito contratar a alguien"
]

KEYWORDS_MX_WORK = [
    "busco chamba urgente",
    "dónde conseguir clientes",
    "hago trabajos de plomería",
    "ofrezco mis servicios",
    "trabajador independiente",
    "busco ingresos extra",
    "cómo conseguir más chamba",
    "busco trabajo de oficio"
]

# ==============================================================================
# 🟢 WHATSAPP GROUPS MONITORING
# ==============================================================================
# Port lokalnego webservera webhooka odbierającego wiadomości z grup WhatsApp
WHATSAPP_WEBHOOK_PORT = int(os.getenv("WHATSAPP_WEBHOOK_PORT", "8088"))
WHATSAPP_ENABLED = os.getenv("WHATSAPP_ENABLED", "true").lower() in ("true", "1", "yes")

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "1800"))
DB_PATH = os.path.join(os.path.dirname(__file__), "leads.db")
