from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from gtts import gTTS
from pdfminer.high_level import extract_text

app = FastAPI()

# Montar carpeta estática
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")  # Para servir archivos MP3


@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Servir la página HTML con el formulario.
    """
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.post("/convert")
async def convert_pdf_to_audio(file: UploadFile = File(...)):
    """
    Recibe un PDF, extrae su texto y lo convierte en un archivo MP3.
    """
    # Guardar temporalmente el PDF
    pdf_filename = f"temp_{uuid.uuid4().hex}.pdf"
    with open(pdf_filename, "wb") as buffer:
        buffer.write(await file.read())

    # Extraer texto
    text = extract_text_from_pdf(pdf_filename)

    if not text.strip():
        os.remove(pdf_filename)
        return JSONResponse(content={"error": "No se pudo extraer texto del PDF."}, status_code=400)

    # Convertir texto a MP3
    mp3_filename = f"audio/{uuid.uuid4().hex}.mp3"
    text_to_speech(text, mp3_filename)

    # Borrar el PDF temporal
    os.remove(pdf_filename)

    # Devolver JSON con el texto extraído y la URL del MP3
    return JSONResponse(content={
        "texto": text,
        "audio_url": f"/{mp3_filename}"
    })


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrae el texto del PDF usando pdfminer.six.
    """
    return extract_text(pdf_path)


def text_to_speech(text: str, output_filename: str):
    """
    Convierte texto a voz usando gTTS y guarda el audio en un archivo MP3.
    """
    tts = gTTS(text=text, lang="es")
    tts.save(output_filename)
