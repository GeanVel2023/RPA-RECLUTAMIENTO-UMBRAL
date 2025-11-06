import pdfplumber
import json
import os
import shutil

# ================================
# Rutas
# ================================
ruta_pdfs = r"C:\RPA_Reclutamiento"
ruta_salida = r"C:\RPA_Reclutamiento\json"
ruta_procesados = r"C:\RPA_Reclutamiento\pdfProcesados"

# Crear carpetas si no existen
for carpeta in [ruta_salida, ruta_procesados]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# ================================
# Proceso principal
# ================================
for archivo in os.listdir(ruta_pdfs):
    if archivo.lower().endswith(".pdf"):
        ruta_completa = os.path.join(ruta_pdfs, archivo)

        print(f"Procesando: {archivo}")

        # Extraer texto
        texto = ""
        with pdfplumber.open(ruta_completa) as pdf:
            for pagina in pdf.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto += extraido + "\n"

        # Crear JSON simple
        data = {
            "nombre_archivo": archivo,
            "contenido_completo": texto.strip()
        }

        # Guardar JSON
        nombre_salida = os.path.splitext(archivo)[0] + ".json"
        ruta_json = os.path.join(ruta_salida, nombre_salida)
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Mover PDF procesado
        shutil.move(ruta_completa, os.path.join(ruta_procesados, archivo))

        print(f"✅ JSON creado: {ruta_json}")
        print(f"📂 PDF movido a: {ruta_procesados}")

print("Proceso finalizado.")
