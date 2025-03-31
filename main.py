from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import traceback
from gtts import gTTS
from pdfminer.high_level import extract_text
from docx import Document

app = FastAPI()

# Asegurar que las carpetas necesarias existen
for folder in ["static", "audio", "temp"]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Montar carpetas estáticas
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")  # Para archivos MP3

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Servir la página HTML con el formulario."""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: No se encontró el archivo index.html</h1>", status_code=500)

@app.post("/convert")
async def convert_file_to_audio(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF o DOCX, extrae su texto y lo convierte en un archivo MP3.
    """
    try:
        # Identificar el tipo de archivo
        file_ext = file.filename.split(".")[-1].lower()
        temp_filename = os.path.join("temp", f"temp_{uuid.uuid4().hex}.{file_ext}")

        with open(temp_filename, "wb") as buffer:
            buffer.write(await file.read())

        print(f"Archivo guardado en: {temp_filename}, Tamaño: {os.path.getsize(temp_filename)} bytes")

        # Extraer texto según el tipo de archivo
        if file_ext == "pdf":
            text = extract_text_from_pdf(temp_filename)
        elif file_ext == "docx":
            text = extract_text_from_docx(temp_filename)
        else:
            os.remove(temp_filename)
            return JSONResponse(content={"error": "Formato de archivo no soportado. Sube un PDF o DOCX."}, status_code=400)

        if not text.strip():
            os.remove(temp_filename)
            return JSONResponse(content={"error": "No se pudo extraer texto del archivo."}, status_code=400)

        # Convertir texto a MP3
        mp3_filename = f"audio/{uuid.uuid4().hex}.mp3"
        text_to_speech(text, mp3_filename)

        os.remove(temp_filename)

        return JSONResponse(content={
            "texto": text,
            "audio_url": f"/{mp3_filename}"
        })

    except Exception as e:
        error_message = f"Error: {str(e)}\n{traceback.format_exc()}"
        return JSONResponse(content={"error": error_message}, status_code=500)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae el texto del PDF usando pdfminer.six."""
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error al extraer texto del PDF: {e}")
        return ""

def extract_text_from_docx(docx_path: str) -> str:
    """Extrae el texto de un archivo DOCX usando python-docx."""
    try:
        doc = Document(docx_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error al extraer texto del DOCX: {e}")
        return ""

def text_to_speech(text: str, output_filename: str):
    """Convierte texto a voz usando gTTS y guarda el audio en un archivo MP3."""
    try:
        tts = gTTS(text=text, lang="es")
        tts.save(output_filename)
        print(f"Archivo MP3 guardado en {output_filename}")
    except Exception as e:
        print(f"Error al generar el archivo de audio: {e}")
