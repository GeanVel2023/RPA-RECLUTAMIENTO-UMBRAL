import win32serviceutil
import win32service
import win32event
import servicemanager
import time
import os
import pdfplumber
import json
import shutil
import re
import sys
import traceback
import unicodedata

# ================================
# Cargar configuración
# ================================
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config_rpa.json")

def cargar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"Configuración cargada correctamente desde {CONFIG_PATH}")
        return config
    except Exception as e:
        msg = f"No se pudo cargar config_rpa.json: {e}"
        print(msg)
        return None

config = cargar_config()
if not config:
    raise Exception("No se pudo leer la configuración. Verifique config_rpa.json")

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
# Función: Dividir texto en CVs
# ================================
def dividir_cvs(texto):
    patrones = [
        r"(?=Curr[ií]culum\s*Vitae)",
        r"(?=Hoja\s*de\s*Vida)",
        r"(?=Hoja\s*de\s*vida)",
        r"(?=Nombre\s*:)",
        r"(?=Datos\s*Personales)",
        r"(?=Candidato\s*:)"
    ]

    patron_combinado = "|".join(patrones)
    secciones = re.split(patron_combinado, texto, flags=re.IGNORECASE)
    secciones = [s.strip() for s in secciones if len(s.strip()) > 50]
    return secciones

# ================================
# Función: Limpiar nombres
# ================================
def limpiar_nombre(nombre):
    nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z0-9_ ]', '', nombre)
    return "_".join(nombre.split())

# ================================
# Función: Procesar PDFs
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

                secciones = dividir_cvs(texto)
                if len(secciones) > 1:
                    print(f"Se detectaron {len(secciones)} CVs en {archivo}")
                else:
                    print(f"Solo se detectó un CV en {archivo}")

                for i, cv_texto in enumerate(secciones, start=1):
                    match = re.search(r"(?:Hoja\s*de\s*vida\s*de|Curr[ií]culum\s*Vitae\s*de|Nombre\s*:)\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)", cv_texto, re.IGNORECASE)
                    if match:
                        nombre_persona = limpiar_nombre(match.group(1).strip().title())
                        nombre_salida = f"{os.path.splitext(archivo)[0]}_{nombre_persona}.json"
                    else:
                        nombre_salida = f"{os.path.splitext(archivo)[0]}_cv{i}.json"

                    ruta_json = os.path.join(ruta_salida, nombre_salida)

                    data = {
                        "archivo_origen": archivo,
                        "indice_cv": i,
                        "nombre_detectado": match.group(1).strip() if match else None,
                        "contenido_completo": cv_texto.strip()
                    }

                    with open(ruta_json, "w", encoding=config["parametros"]["codificacion"]) as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                if not secciones:
                    nombre_salida = os.path.splitext(archivo)[0] + ".json"
                    ruta_json = os.path.join(ruta_salida, nombre_salida)
                    with open(ruta_json, "w", encoding=config["parametros"]["codificacion"]) as f:
                        json.dump({"nombre_archivo": archivo, "contenido_completo": texto.strip()}, f, ensure_ascii=False, indent=4)

                shutil.move(ruta_completa, os.path.join(ruta_procesados, archivo))

                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Procesado correctamente: {archivo}\n")

            except Exception as e:
                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error procesando {archivo}: {str(e)}\n")
                    log.write(traceback.format_exc() + "\n")

# ================================
# Servicio de Windows
# ================================
class RPAService(win32serviceutil.ServiceFramework):
    _svc_name_ = "RPA_Reclutamiento_Service_v2"
    _svc_display_name_ = "RPA Reclutamiento CVs v2 - Umbral S.A."
    _svc_description_ = "Servicio que monitorea C:\\RPA_PYTHOM\\ProyectoRPA y convierte PDFs en JSON, dividiendo múltiples CVs automáticamente."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        with open(ruta_log, "a", encoding="utf-8") as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando como servicio...\n")
        self.main()

    def main(self):
        while self.running:
            try:
                procesar_pdfs()
            except Exception as e:
                with open(ruta_log, "a", encoding="utf-8") as log:
                    log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error general: {str(e)}\n")
                    log.write(traceback.format_exc() + "\n")
            time.sleep(intervalo)

# ================================
# Ejecución manual o como servicio
# ================================
if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(RPAService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("Iniciando modo manual de prueba...")
            procesar_pdfs()
            print("Proceso manual finalizado correctamente.")
    except Exception as e:
        with open("C:\\RPA_PYTHOM\\ProyectoRPA\\log_error_servicio.txt", "a", encoding="utf-8") as log:
            log.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error al iniciar servicio: {str(e)}\n")
            log.write(traceback.format_exc() + "\n")
