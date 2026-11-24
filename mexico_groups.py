# ServiceApp - Grupy Meksyk na Instagramie
# Tak samo jak instagram_groups.py dla Brazylii, tylko po hiszpansku

MEXICO_GROUPS = [
    {
        "name": "ServiceApp CDMX / Servicios",
        "city": "CDMX",
        "language": "es",
        "topics": ["buscar trabajo", "ofrecer servicios", "intercambio de servicios"],
        "audience": "prestadores y clientes",
    },
    {
        "name": "ServiceApp Guadalajara / Servicios",
        "city": "Guadalajara",
        "language": "es",
        "topics": ["buscar trabajo", "ofrecer servicios", "intercambio de servicios"],
        "audience": "prestadores y clientes",
    },
    {
        "name": "ServiceApp Monterrey / Servicios",
        "city": "Monterrey",
        "language": "es",
        "topics": ["buscar trabajo", "ofrecer servicios", "intercambio de servicios"],
        "audience": "prestadores y clientes",
    },
]

# Rotacja - 1 grupa dziennie, na zmiane
# Poniedzialek - CDMX, Wtorek - Guadalajara, Sroda - Monterrey, Czwartek - CDMX, itd.
# 1 post dziennie na Meksyk, 1 post dziennie na Brazylie, nie wiecej

def get_today_group(day_number):
    # day_number: 0 = Poniedzialek, 6 = Niedziela
    return MEXICO_GROUPS[day_number % len(MEXICO_GROUPS)]

# Gotowe nazwy do kopiowania
GROUP_NAMES_MX = [
    "ServiceApp CDMX / Servicios",
    "ServiceApp Guadalajara / Servicios",
    "ServiceApp Monterrey / Servicios",
]
