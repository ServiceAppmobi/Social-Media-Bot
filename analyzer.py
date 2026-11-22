import re
import json
import urllib.request
import urllib.error
from typing import Tuple, Optional
from config import (
    APP_NAME,
    APP_URL,
    APP_VALUE_PROPOSITION_BR_CLIENT,
    APP_VALUE_PROPOSITION_BR_WORKER,
    APP_VALUE_PROPOSITION_MX_CLIENT,
    APP_VALUE_PROPOSITION_MX_WORKER,
    GEMINI_API_KEY,
    GEMINI_MODEL
)

class PostAnalyzer:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key

    def analyze_post(self, title: str, content: str, country: str = "BR") -> Tuple[str, Optional[str]]:
        """
        Analizuje treść wpisu z Brazylii (PT-BR) lub Meksyku (ES-MX).
        Zwraca: (lead_type, draft_response)
        """
        combined_text = f"{title}\n{content}".lower()

        # 1. Klasyfikacja intencji (regułowa z uwzględnieniem kraju)
        heuristic_type = self._heuristic_classification(combined_text, country)
        if heuristic_type == "IRRELEVANT":
            return "IRRELEVANT", None

        # 2. Jeśli mamy klucz Gemini, tworzymy hiper-spersonalizowany draft w odpowiednim języku
        if self.api_key:
            try:
                ai_result = self._gemini_analyze(title, content, country)
                if ai_result:
                    return ai_result
            except Exception as e:
                print(f"[!] Błąd wywołania Gemini API ({e}). Używam silnika regułowego.")

        # 3. Tryb regułowy z szablonami PT-BR (Brazylia) lub ES-MX (Meksyk)
        draft = self._generate_heuristic_draft(heuristic_type, country, title, content)
        return heuristic_type, draft

    def _heuristic_classification(self, text: str, country: str) -> str:
        """Klasyfikacja intencji na bazie wzorców językowych dla Brazylii i Meksyku."""
        if country == "MX":
            # Meksyk (Hiszpański es-MX)
            mx_service_patterns = [
                r"busco (un |una )?(plomero|electricista|albañil|pintor|técnico|carpintero|cerrajero)",
                r"(recomienden|alguien recomienda|conocen a) (un |una )?(plomero|electricista|albañil|señora de limpieza)",
                r"cotizaci[o|ó]n para (remodelaci[o|ó]n|trabajo|reparaci[o|ó]n)",
                r"alguien que haga trabajos de",
                r"necesito contratar (a alguien|un servicio)",
                r"busco señora de limpieza"
            ]
            mx_work_patterns = [
                r"busco (chamba|trabajo|empleo)",
                r"hago trabajos de (albañiler[i|í]a|plomer[i|í]a|electricidad|pintura)",
                r"ofrezco mis servicios",
                r"d[o|ó]nde (conseguir clientes|anunciar mi trabajo)",
                r"trabajador independiente",
                r"me urge (chamba|trabajar)",
                r"ingreso extra"
            ]

            for p in mx_service_patterns:
                if re.search(p, text):
                    return "SERVICE_SEEKER"
            for p in mx_work_patterns:
                if re.search(p, text):
                    return "WORK_SEEKER"

        else:
            # Brazylia (Portugalski pt-BR)
            br_service_patterns = [
                r"preciso de (um |uma )?(encanador|eletricista|diarista|pedreiro|pintor|marceneiro|técnico|profissional)",
                r"alguém (indica|recomenda|tem contato)",
                r"indicação de (um |uma )?(encanador|eletricista|diarista|pedreiro|pintor|profissional|faxineira)",
                r"orçamento para",
                r"contratar (serviço|pessoa|alguém)",
                r"onde encontro (um |uma )?(profissional|pessoa que faça)"
            ]
            br_work_patterns = [
                r"como conseguir clientes",
                r"onde divulgar (meu trabalho|meus serviços)",
                r"trabalho autônomo",
                r"procurando (tramp[o|a]|bico|renda extra|trabalho)",
                r"sou (eletricista|encanador|pintor|técnico|autônomo)",
                r"precisando de trabalho urgente",
                r"plataforma para (autônomos|freelancer)"
            ]

            for p in br_service_patterns:
                if re.search(p, text):
                    return "SERVICE_SEEKER"
            for p in br_work_patterns:
                if re.search(p, text):
                    return "WORK_SEEKER"

        return "IRRELEVANT"

    def _generate_heuristic_draft(self, lead_type: str, country: str, title: str, content: str) -> str:
        """Generuje naturalną odpowiedź dopasowaną do kraju i języka."""
        if country == "MX":
            # Meksyk (Hiszpański es-MX)
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"¡Hola! Si todavía estás buscando, te recomiendo checar {APP_NAME} ({APP_URL}). "
                    f"Es {APP_VALUE_PROPOSITION_MX_CLIENT}. "
                    f"Puedes solicitar cotizaciones gratis y comparar las opiniones de otros clientes antes de contratar. "
                    f"¡Ojalá te sirva para solucionar rápido el trabajo!"
                )
            elif lead_type == "WORK_SEEKER":
                return (
                    f"¡Qué tal colega! Para conseguir más chamba además de tus conocidos, vale la pena registrarte en {APP_NAME} ({APP_URL}). "
                    f"Es {APP_VALUE_PROPOSITION_MX_WORKER}. "
                    f"El registro es fácil y te conecta directo con personas que están buscando servicios en tu colonia o municipio. "
                    f"¡Mucho éxito con la chamba!"
                )
        else:
            # Brazylia (Portugalski pt-BR)
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"Olá! Se ainda estiver procurando, dá uma olhada no {APP_NAME} ({APP_URL}). "
                    f"É {APP_VALUE_PROPOSITION_BR_CLIENT}. "
                    f"Dá para solicitar orçamentos sem compromisso e ver as avaliações de outros clientes antes de fechar. "
                    f"Espero que ajude a resolver logo!"
                )
            elif lead_type == "WORK_SEEKER":
                return (
                    f"Fala parceiro! Para divulgar seu serviço além do boca a boca, vale a pena dar uma olhada no {APP_NAME} ({APP_URL}). "
                    f"É {APP_VALUE_PROPOSITION_BR_WORKER}. "
                    f"O cadastro é simples e ajuda bastante a conectar com quem está precisando de atendimento no seu bairro/cidade. "
                    f"Boa sorte na captação!"
                )
        return ""

    def _gemini_analyze(self, title: str, content: str, country: str) -> Optional[Tuple[str, str]]:
        """Używa Google Gemini do analizy i wygenerowania odpowiedzi w dialekcie PT-BR lub ES-MX."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={self.api_key}"
        
        country_name = "México" if country == "MX" else "Brasil"
        language_spec = "Español de México (ES-MX), usando modismos naturales como 'chamba', 'cotización', etc." if country == "MX" else "Português do Brasil (PT-BR), tom natural e amigável."

        prompt = f"""
Você é um especialista em marketing de relacionamento para o aplicativo '{APP_NAME}' ({APP_URL}) no país: {country_name}.
O {APP_NAME} é uma plataforma que conecta pessoas que precisam de serviços (reformas, encanadores, eletricistas, diaristas, técnicos) com profissionais locais qualificados.

Analise a seguinte publicação de fórum, rede social ou grupo de WhatsApp:
PAÍS: {country_name}
TÍTULO: {title}
CONTEÚDO: {content}

TAREFAS:
1. Determine a intenção do autor:
   - 'SERVICE_SEEKER' se o autor estiver buscando contratar um serviço/trabalhador ou pedindo orçamentos/indicações.
   - 'WORK_SEEKER' se for um trabalhador/autônomo buscando clientes, perguntando onde divulgar ou precisando de trabalho/chamba/renda extra.
   - 'IRRELEVANT' se não tiver relação com contratação de serviços ou busca de trabalho autônomo.

2. Se for 'SERVICE_SEEKER' ou 'WORK_SEEKER', escreva uma sugestão de resposta:
   - Idioma: {language_spec}
   - Tom: Natural, prestativo, empático, não pareça um robô ou spam.
   - Recomende o {APP_NAME} como uma solução prática.
   - Tamanho: 2 a 4 frases.

Responda ESTRITAMENTE em formato JSON:
{{
  "intent": "SERVICE_SEEKER" | "WORK_SEEKER" | "IRRELEVANT",
  "draft_reply": "texto da resposta"
}}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "response_mime_type": "application/json"}
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                result_json = json.loads(resp.read().decode("utf-8"))
                text_part = result_json["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_part)
                return parsed.get("intent", "IRRELEVANT"), parsed.get("draft_reply", "")

        return None
