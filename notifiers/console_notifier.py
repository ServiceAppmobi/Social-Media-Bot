import textwrap
from config import get_country_info

class ConsoleNotifier:
    @staticmethod
    def print_lead(lead: dict):
        lead_type = lead.get("lead_type")
        country = lead.get("country", "BR")
        cinfo = get_country_info(country)
        country_flag = f"{cinfo['flag']} [{cinfo['name'].upper()}]"

        if lead_type == "SERVICE_SEEKER":
            type_badge = "\033[1;34m[KLIENT SZUKA FACHOWCA]\033[0m"
        elif lead_type == "WORK_SEEKER":
            type_badge = "\033[1;32m[FACHOWIEC SZUKA PRACY/ZLECEŃ]\033[0m"
        else:
            type_badge = "[DYSKUSJA]"

        platform = lead.get("platform", "web")
        plat_icon = "🟢 WhatsApp" if platform == "whatsapp" else "🐘 " + lead.get("source_channel", "") if platform == "mastodon" else "🌐 " + lead.get("source_channel", "")

        print("\n" + "="*80)
        print(f"{country_flag} {type_badge}  | Źródło: \033[1m{plat_icon}\033[0m  | Autor: {lead.get('author')}")
        print(f"📌 Tytuł: \033[1m{lead.get('title')}\033[0m")
        print(f"🔗 Link:  \033[4m{lead.get('url')}\033[0m")
        
        snippet = lead.get("content_snippet", "")
        if snippet:
            short_snippet = textwrap.shorten(snippet, width=180, placeholder="...")
            print(f"📄 Treść: \"{short_snippet}\"")
        
        lang_note = cinfo["lang_label"]
        print(f"\n💬 Proponowana naturalna odpowiedź ({lang_note}):")
        print("\033[36m" + textwrap.fill(lead.get('ai_draft', ''), width=75) + "\033[0m")
        print("="*80)
