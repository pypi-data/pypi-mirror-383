import os
import datetime
import json
import platform
from django.utils import timezone

LOG_FILE = "auditoria_guardian.log"

# =====================================================
# === FUNCIONES DE CAPTURA Y ANÁLISIS DE CLIENTE ===
# =====================================================
def capturar_datos_cliente(request) -> dict:
    """Extrae información útil del cliente que accede al sistema."""
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "Desconocida")

    user_agent = request.META.get("HTTP_USER_AGENT", "Desconocido")
    metodo = request.method
    ruta = request.path
    parametros = request.GET.dict() if metodo == "GET" else request.POST.dict()
    so_servidor = platform.system()

    return {
        "ip_cliente": ip,
        "navegador": user_agent,
        "metodo": metodo,
        "ruta": ruta,
        "parametros": parametros,
        "servidor_os": so_servidor,
        "hora_servidor": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


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

    ip = datos_cliente.get("ip_cliente", "")
    user_agent = datos_cliente.get("navegador", "").lower()
    ruta = datos_cliente.get("ruta", "")

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

    # Comportamiento sin parámetros ni cabeceras
    if not datos_cliente.get("parametros"):
        descripcion.append("Petición sin parámetros ni cabeceras útiles.")
        riesgo = "BAJO"

    if not descripcion:
        descripcion.append("Acceso normal detectado.")

    return riesgo, " | ".join(descripcion)


# =====================================================
# === FUNCIÓN PRINCIPAL DE REGISTRO ===
# =====================================================
def registrar_evento(request, tipo: str = "ACCESO", extra: dict | None = None):
    """Registra un evento de auditoría detallado del cliente."""
    try:
        datos_cliente = capturar_datos_cliente(request)
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

        # (Opcional) Log en consola
        print(f"[AUDITORÍA] Evento registrado: {evento['descripcion']} (nivel {severidad})")

    except Exception as e:
        print(f"[Auditoría] Error al registrar evento: {e}")


# =====================================================
# === CONSULTA DE REGISTROS ===
# =====================================================
def generar_reporte() -> str:
    """Devuelve todo el contenido del archivo de auditoría."""
    if not os.path.exists(LOG_FILE):
        return "No hay registros aún."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return f.read()
