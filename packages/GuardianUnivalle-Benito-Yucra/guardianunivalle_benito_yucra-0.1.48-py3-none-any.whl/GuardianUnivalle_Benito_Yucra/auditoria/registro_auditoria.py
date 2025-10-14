# E:\EcuacionPotosi\GuardianUnivalle-Benito-Yucra\GuardianUnivalle_Benito_Yucra\auditoria\registro_auditoria.py

import os
import datetime
import json
import platform
import requests
from django.utils.timezone import now
from user_agents import parse

LOG_FILE = "auditoria_guardian.log"

# =====================================================
# === FUNCIONES DE CAPTURA Y ANÁLISIS DE CLIENTE ===
# =====================================================

def obtener_datos_maquina(request) -> dict:
    """Obtiene información detallada del cliente desde la petición"""
    try:
        # --- IP real ---
        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR")
            or request.META.get("REMOTE_ADDR")
            or "0.0.0.0"
        )
        ip = ip.split(",")[0].strip()

        # --- User Agent ---
        user_agent_str = request.META.get("HTTP_USER_AGENT", "Desconocido")
        user_agent = parse(user_agent_str)
        navegador = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        sistema = f"{user_agent.os.family} {user_agent.os.version_string}"

        # --- Geolocalización (ipinfo.io gratuita) ---
        geo_data = {}
        try:
            r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
            if r.status_code == 200:
                geo_data = r.json()
        except Exception:
            pass

        pais = geo_data.get("country", "Desconocido")
        ciudad = geo_data.get("city", "Desconocida")
        isp = geo_data.get("org", "Desconocido")

        # --- Usuario autenticado ---
        usuario = "Anónimo"
        if hasattr(request, "user") and request.user.is_authenticated:
            usuario = getattr(request.user, "username", "Desconocido")

        # --- Construir estructura ---
        datos = {
            "fecha": now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": ip,
            "pais": pais,
            "ciudad": ciudad,
            "isp": isp,
            "usuario": usuario,
            "user_agent": user_agent_str,
            "navegador": navegador,
            "sistema_operativo": sistema,
            "url": request.path,
            "metodo": request.method,
        }

        return datos
    except Exception as e:
        return {"error": str(e)}


def analizar_comportamiento_cliente(datos_cliente: dict) -> tuple[str, str]:
    """
    Aplica reglas básicas de detección:
      - IP sospechosa o repetitiva
      - Agente extraño o vacío
      - Peticiones sospechosas (ej: /admin, /etc/passwd)
    Devuelve: (nivel_riesgo, descripcion)
    """
    descripcion = []
    riesgo = "BAJO"

    ip = datos_cliente.get("ip", "")
    user_agent = datos_cliente.get("user_agent", "").lower()
    ruta = datos_cliente.get("url", "")

    # === Reglas simples ===
    if not user_agent or "curl" in user_agent or "python" in user_agent:
        descripcion.append("Agente de usuario anómalo (posible bot o script).")
        riesgo = "MEDIO"

    if "admin" in ruta or "etc/passwd" in ruta or "../" in ruta:
        descripcion.append("Ruta sospechosa accedida.")
        riesgo = "ALTO"

    if "Desconocida" in ip or ip.startswith("192.168.") is False:
        descripcion.append(f"IP externa detectada: {ip}")
        riesgo = "MEDIO"

    if not datos_cliente.get("url"):
        descripcion.append("Petición sin parámetros ni cabeceras útiles.")
        riesgo = "BAJO"

    if not descripcion:
        descripcion.append("Acceso normal detectado.")

    return riesgo, " | ".join(descripcion)


# =====================================================
# === FUNCIÓN PRINCIPAL DE REGISTRO ===
# =====================================================
def registrar_evento(request, tipo: str = "ACCESO", extra: dict | None = None):
    """
    Registra un evento de auditoría detallado del cliente.
    Incluye login exitoso, acceso normal y detección de ataques.
    """
    try:
        datos_cliente = obtener_datos_maquina(request)
        severidad, descripcion = analizar_comportamiento_cliente(datos_cliente)

        evento = {
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo,
            "descripcion": descripcion,
            "severidad": severidad,
            "cliente": datos_cliente,
            "extra": extra or {},
        }

        # Crear carpeta solo si hay directorio en la ruta
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Registrar en archivo
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")

        # Log en consola para depuración local
        print(f"[AUDITORÍA] Evento registrado: {evento['descripcion']} (nivel {severidad})")

    except Exception as e:
        print(f"[AUDITORÍA] Error al registrar evento: {e}")


# =====================================================
# === CONSULTA DE REGISTROS (opcional) ===
# =====================================================
def generar_reporte() -> str:
    """Devuelve todo el contenido del archivo de auditoría."""
    if not os.path.exists(LOG_FILE):
        return "No hay registros aún."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()
