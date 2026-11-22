import re
from typing import Optional, Tuple
from config import (
    APP_NAME,
    APP_URL,
    APP_VALUE_PROPOSITION_BR_CLIENT,
    APP_VALUE_PROPOSITION_BR_WORKER,
    APP_VALUE_PROPOSITION_MX_CLIENT,
    APP_VALUE_PROPOSITION_MX_WORKER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
)
from gemini_client import GeminiAPIError, GeminiClient

LEAD_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["SERVICE_SEEKER", "WORK_SEEKER", "IRRELEVANT"],
            "description": "Classified intent of the post author.",
        },
        "draft_reply": {
            "type": "string",
            "description": "Natural 2-4 sentence reply in the local dialect, or empty string if IRRELEVANT.",
        },
    },
    "required": ["intent", "draft_reply"],
}


class PostAnalyzer:
    def __init__(
        self,
        api_key: str = GEMINI_API_KEY,
        model: str = GEMINI_MODEL,
        gemini_client: Optional[GeminiClient] = None,
    ):
        self.gemini_client = gemini_client or GeminiClient(
            api_key=api_key,
            default_model=model,
        )
        self.api_key = self.gemini_client.api_key

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

        # 2. Jeśli mamy klucz Gemini, tworzymy hiper-spersonalizowany draft przez Interactions API
        if self.gemini_client.is_configured():
            try:
                ai_result = self._gemini_analyze(title, content, country)
                if ai_result:
                    return ai_result
            except (GeminiAPIError, ValueError, KeyError) as e:
                print(f"[!] Błąd wywołania Gemini API ({e}). Używam silnika regułowego.")

        # 3. Tryb regułowy z szablonami PT-BR (Brazylia) lub ES-MX (Meksyk)
        draft = self._generate_heuristic_draft(heuristic_type, country, title, content)
        return heuristic_type, draft

    def _heuristic_classification(self, text: str, country: str) -> str:
        """Klasyfikacja intencji na bazie wzorców językowych dla Brazylii i Meksyku."""
        if country == "MX":
            # Meksyk (Hiszpański es-MX)
            mx_service_patterns = [
                r"(busco|necesito) (un |una )?(buen |buena )?(plomero|electricista|albañil|pintor|técnico|tecnico|carpintero|cerrajero|herrero|jardinero|mec[aá]nico|técnico de|tecnico de)",
                r"(recomienden|alguien recomienda|conocen a|alg[uú]n contacto de) (un |una )?(buen |buena )?(plomero|electricista|albañil|pintor|carpintero|cerrajero|técnico|tecnico|señora de limpieza|mantenimiento)",
                r"cotizaci[oó]n para (remodelaci[oó]n|trabajo|reparaci[oó]n|pintura|plomer[ií]a|electricidad|obra)",
                r"alguien que haga trabajos de",
                r"necesito contratar (a alguien|un servicio)",
                r"busco (señora|persona|alguien) (de|para) limpieza",
                r"(recomienden|busco) servicio de (limpieza|mudanza|reparaci[oó]n|mantenimiento|fumigaci[oó]n|aire acondicionado)",
            ]
            mx_work_patterns = [
                r"(busco|necesito|me urge) (chamba|trabajo|empleo|jale)",
                r"hago trabajos de (albañiler[ií]a|plomer[ií]a|electricidad|pintura|carpinter[ií]a|mantenimiento|reparaci[oó]n)",
                r"ofrezco (mis )?servicios",
                r"d[oó]nde (conseguir clientes|anunciar mi trabajo|ofrecer mis servicios)",
                r"trabajador independiente",
                r"c[oó]mo conseguir (m[aá]s )?(clientes|chamba)",
                r"ingreso(s)? extra",
                r"sin (chamba|trabajo|empleo).{0,40}(ayuda|consejo|d[oó]nde|busco)",
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
                r"(preciso|procuro) (de )?(um |uma )?(bom |boa )?(encanador|eletricista|diarista|faxineira|pedreiro|pintor|marceneiro|chaveiro|jardineiro|técnico|tecnico|montador|profissional|marido de aluguel)",
                r"(alguém|alguem) (indica|recomenda|conhece|tem contato de?) (um |uma )?(bom |boa )?(encanador|eletricista|diarista|faxineira|pedreiro|pintor|marceneiro|chaveiro|técnico|tecnico|montador|profissional|marido de aluguel|limpeza)",
                r"indica[cç][aã]o de (um |uma )?(encanador|eletricista|diarista|pedreiro|pintor|profissional|faxineira|técnico|tecnico|marceneiro|chaveiro|reforma)",
                r"or[cç]amento para (reforma|pintura|obra|servi[cç]o|reparo|instala[cç][aã]o|mudan[cç]a)",
                r"contratar (servi[cç]o|pessoa|alguém|alguem|profissional|diarista|pedreiro|eletricista|encanador)",
                r"onde encontro (um |uma )?(profissional|pessoa que fa[cç]a|técnico|tecnico|diarista|pedreiro|eletricista|encanador)",
            ]
            br_work_patterns = [
                r"como conseguir clientes",
                r"onde divulgar (meu trabalho|meus servi[cç]os)",
                r"trabalho aut[oô]nomo",
                r"(procurando|precisando de|buscando) (tramp[oa]|bico|renda extra|trabalho|emprego|servi[cç]o|freela)",
                r"preciso de ajuda para encontrar (emprego|trabalho|trampo|servi[cç]o)",
                r"sou (eletricista|encanador|pintor|pedreiro|marceneiro|técnico|tecnico|aut[oô]nomo|diarista).{0,60}(cliente|servi[cç]o|trabalho|trampo|divulgar|renda)",
                r"fa[cç]o servi[cç]os de (el[eé]trica|hidr[aá]ulica|pintura|reforma|manuten[cç][aã]o|limpeza|marcenaria)",
                r"plataforma para (aut[oô]nomos|freelancer|prestar servi[cç]os)",
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

    def _gemini_analyze(self, title: str, content: str, country: str) -> Optional[Tuple[str, Optional[str]]]:
        """Używa Google Gemini Interactions API do analizy i odpowiedzi w PT-BR lub ES-MX."""
        country_name = "México" if country == "MX" else "Brasil"
        language_spec = (
            "Español de México (ES-MX), usando modismos naturales como 'chamba', 'cotización', etc."
            if country == "MX"
            else "Português do Brasil (PT-BR), tom natural e amigável."
        )

        system_instruction = (
            f"Você é um especialista em marketing de relacionamento para o aplicativo '{APP_NAME}' ({APP_URL}) "
            f"no país: {country_name}. O {APP_NAME} é uma plataforma que conecta pessoas que precisam de "
            "serviços (reformas, encanadores, eletricistas, diaristas, técnicos) com profissionais locais "
            "qualificados. Classifique a intenção do autor ('SERVICE_SEEKER', 'WORK_SEEKER' ou 'IRRELEVANT') "
            f"e, quando relevante, escreva uma resposta natural, prestativa e empática de 2 a 4 frases em "
            f"{language_spec} recomendando o {APP_NAME} sem parecer spam."
        )

        user_prompt = (
            f"PAÍS: {country_name}\n"
            f"TÍTULO: {title}\n"
            f"CONTEÚDO: {content}"
        )

        parsed, _ = self.gemini_client.create_structured_json(
            input_data=user_prompt,
            schema=LEAD_ANALYSIS_SCHEMA,
            system_instruction=system_instruction,
            temperature=0.4,
            store=False,
        )

        if not isinstance(parsed, dict):
            return None

        intent = parsed.get("intent", "IRRELEVANT")
        if intent not in ("SERVICE_SEEKER", "WORK_SEEKER", "IRRELEVANT"):
            return None

        if intent == "IRRELEVANT":
            return "IRRELEVANT", None

        draft_reply = (parsed.get("draft_reply") or "").strip()
        return intent, draft_reply
