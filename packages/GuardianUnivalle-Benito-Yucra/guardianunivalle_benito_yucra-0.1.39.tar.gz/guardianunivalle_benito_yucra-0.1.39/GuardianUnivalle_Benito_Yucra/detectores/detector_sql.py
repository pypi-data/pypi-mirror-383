# sql_defense.py
# sql_defense.py - versión robusta y precisa
import json
import logging
import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger("sqlidefense")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

# Patrones organizados por nivel de severidad
SQL_PATTERNS = [
    # Ataques fuertes (bloqueo inmediato)
    (re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I), "Uso de UNION SELECT", 0.7),
    (re.compile(r"\bor\b\s+'?\d+'?\s*=\s*'?\d+'?", re.I), "Tautología OR 1=1", 0.6),
    (re.compile(r"\bselect\b.+\bfrom\b", re.I), "Consulta SQL SELECT-FROM", 0.5),
    (re.compile(r"(--|#|/\*|\*/)", re.I), "Comentario SQL sospechoso", 0.4),
    (re.compile(r"\b(drop|truncate|delete|insert|update)\b", re.I), "Manipulación SQL", 0.5),
    (re.compile(r"exec\s*\(", re.I), "Ejecución de procedimiento almacenado", 0.6),
]

# Campos que deben ser analizados con cuidado o ignorados
IGNORED_FIELDS = ["password", "csrfmiddlewaretoken", "token", "auth"]

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")

def extract_body(request):
    try:
        if "application/json" in request.META.get("CONTENT_TYPE", ""):
            data = json.loads(request.body.decode("utf-8") or "{}")
        else:
            data = request.POST.dict() or {}
    except Exception:
        data = {}
    return data

def detect_sql_injection(value: str):
    score_total = 0.0
    descripciones = []
    matches = []

    for pattern, desc, weight in SQL_PATTERNS:
        if pattern.search(value):
            score_total += weight
            descripciones.append(desc)
            matches.append(pattern.pattern)

    return score_total, descripciones, matches

class SQLIDefenseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        client_ip = get_client_ip(request)
        trusted_ips = getattr(settings, "SQLI_DEFENSE_TRUSTED_IPS", [])

        if client_ip in trusted_ips:
            return None

        data = extract_body(request)
        score = 0.0
        all_desc = []
        all_matches = []

        for key, value in data.items():
            if not isinstance(value, str):
                continue
            if key.lower() in IGNORED_FIELDS:
                continue  # No analizar contraseñas ni tokens

            s, desc, matches = detect_sql_injection(value)
            score += s
            all_desc.extend(desc)
            all_matches.extend(matches)

        if score == 0:
            return None  # nada sospechoso

        logger.warning(
            f"[SQLiDetect] IP={client_ip} Score={score:.2f} Desc={all_desc} Campos={list(data.keys())}"
        )

        # Guardamos info en request
        request.sql_attack_info = {
            "ip": client_ip,
            "tipos": ["SQLi"],
            "descripcion": all_desc,
            "score": round(score, 2),
        }

        # Bloqueamos solo si supera umbral de riesgo
        if score >= 0.7:
            from django.http import JsonResponse
            return JsonResponse(
                {"error": "Posible ataque de inyección SQL detectado. Solicitud bloqueada."},
                status=403
            )


# =====================================================
# ===              INFORMACIÓN EXTRA                ===
# =====================================================
"""
Algoritmos relacionados:
    - Se recomienda almacenar logs SQLi cifrados (AES-GCM) 
      para proteger evidencia de intentos maliciosos.

Cálculo de puntaje de amenaza:
    S_sqli = w_sqli * detecciones_sqli
    Ejemplo: S_sqli = 0.4 * 3 = 1.2

Integración:
    Este middleware puede combinarse con:
        - CSRFDefenseMiddleware
        - XSSDefenseMiddleware
    para calcular un score total de amenaza y decidir bloqueo.
"""
