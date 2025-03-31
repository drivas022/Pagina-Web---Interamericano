from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pathlib import Path
import uuid
import shutil
import pdfplumber
from gtts import gTTS
import os

app = FastAPI()

# Directorio para almacenar archivos
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Servir la página HTML con el formulario.
    """
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/convert")
async def convert_pdf_to_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Procesar el archivo PDF, extraer texto y convertirlo a MP3.
    """
    # Guardar el PDF temporalmente
    temp_pdf_path = Path(f"temp_{uuid.uuid4().hex}.pdf")
    with temp_pdf_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extraer texto del PDF
    text = ""
    with pdfplumber.open(temp_pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + " "
    
    temp_pdf_path.unlink()  # Eliminar PDF después de la extracción
    
    if not text.strip():
        return JSONResponse(content={"error": "No se pudo extraer texto del PDF."}, status_code=400)
    
    # Generar nombre de archivo MP3
    mp3_filename = f"{uuid.uuid4().hex}.mp3"
    mp3_path = AUDIO_DIR / mp3_filename
    
    # Procesar en segundo plano
    background_tasks.add_task(generate_audio, text, mp3_path)
    
    return JSONResponse(content={
        "texto": text,
        "audio_url": f"/audio/{mp3_filename}"
    })

def generate_audio(text: str, output_path: Path):
    """Genera el archivo de audio a partir del texto."""
    try:
        tts = gTTS(text=text, lang='es', slow=False)
        tts.save(str(output_path))
    except Exception as e:
        print(f"Error al generar el audio: {e}")

@app.get("/audio/{filename}")
def get_audio(filename: str):
    """
    Servir el archivo de audio generado.
    """
    file_path = AUDIO_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)