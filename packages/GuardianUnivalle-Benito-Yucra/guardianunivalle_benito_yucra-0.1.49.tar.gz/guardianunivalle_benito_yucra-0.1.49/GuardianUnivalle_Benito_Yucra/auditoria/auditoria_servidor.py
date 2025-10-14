import logging
import json
import platform
import socket
import uuid
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("auditoria_servidor")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


def obtener_datos_maquina(request):
    """
    Retorna un diccionario con información del cliente y del servidor.
    No accede a ningún modelo Django.
    """
    datos = {}
    try:
        # Datos del cliente
        datos["ip"] = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0] or request.META.get("REMOTE_ADDR", "")
        datos["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
        datos["navegador"] = datos["user_agent"].split("/")[0] if "/" in datos["user_agent"] else datos["user_agent"]
        datos["sistema_operativo"] = platform.system()
        datos["url"] = request.build_absolute_uri()
        datos["fecha"] = datetime.now().isoformat()

        # Datos del servidor
        datos["servidor_nombre"] = socket.gethostname()
        datos["servidor_ip"] = socket.gethostbyname(socket.gethostname())
        datos["servidor_uuid"] = str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Error obteniendo datos de máquina: {e}")
    return datos


def analizar_comportamiento_cliente(datos):
    """
    Analiza los datos del cliente y retorna una evaluación general:
    (nivel_severidad, descripcion)
    """
    if not datos:
        return "BAJA", "Sin datos del cliente"

    ip = datos.get("ip", "")
    navegador = datos.get("navegador", "")
    descripcion = f"Actividad detectada desde IP {ip} con navegador {navegador}"

    if "bot" in navegador.lower():
        return "MEDIA", descripcion + " (posible bot)"
    return "BAJA", descripcion


def registrar_evento(tipo, descripcion, severidad="BAJA", extra=None):
    """
    Registra un evento en los logs (la BD será manejada por el backend Django).
    """
    try:
        registro = {
            "tipo": tipo,
            "descripcion": descripcion,
            "severidad": severidad,
            "fecha": datetime.now().isoformat(),
            "extra": extra or {},
        }
        logger.info("[AUDITORIA] %s", json.dumps(registro, ensure_ascii=False))
        return registro
    except Exception as e:
        logger.error(f"Error registrando evento: {e}")
        return None


class AuditoriaServidorMiddleware(MiddlewareMixin):
    """
    Middleware que integra toda la información generada por los detectores (SQLi, XSS, etc.)
    y la deja lista en request.guardian_auditoria para que el backend (Django)
    la guarde en la base de datos.
    """

    def process_request(self, request):
        try:
            datos_cliente = obtener_datos_maquina(request)
            severidad, descripcion = analizar_comportamiento_cliente(datos_cliente)

            # Base del registro
            registro_base = {
                "datos_cliente": datos_cliente,
                "descripcion": descripcion,
                "severidad": severidad,
                "eventos_detectados": [],
            }

            # Integrar información de ataques detectada por otros middlewares
            if hasattr(request, "sql_attack_info"):
                registro_base["eventos_detectados"].append(request.sql_attack_info)

            if hasattr(request, "xss_attack_info"):
                registro_base["eventos_detectados"].append(request.xss_attack_info)

            if hasattr(request, "csrf_attack_info"):
                registro_base["eventos_detectados"].append(request.csrf_attack_info)

            if hasattr(request, "dos_attack_info"):
                registro_base["eventos_detectados"].append(request.dos_attack_info)

            # Si hubo algún evento sospechoso
            if registro_base["eventos_detectados"]:
                registrar_evento(
                    tipo="ATAQUE_DETECTADO",
                    descripcion="Se detectó comportamiento sospechoso en la solicitud",
                    severidad="ALTA",
                    extra=registro_base,
                )

            # Guardar la info para el backend (sin registrar aún en BD)
            request.guardian_auditoria = registro_base

        except Exception as e:
            logger.error(f"Error en AuditoriaServidorMiddleware: {e}")
        return None
