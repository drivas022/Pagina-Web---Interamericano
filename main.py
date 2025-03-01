from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import pyttsx3
import PyPDF2
import os
import uuid

app = FastAPI()

# Montamos la carpeta "static" para servir CSS u otros archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Servir el formulario HTML para subir el PDF.
    """
    # Podríamos devolver directamente contenido HTML aquí,
    # o podemos leer el HTML desde una plantilla "index.html"
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/convert")
async def convert_pdf_to_audio(file: UploadFile = File(...)):
    """
    Endpoint que recibe el PDF y devuelve un archivo mp3.
    """
    # 1. Guardar temporalmente el PDF subido para procesarlo.
    pdf_filename = f"temp_{uuid.uuid4().hex}.pdf"
    with open(pdf_filename, "wb") as buffer:
        buffer.write(await file.read())

    # 2. Extraer texto del PDF
    text = extract_text_from_pdf(pdf_filename)

    # 3. Usar pyttsx3 para convertir a voz
    mp3_filename = f"output_{uuid.uuid4().hex}.mp3"
    text_to_speech(text, mp3_filename)

    # 4. Borrar el PDF temporal (opcional)
    os.remove(pdf_filename)

    # 5. Devolver el archivo mp3
    return FileResponse(path=mp3_filename, media_type="audio/mpeg", filename="resultado.mp3")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Función auxiliar para extraer el texto completo de un PDF usando PyPDF2.
    """
    text_content = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text_content.append(page.extract_text())
    return "\n".join(text_content)


def text_to_speech(text: str, output_filename: str):
    """
    Convierte el texto en archivo de audio usando pyttsx3.
    """
    engine = pyttsx3.init()
    # Configurar propiedades (voz, velocidad, volumen, etc.) si se desea
    # Por ejemplo:
    # engine.setProperty('rate', 150)     # velocidad de lectura
    # engine.setProperty('volume', 0.8)   # volumen (0.0 a 1.0)
    engine.save_to_file(text, output_filename)
    engine.runAndWait()
