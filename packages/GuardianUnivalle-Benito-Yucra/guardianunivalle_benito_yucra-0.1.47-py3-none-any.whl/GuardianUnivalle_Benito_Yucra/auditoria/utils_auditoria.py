import requests
from django.utils.timezone import now
from user_agents import parse

def obtener_datos_maquina(request):
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

        # --- Geolocalización (usando ipinfo.io gratuita) ---
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
        if request.user and request.user.is_authenticated:
            usuario = request.user.username

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
