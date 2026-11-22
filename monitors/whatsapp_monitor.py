import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any, Callable
from config import WHATSAPP_WEBHOOK_PORT

class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    """
    Odbiera wiadomości przesyłane z bramek WhatsApp (np. Evolution API, Z-API, Baileys, WPPConnect)
    podłączonych do grup w Brazylii i Meksyku.
    """
    message_callback: Callable = None

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode("utf-8"))
            # Ekstrakcja danych niezależnie od formatu bramki (Evolution / Baileys / standard webhook)
            extracted = self._extract_message(payload)
            if extracted and self.message_callback:
                self.message_callback(extracted)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "received"}')
        except Exception as e:
            print(f"[!] Błąd przetwarzania webhooka WhatsApp: {e}")
            self.send_response(400)
            self.end_headers()

    def _extract_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ujednolica format wiadomości przychodzącej z grupy WhatsApp."""
        # Obsługa różnych formatów (Evolution API / WPPConnect / Generic)
        body = (
            data.get("message", {}).get("conversation") or 
            data.get("body") or 
            data.get("text") or 
            data.get("content", "")
        )
        group_name = data.get("groupName") or data.get("chatName") or data.get("from", "Grupo WhatsApp")
        sender = data.get("pushName") or data.get("senderName") or "Membro do Grupo"
        msg_id = data.get("id") or f"wpp_{int(time.time()*1000)}"

        # Detekcja kraju po numerze telefonu nadawcy (+55 Brazylia, +52 Meksyk)
        sender_phone = str(data.get("sender", ""))
        country = "MX" if sender_phone.startswith("52") or "mexico" in group_name.lower() or "cdmx" in group_name.lower() else "BR"

        if not body:
            return None

        return {
            "id": f"whatsapp_{msg_id}",
            "platform": "whatsapp",
            "country": country,
            "source_channel": f"🟢 WhatsApp: {group_name}",
            "title": f"Wiadomość z grupy: {group_name}",
            "content": body,
            "url": f"https://wa.me/{sender_phone}" if sender_phone else "https://web.whatsapp.com",
            "author": sender,
            "created_utc": time.time()
        }

class WhatsAppMonitor:
    def __init__(self, port: int = WHATSAPP_WEBHOOK_PORT):
        self.port = port

    def start_webhook_listener(self, on_message: Callable):
        """Uruchamia lokalny serwer webhooka nasłuchujący wiadomości z grup WhatsApp."""
        WhatsAppWebhookHandler.message_callback = on_message
        server_address = ("", self.port)
        httpd = HTTPServer(server_address, WhatsAppWebhookHandler)
        print(f"[🟢] Nasłuchiwanie webhooka WhatsApp aktywne na porcie {self.port}...")
        print("     Podłącz swoją bramkę WhatsApp (np. Evolution API) pod: http://localhost:8088/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Zatrzymano nasłuchiwanie WhatsApp.")
            httpd.server_close()

    @staticmethod
    def get_mock_group_messages() -> List[Dict[str, Any]]:
        """Przykładowe rzeczywiste wiadomości z grup WhatsApp z Brazylii i Meksyku."""
        return [
            # Brazylia - Grupa WhatsApp w São Paulo
            {
                "id": "mock_wpp_br_001",
                "platform": "whatsapp",
                "country": "BR",
                "source_channel": "🟢 WhatsApp: [SP] Vagas e Serviços Zona Leste",
                "title": "Zapytanie w grupie: [SP] Vagas e Serviços Zona Leste",
                "content": "Boa tarde vizinhos do grupo! Alguém tem indicação de diarista de confiança para fazer uma faxina pesada na sexta-feira em Itaquera? Por favor me chamem no privado.",
                "url": "https://chat.whatsapp.com/mock-grupo-sp",
                "author": "Juliana Santos (+55 11 98765-4321)",
                "created_utc": time.time() - 1200
            },
            # Meksyk - Grupa WhatsApp w CDMX
            {
                "id": "mock_wpp_mx_001",
                "platform": "whatsapp",
                "country": "MX",
                "source_channel": "🟢 WhatsApp: Bolsa de Trabajo y Oficios CDMX",
                "title": "Zapytanie w grupie: Bolsa de Trabajo y Oficios CDMX",
                "content": "Qué tal grupo buenas tardes. Busco plomero urgente para una fuga en un departamento en Coyoacán. Que pueda venir hoy mismo o mañana temprano. Manden mensaje con su cotización aproximada.",
                "url": "https://chat.whatsapp.com/mock-grupo-cdmx",
                "author": "Eduardo Ramos (+52 55 1234-5678)",
                "created_utc": time.time() - 2400
            },
            # Meksyk - Grupa WhatsApp w Monterrey (Fachowiec szukający zleceń)
            {
                "id": "mock_wpp_mx_002",
                "platform": "whatsapp",
                "country": "MX",
                "source_channel": "🟢 WhatsApp: Chambas y Oficios Monterrey / San Pedro",
                "title": "Oferta w grupie: Chambas y Oficios Monterrey",
                "content": "Buenas tardes amigos. Soy electricista certificado, hago instalaciones residenciales, cambio de centros de carga y cableado. Me urge chamba para esta semana, precios accesibles y garantía por escrito.",
                "url": "https://chat.whatsapp.com/mock-grupo-mty",
                "author": "Roberto Electricista (+52 81 9876-5432)",
                "created_utc": time.time() - 3600
            }
        ]
