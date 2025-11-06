import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import pdfplumber
import json
import shutil

# ================================
# 📦 Cargar configuración desde JSON
# ================================
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_rpa.json")

def cargar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ No se pudo cargar config_rpa.json: {e}")
        return None

config = cargar_config()
if not config:
    raise Exception("No se pudo leer la configuración. Verifique config_rpa.json")

# Rutas reales del entorno
ruta_pdfs = config["rutas"]["pdfs"]
ruta_salida = config["rutas"]["salida_json"]
ruta_procesados = config["rutas"]["procesados"]
ruta_log = config["rutas"]["log"]
intervalo = config["parametros"]["intervalo_segundos"]
extensiones = [ext.lower() for ext in config["parametros"]["extensiones_permitidas"]]

# Crear carpetas si no existen
for carpeta in [ruta_pdfs, ruta_salida, ruta_procesados]:
    os.makedirs(carpeta, exist_ok=True)

# ================================
# 🧩 Función principal: Procesar PDFs
# ================================
def procesar_pdfs():
    for archivo in os.listdir(ruta_pdfs):
        if any(archivo.lower().endswith(ext) for ext in extensiones):
            ruta_completa = os.path.join(ruta_pdfs, archivo)
            print(f"Procesando: {archivo}")

            try:
                texto = ""
                with pdfplumber.open(ruta_completa) as pdf:
                    for pagina in pdf.pages:
                        extraido = pagina.extract_text()
                        if extraido:
                            texto += extraido + "\n"

                # Generar JSON
                data = {
                    "nombre_archivo": archivo,
                    "contenido_completo": texto.strip()
                }

                nombre_salida = os.path.splitext(archivo)[0] + ".json"
                ruta_json = os.path.join(ruta_salida, nombre_salida)
                with open(ruta_json, "w", encoding=config["parametros"]["codificacion"]) as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                # Mover PDF a carpeta de procesados
                shutil.move(ruta_completa, os.path.join(ruta_procesados, archivo))

                # Log
                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Procesado: {archivo}\n")

            except Exception as e:
                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error procesando {archivo}: {str(e)}\n")

# ================================
# 🧠 Clase del servicio de Windows
# ================================
class RPAService(win32serviceutil.ServiceFramework):
    _svc_name_ = "RPA_Reclutamiento_Service"
    _svc_display_name_ = "RPA Reclutamiento CVs - Umbral S.A."
    _svc_description_ = "Servicio que monitorea la carpeta C:\\RPA_Reclutamiento y convierte automáticamente los PDFs en JSON estructurados para el flujo RPA de reclutamiento."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("🔄 Servicio RPA Reclutamiento iniciado correctamente.")
        self.main()

    def main(self):
        while self.running:
            try:
                procesar_pdfs()
            except Exception as e:
                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ Error general: {str(e)}\n")
            time.sleep(intervalo)


if __name__ == "__main__":
    print("🧠 Iniciando modo manual de prueba...")
    import time, json, os, pdfplumber, shutil

    # Leer configuración
    with open("config_rpa.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ruta_pdfs = config["rutas"]["pdfs"]
    ruta_json = config["rutas"]["salida_json"]
    ruta_proc = config["rutas"]["procesados"]

    # Procesar archivos PDF
    for archivo in os.listdir(ruta_pdfs):
        if archivo.lower().endswith(".pdf"):
            ruta_completa = os.path.join(ruta_pdfs, archivo)
            print(f"📄 Procesando {archivo}")

            texto = ""
            with pdfplumber.open(ruta_completa) as pdf:
                for pagina in pdf.pages:
                    texto += (pagina.extract_text() or "") + "\n"

            data = {"nombre_archivo": archivo, "contenido_completo": texto.strip()}
            salida = os.path.join(ruta_json, os.path.splitext(archivo)[0] + ".json")

            with open(salida, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            shutil.move(ruta_completa, os.path.join(ruta_proc, archivo))
            print(f"✅ Guardado en {salida}")

    print("🟢 Proceso manual finalizado correctamente.")
