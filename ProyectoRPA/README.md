# 🤖 Scripts Python - Servicio RPA Reclutamiento

Este módulo contiene los scripts Python desarrollados para la automatización de lectura, procesamiento y almacenamiento de información proveniente de currículums en PDF.

## 📂 Contenido

| Archivo | Descripción |
|----------|-------------|
| **servicio_rpa_reclutamiento.py** | Script principal que orquesta la lectura de archivos PDF, extracción de texto y generación de archivos JSON. |
| **leer_pdf.py** | Módulo auxiliar encargado de abrir y procesar el texto de cada CV utilizando pdfplumber. |
| **config_rpa.json** | Archivo de configuración con las rutas de entrada, salida y parámetros del servicio. |
| **log_rpa.txt** | Registro de ejecución manual, validaciones y estado del procesamiento. |

## ⚙️ Librerías utilizadas
- `pdfplumber`
- `os`, `shutil`, `json`
- `datetime`, `time`

## 🧠 Ejecución
```bash
python servicio_rpa_reclutamiento.py
