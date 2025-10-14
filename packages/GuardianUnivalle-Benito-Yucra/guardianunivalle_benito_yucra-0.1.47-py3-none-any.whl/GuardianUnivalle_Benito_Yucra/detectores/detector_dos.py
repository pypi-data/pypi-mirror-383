from __future__ import annotations
import time
import logging
import json
from collections import deque
from typing import Dict, List
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from ..mitigacion.limitador_peticion import limitar_peticion
from ..auditoria.registro_auditoria import registrar_evento

# =====================================================
# === CONFIGURACIÓN DEL LOGGER ===
# =====================================================
logger = logging.getLogger("dosdefense")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

# =====================================================
# === PARÁMETROS DE CONFIGURACIÓN BASE ===
# =====================================================
LIMITE_PETICIONES = getattr(settings, "DOS_LIMITE_PETICIONES", 100)  # por minuto
VENTANA_SEGUNDOS = getattr(settings, "DOS_VENTANA_SEGUNDOS", 60)
PESO_DOS = getattr(settings, "DOS_PESO", 0.6)
LIMITE_ENDPOINTS_DISTINTOS = getattr(settings, "DOS_LIMITE_ENDPOINTS", 50)
TRUSTED_IPS = getattr(settings, "DOS_TRUSTED_IPS", [])

# =====================================================
# === REGISTRO TEMPORAL EN MEMORIA ===
# =====================================================
# Estructura: { ip: deque([timestamps]), ... }
# deque es eficiente para ventanas deslizantes
REGISTRO_SOLICITUDES: Dict[str, deque] = {}
REGISTRO_ENDPOINTS: Dict[str, set] = {}

# =====================================================
# === FUNCIONES AUXILIARES ===
# =====================================================
def get_client_ip(request) -> str:
    """Obtiene la IP real del cliente (considera proxies)."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or "0.0.0.0"


def limpiar_registro_global():
    """Elimina IPs sin actividad reciente para evitar uso excesivo de memoria."""
    ahora = time.time()
    expiracion = VENTANA_SEGUNDOS * 2  # doble ventana
    inactivas = [
        ip for ip, tiempos in REGISTRO_SOLICITUDES.items()
        if tiempos and ahora - tiempos[-1] > expiracion
    ]
    for ip in inactivas:
        REGISTRO_SOLICITUDES.pop(ip, None)
        REGISTRO_ENDPOINTS.pop(ip, None)


def limpiar_registro(ip: str):
    """Limpia peticiones antiguas fuera de la ventana de tiempo."""
    ahora = time.time()
    if ip not in REGISTRO_SOLICITUDES:
        REGISTRO_SOLICITUDES[ip] = deque()
    tiempos = REGISTRO_SOLICITUDES[ip]
    while tiempos and ahora - tiempos[0] > VENTANA_SEGUNDOS:
        tiempos.popleft()


def calcular_nivel_amenaza_dos(tasa_peticion: int, limite: int = LIMITE_PETICIONES) -> float:
    """
    Calcula la puntuación de amenaza DoS.
    Fórmula: S_dos = w_dos * (tasa_peticion / limite)
    """
    proporcion = tasa_peticion / max(limite, 1)
    s_dos = PESO_DOS * min(proporcion, 2.0)
    return round(min(s_dos, 1.0), 3)


def detectar_dos(ip: str, tasa_peticion: int, limite: int = LIMITE_PETICIONES) -> bool:
    """Evalúa si la tasa de peticiones excede el umbral permitido."""
    if tasa_peticion > limite:
        registrar_evento(
            tipo="DoS",
            descripcion=f"Alta tasa de peticiones desde {ip}: {tasa_peticion} req/min (límite {limite})",
            severidad="ALTA",
        )
        limitar_peticion(usuario_id="anonimo")
        return True
    elif tasa_peticion > limite * 0.75:
        # Umbral de advertencia
        registrar_evento(
            tipo="DoS",
            descripcion=f"Posible saturación desde {ip}: {tasa_peticion} req/min",
            severidad="MEDIA",
        )
    return False


def analizar_headers(user_agent: str, referer: str) -> List[str]:
    """Detecta patrones de agentes o cabeceras sospechosas."""
    sospechas = []
    if not user_agent or len(user_agent) < 10:
        sospechas.append("User-Agent vacío o anómalo")
    if "curl" in user_agent.lower() or "python" in user_agent.lower():
        sospechas.append("User-Agent indica script o bot")
    if referer and any(palabra in referer.lower() for palabra in ["attack", "scan", "bot"]):
        sospechas.append("Referer sospechoso")
    return sospechas


# =====================================================
# === MIDDLEWARE PRINCIPAL DE DEFENSA DoS ===
# =====================================================
class DOSDefenseMiddleware(MiddlewareMixin):
    """
    Middleware de detección y registro de ataques DoS.
    """

    def process_request(self, request):
        limpiar_registro_global()

        client_ip = get_client_ip(request)
        if client_ip in TRUSTED_IPS:
            return None

        user_agent = request.META.get("HTTP_USER_AGENT", "Desconocido")
        referer = request.META.get("HTTP_REFERER", "")
        path = request.path

        # Registrar endpoint accedido
        REGISTRO_ENDPOINTS.setdefault(client_ip, set()).add(path)

        # Mantener ventana deslizante
        limpiar_registro(client_ip)
        REGISTRO_SOLICITUDES[client_ip].append(time.time())

        tasa = len(REGISTRO_SOLICITUDES[client_ip])
        nivel = calcular_nivel_amenaza_dos(tasa)
        es_dos = detectar_dos(client_ip, tasa)

        descripcion = []
        sospechas_headers = analizar_headers(user_agent, referer)
        if sospechas_headers:
            descripcion.extend(sospechas_headers)

        # Verificar exceso de endpoints distintos (indicativo de escaneo)
        if len(REGISTRO_ENDPOINTS[client_ip]) > LIMITE_ENDPOINTS_DISTINTOS:
            descripcion.append("Número anormal de endpoints distintos accedidos")

        if es_dos or descripcion:
            descripcion.insert(0, f"Tasa actual: {tasa} req/min (nivel {nivel:.2f})")
            descripcion.append(f"Ruta: {path}")

            logger.warning(
                "DoS detectado o sospechoso desde IP %s: %s ; nivel: %.2f",
                client_ip,
                descripcion,
                nivel,
            )

            request.dos_attack_info = {
                "ip": client_ip,
                "tipos": ["DoS"],
                "descripcion": descripcion,
                "payload": json.dumps(
                    {"user_agent": user_agent, "referer": referer, "path": path}
                ),
                "score": nivel,
            }

        return None


"""
Detector de ataques de tipo DoS (Denial of Service)
====================================================

Este módulo forma parte del sistema de detección de amenazas.
Detecta tasas de petición anómalas en base a límites configurables,
captura datos del atacante (IP, agente, cabeceras)
y registra los incidentes para su auditoría.

Componentes:
- DOSDefenseMiddleware: Middleware principal de detección.
- detectar_dos(): Evalúa si la tasa supera el umbral permitido.
- calcular_nivel_amenaza_dos(): Calcula la severidad proporcional.
- registrar_evento(): Registra los incidentes en auditoría.

Algoritmos relacionados:
    * Rate Limiting basado en ventana deslizante.
    * Cálculo de score: S_dos = w_dos * (tasa_peticion / limite)
"""


""" 
Algoritmos relacionados:
    *Rate Limiting, listas de bloqueo.
    *Opcional: cifrado de logs con ChaCha20-Poly1305.
Contribución a fórmula de amenaza S:
S_dos = w_dos * (tasa_peticion / limite)
S_dos = 0.6 * (150 / 100)
donde w_dos es peso asignado a DoS y tasa_peticion / limite es la proporción de la tasa actual sobre el límite.
"""
"""
Detector de ataques de tipo DoS (Denial of Service)
====================================================

Este módulo forma parte del sistema de detección de amenazas.
Detecta tasas de petición anómalas en base a límites configurables,
captura datos del atacante (IP, agente, cabeceras)
y registra los incidentes para su auditoría.

Componentes:
- DOSDefenseMiddleware: Middleware principal de detección.
- detectar_dos(): Evalúa si la tasa supera el umbral permitido.
- calcular_nivel_amenaza_dos(): Calcula la severidad proporcional.
- registrar_evento(): Registra los incidentes en auditoría.

Algoritmos relacionados:
    * Rate Limiting basado en ventana deslizante.
    * Cálculo de score: S_dos = w_dos * (tasa_peticion / limite)
"""
