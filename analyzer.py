import re
from typing import Optional, Tuple

from config import (
    APP_NAME,
    APP_URL,
    APP_VALUE_PROPOSITION_BR_CLIENT,
    APP_VALUE_PROPOSITION_BR_WORKER,
    APP_VALUE_PROPOSITION_EN_CLIENT,
    APP_VALUE_PROPOSITION_EN_WORKER,
    APP_VALUE_PROPOSITION_FR_CLIENT,
    APP_VALUE_PROPOSITION_FR_WORKER,
    APP_VALUE_PROPOSITION_JA_CLIENT,
    APP_VALUE_PROPOSITION_JA_WORKER,
    APP_VALUE_PROPOSITION_MX_CLIENT,
    APP_VALUE_PROPOSITION_MX_WORKER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GOOGLE_PLAY_URL,
    get_country_info,
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
            "description": "Natural 2-4 sentence reply in the local language including the Google Play link, or empty string if IRRELEVANT.",
        },
    },
    "required": ["intent", "draft_reply"],
}

JAPANESE_CHAR_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9faf]")
FRENCH_HINT_RE = re.compile(r"\b(plombier|[eé]lectricien|devis|r[eé]novation|cherche un|besoin d'un|travail autonome|m[eé]nage)\b")


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
        Analizuje treść wpisu dla dowolnego z 17 krajów (Ameryka Płd., USA, Kanada, Singapur, Japonia).
        Zwraca: (lead_type, draft_response)
        """
        combined_text = f"{title}\n{content}".lower()
        info = get_country_info(country)
        lang = info["lang"]

        # 1. Klasyfikacja intencji (wielojęzyczna: PT, ES, EN, FR, NL, JA)
        heuristic_type = self._heuristic_classification(combined_text, country, lang)
        if heuristic_type == "IRRELEVANT":
            return "IRRELEVANT", None

        # 2. Jeśli mamy klucz Gemini, tworzymy spersonalizowaną odpowiedź w lokalnym języku
        if self.gemini_client.is_configured():
            try:
                ai_result = self._gemini_analyze(title, content, country)
                if ai_result:
                    return ai_result
            except (GeminiAPIError, ValueError, KeyError) as e:
                print(f"[!] Błąd wywołania Gemini API ({e}). Używam silnika regułowego.")

        # 3. Tryb regułowy z szablonami dopasowanymi do języka wpisu i kraju
        reply_lang = self._detect_reply_language(combined_text, lang)
        draft = self._generate_heuristic_draft(heuristic_type, country, reply_lang)
        return heuristic_type, draft

    def _detect_reply_language(self, text: str, default_lang: str) -> str:
        if default_lang == "ja":
            return "ja" if JAPANESE_CHAR_RE.search(text) else "en"
        if default_lang == "en" and FRENCH_HINT_RE.search(text):
            return "fr"
        if default_lang == "nl":
            return "en"
        return default_lang

    def _heuristic_classification(self, text: str, country: str, lang: str = "pt") -> str:
        """Klasyfikacja intencji na bazie wzorców dla PT, ES, EN, FR, NL i JA."""
        if lang == "pt":
            return self._match_pt(text)
        if lang == "es":
            return self._match_es(text)
        if lang == "ja":
            ja_hit = self._match_ja(text)
            if ja_hit != "IRRELEVANT":
                return ja_hit
            return self._match_en(text)
        if lang == "nl":
            nl_hit = self._match_nl(text)
            if nl_hit != "IRRELEVANT":
                return nl_hit
            return self._match_en(text)

        # English (+ French for Canada)
        en_hit = self._match_en(text)
        if en_hit != "IRRELEVANT":
            return en_hit
        if country.upper() == "CA":
            return self._match_fr(text)
        return "IRRELEVANT"

    @staticmethod
    def _match_pt(text: str) -> str:
        service_patterns = [
            r"(preciso|procuro) (de )?(um |uma )?(bom |boa )?(encanador|eletricista|diarista|faxineira|pedreiro|pintor|marceneiro|chaveiro|jardineiro|técnico|tecnico|montador|profissional|marido de aluguel)",
            r"(alguém|alguem) (indica|recomenda|conhece|tem contato de?) (um |uma )?(bom |boa )?(encanador|eletricista|diarista|faxineira|pedreiro|pintor|marceneiro|chaveiro|técnico|tecnico|montador|profissional|marido de aluguel|limpeza)",
            r"indica[cç][aã]o de (um |uma )?(encanador|eletricista|diarista|pedreiro|pintor|profissional|faxineira|técnico|tecnico|marceneiro|chaveiro|reforma)",
            r"or[cç]amento para (reforma|pintura|obra|servi[cç]o|reparo|instala[cç][aã]o|mudan[cç]a)",
            r"contratar (servi[cç]o|pessoa|alguém|alguem|profissional|diarista|pedreiro|eletricista|encanador)",
            r"onde encontro (um |uma )?(profissional|pessoa que fa[cç]a|técnico|tecnico|diarista|pedreiro|eletricista|encanador)",
        ]
        work_patterns = [
            r"como conseguir clientes",
            r"onde divulgar (meu trabalho|meus servi[cç]os)",
            r"trabalho aut[oô]nomo",
            r"(procurando|precisando de|buscando) (tramp[oa]|bico|renda extra|trabalho|emprego|servi[cç]o|freela)",
            r"preciso de ajuda para encontrar (emprego|trabalho|trampo|servi[cç]o)",
            r"sou (eletricista|encanador|pintor|pedreiro|marceneiro|técnico|tecnico|aut[oô]nomo|diarista).{0,60}(cliente|servi[cç]o|trabalho|trampo|divulgar|renda)",
            r"fa[cç]o servi[cç]os de (el[eé]trica|hidr[aá]ulica|pintura|reforma|manuten[cç][aã]o|limpeza|marcenaria)",
            r"plataforma para (aut[oô]nomos|freelancer|prestar servi[cç]os)",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    @staticmethod
    def _match_es(text: str) -> str:
        # Obejmuje ES-MX + całą Amerykę Południową (AR, CO, CL, PE, EC, VE, UY, PY, BO)
        service_patterns = [
            r"(busco|necesito) (un |una )?(buen |buena )?(plomero|gasfitero|gasfiter|gasista|electricista|albañil|maestro|pintor|técnico|tecnico|carpintero|cerrajero|herrero|jardinero|mec[aá]nico)",
            r"(recomienden|recomiendan|alguien recomienda|conocen a|alg[uú]n contacto de) (un |una )?(buen |buena )?(plomero|gasfitero|gasfiter|gasista|electricista|albañil|pintor|carpintero|cerrajero|técnico|tecnico|señora de limpieza|mantenimiento)",
            r"(cotizaci[oó]n|presupuesto) para (remodelaci[oó]n|trabajo|reparaci[oó]n|pintura|plomer[ií]a|electricidad|obra)",
            r"alguien que haga trabajos de",
            r"necesito contratar (a alguien|un servicio)",
            r"busco (señora|persona|alguien) (de|para) limpieza",
            r"(recomienden|busco) servicio de (limpieza|mudanza|reparaci[oó]n|mantenimiento|fumigaci[oó]n|aire acondicionado)",
        ]
        work_patterns = [
            r"(busco|necesito|me urge) (chamba|laburo|pega|camello|trabajo|empleo|jale)",
            r"hago trabajos de (albañiler[ií]a|plomer[ií]a|gasfiter[ií]a|electricidad|pintura|carpinter[ií]a|mantenimiento|reparaci[oó]n)",
            r"ofrezco (mis )?servicios",
            r"d[oó]nde (conseguir clientes|anunciar mi trabajo|ofrecer mis servicios)",
            r"trabajador independiente",
            r"c[oó]mo conseguir (m[aá]s )?(clientes|chamba|laburo|pega)",
            r"ingreso(s)? extra",
            r"sin (chamba|laburo|pega|trabajo|empleo).{0,40}(ayuda|consejo|d[oó]nde|busco)",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    @staticmethod
    def _match_en(text: str) -> str:
        # USA, Kanada, Singapur (aircon servicing!), Gujana, anglojęzyczni w Japonii
        service_patterns = [
            r"(need|looking for|hire|hiring|recommend|recommendations for) (a |an )?(good |reliable |affordable )?(plumber|electrician|handyman|cleaner|house cleaner|painter|carpenter|locksmith|contractor|roofer|mover|aircon (servicing|technician|repair)|appliance repair)",
            r"(any|anyone) recommend (a |an )?(plumber|electrician|handyman|cleaner|painter|contractor|aircon)",
            r"(quote|estimate) for (plumbing|electrical|painting|renovation|remodel|repair|cleaning|moving|handyman)",
            r"looking to hire (a |someone for )?(cleaning|plumbing|electrical|painting|handyman|repair)",
        ]
        work_patterns = [
            r"(how to|where to|best app to) (get|find) (more )?(clients|customers|leads|handyman jobs|cleaning jobs|plumbing jobs)",
            r"(starting|started) (a |my )?(handyman|cleaning|plumbing|electrical|painting|lawn care|pressure washing) business",
            r"(looking for|need) (side work|extra income|handyman work|freelance work|odd jobs|gig work)",
            r"(i am|i'm) a (plumber|electrician|handyman|cleaner|painter|carpenter).{0,60}(clients|customers|jobs|work|leads)",
            r"offering (handyman|plumbing|electrical|cleaning|painting|moving) services",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    @staticmethod
    def _match_fr(text: str) -> str:
        service_patterns = [
            r"(besoin d'un|cherche un|recommande(z|r)? un) (bon )?(plombier|[eé]lectricien|peintre|menuisier|homme [aà] tout faire|femme de m[eé]nage|entrepreneur)",
            r"(devis|soumission) pour (r[eé]novation|plomberie|[eé]lectricit[eé]|peinture|m[eé]nage)",
        ]
        work_patterns = [
            r"(cherche du travail|besoin de travail|trouver des clients|travailleur autonome|offrir mes services)",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    @staticmethod
    def _match_nl(text: str) -> str:
        service_patterns = [
            r"(zoek|gezocht|nodig) (een )?(loodgieter|elektricien|klusjesman|schilder|schoonmaker|aannemer|timmerman)",
        ]
        work_patterns = [
            r"(werk gezocht|klanten vinden|zzp|zelfstandige|bijverdienen)",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    @staticmethod
    def _match_ja(text: str) -> str:
        service_patterns = [
            r"(水道修理|電気工事|ハウスクリーニング|エアコン掃除|エアコン修理|リフォーム|便利屋|鍵交換|塗装|引っ越し).{0,20}(おすすめ|探し|依頼|見積もり|業者|お願い)",
            r"(おすすめ|安い|信頼できる).{0,15}(水道修理|電気工事|ハウスクリーニング|便利屋|リフォーム業者|修理業者)",
        ]
        work_patterns = [
            r"(仕事探し|案件獲得|集客方法|副業|フリーランス|個人事業主).{0,20}(探し|方法|アプリ|おすすめ|困っ|増やし)",
            r"(便利屋|清掃|電気工事|水道|修理).{0,15}(独立|開業|集客|仕事)",
        ]
        for p in service_patterns:
            if re.search(p, text):
                return "SERVICE_SEEKER"
        for p in work_patterns:
            if re.search(p, text):
                return "WORK_SEEKER"
        return "IRRELEVANT"

    def _generate_heuristic_draft(self, lead_type: str, country: str, lang: str) -> str:
        """Generuje naturalną odpowiedź dopasowaną do kraju i języka wraz z linkiem do Google Play."""
        if lang == "pt":
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"Olá! Se ainda estiver procurando, dá uma olhada no {APP_NAME} "
                    f"(Google Play: {GOOGLE_PLAY_URL} | Site: {APP_URL}). "
                    f"É {APP_VALUE_PROPOSITION_BR_CLIENT}. "
                    "Dá para solicitar orçamentos sem compromisso e ver avaliações antes de fechar!"
                )
            return (
                f"Fala parceiro! Para divulgar seu serviço além do boca a boca, vale dar uma olhada no {APP_NAME} "
                f"(Google Play: {GOOGLE_PLAY_URL} | Site: {APP_URL}). "
                f"É {APP_VALUE_PROPOSITION_BR_WORKER}. Boa sorte na captação!"
            )

        if lang == "es":
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"¡Hola! Si todavía estás buscando, te recomiendo probar {APP_NAME} "
                    f"(Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}). "
                    f"Es {APP_VALUE_PROPOSITION_MX_CLIENT}. "
                    "Puedes pedir cotizaciones gratis y comparar opiniones antes de contratar."
                )
            return (
                f"¡Qué tal! Para conseguir más clientes en tu zona, vale la pena registrarte en {APP_NAME} "
                f"(Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}). "
                f"Es {APP_VALUE_PROPOSITION_MX_WORKER}. ¡Mucho éxito!"
            )

        if lang == "fr":
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"Bonjour ! Si vous cherchez toujours un professionnel, essayez {APP_NAME} "
                    f"(Google Play : {GOOGLE_PLAY_URL} | Web : {APP_URL}). "
                    f"C'est {APP_VALUE_PROPOSITION_FR_CLIENT}."
                )
            return (
                f"Bonjour ! Pour trouver plus de clients locaux, vous pouvez vous inscrire sur {APP_NAME} "
                f"(Google Play : {GOOGLE_PLAY_URL} | Web : {APP_URL}). "
                f"C'est {APP_VALUE_PROPOSITION_FR_WORKER}."
            )

        if lang == "ja":
            if lead_type == "SERVICE_SEEKER":
                return (
                    f"こんにちは！まだ業者をお探しでしたら、{APP_NAME} をチェックしてみてください"
                    f"（Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}）。"
                    f"{APP_VALUE_PROPOSITION_JA_CLIENT}です。"
                )
            return (
                f"こんにちは！地元で新しい案件やお客様を見つけたい場合は、{APP_NAME} への登録もおすすめです"
                f"（Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}）。"
                f"{APP_VALUE_PROPOSITION_JA_WORKER}です。"
            )

        # Default: English (US, CA, SG, GY, SR, EN posts in JP)
        if lead_type == "SERVICE_SEEKER":
            return (
                f"Hi! If you're still looking for help, check out {APP_NAME} "
                f"(Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}). "
                f"It's {APP_VALUE_PROPOSITION_EN_CLIENT}."
            )
        return (
            f"Hey! If you're looking to get more local jobs without relying only on word of mouth, "
            f"take a look at {APP_NAME} (Google Play: {GOOGLE_PLAY_URL} | Web: {APP_URL}). "
            f"It's {APP_VALUE_PROPOSITION_EN_WORKER}."
        )

    def _gemini_analyze(self, title: str, content: str, country: str) -> Optional[Tuple[str, Optional[str]]]:
        """Używa Google Gemini Interactions API do analizy i odpowiedzi w języku danego kraju."""
        info = get_country_info(country)
        country_name = info["name"]
        lang_label = info["lang_label"]

        system_instruction = (
            f"You are a helpful community specialist for the local services app '{APP_NAME}' "
            f"(Website: {APP_URL}, Google Play: {GOOGLE_PLAY_URL}) operating in {country_name}. "
            f"{APP_NAME} connects people who need local services (plumbing, electrical, cleaning, painting, "
            "repairs, handyman) with rated local workers. Classify author intent as 'SERVICE_SEEKER', "
            "'WORK_SEEKER', or 'IRRELEVANT'. If relevant, write a natural, helpful, non-spammy 2-3 sentence "
            f"reply matching the post's language ({lang_label}) and include the Google Play link ({GOOGLE_PLAY_URL})."
        )

        user_prompt = f"COUNTRY: {country_name} ({country})\nTITLE: {title}\nCONTENT: {content}"

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
        if GOOGLE_PLAY_URL not in draft_reply:
            draft_reply = f"{draft_reply} (Google Play: {GOOGLE_PLAY_URL})".strip()
        return intent, draft_reply
