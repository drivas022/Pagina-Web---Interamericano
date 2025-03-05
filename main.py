from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from gtts import gTTS
from pdfminer.high_level import extract_text
from docx import Document  # Importar para leer archivos DOCX

app = FastAPI()

# Montar carpeta estática para servir CSS, JS e imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")  # Para archivos MP3

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Servir la página HTML con el formulario."""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/convert")
async def convert_file_to_audio(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF o DOCX, extrae su texto y lo convierte en un archivo MP3.
    """
    try:
        # Identificar el tipo de archivo
        file_ext = file.filename.split(".")[-1].lower()
        temp_filename = f"temp_{uuid.uuid4().hex}.{file_ext}"
        
        with open(temp_filename, "wb") as buffer:
            buffer.write(await file.read())

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
        return JSONResponse(content={"error": str(e)}, status_code=500)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae el texto del PDF usando pdfminer.six."""
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path: str) -> str:
    """Extrae el texto de un archivo DOCX usando python-docx."""
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def text_to_speech(text: str, output_filename: str):
    """Convierte texto a voz usando gTTS y guarda el audio en un archivo MP3."""
    tts = gTTS(text=text, lang="es")
    tts.save(output_filename)
