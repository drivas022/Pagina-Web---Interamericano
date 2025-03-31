from fastapi import FastAPI, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import time
import threading
from gtts import gTTS
from pdfminer.high_level import extract_text
from docx import Document
import io
import math
import shutil

app = FastAPI()

# Montar carpeta estática para servir CSS, JS e imágenes
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# Asegurarse de que los directorios necesarios existan
os.makedirs("audio", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Diccionario para almacenar el estado de las tareas
task_status = {}

@app.get("/", response_class=HTMLResponse)
def read_root():
    """Servir la página HTML con el formulario."""
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error al cargar la página: {str(e)}</h1></body></html>", status_code=500)

@app.post("/convert")
async def convert_file_to_audio(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF o DOCX, extrae su texto y lo convierte en un archivo MP3.
    Procesa en segundo plano para archivos grandes.
    """
    try:
        # Identificar el tipo de archivo
        if not file.filename:
            return JSONResponse(content={"error": "No se ha proporcionado un archivo"}, status_code=400)
            
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ["pdf", "docx"]:
            return JSONResponse(content={"error": f"Formato de archivo no soportado: {file_ext}. Sube un PDF o DOCX."}, status_code=400)
        
        # Generar IDs únicos para los archivos
        task_id = str(uuid.uuid4().hex)
        temp_filename = f"temp/temp_{task_id}.{file_ext}"
        mp3_filename = f"audio/{task_id}.mp3"
        
        # Guardar el archivo subido
        file_content = await file.read()
        file_size = len(file_content)
        
        # Verificar tamaño máximo (50MB)
        if file_size > 50 * 1024 * 1024:
            return JSONResponse(content={"error": "El archivo excede el tamaño máximo permitido de 50MB"}, status_code=400)
        
        with open(temp_filename, "wb") as buffer:
            buffer.write(file_content)
        
        # Estimar tiempo basado en el tamaño del archivo
        estimated_time = estimate_processing_time(file_size, file_ext)
        
        # Inicializar el estado de la tarea
        task_status[task_id] = {
            "status": "processing",
            "progress": 0,
            "estimated_time": estimated_time,
            "start_time": time.time(),
            "file_size": file_size
        }
        
        # Iniciar el procesamiento en un hilo separado (no en asyncio)
        thread = threading.Thread(
            target=process_file_thread,
            args=(task_id, temp_filename, file_ext, mp3_filename)
        )
        thread.daemon = True  # El hilo se cerrará cuando el programa principal termine
        thread.start()
        
        return JSONResponse(content={
            "task_id": task_id,
            "estimated_time": estimated_time,
            "file_size": file_size
        })
        
    except Exception as e:
        # Registrar el error para depuración
        print(f"Error al procesar la solicitud de conversión: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """Obtener el estado actual de una tarea de procesamiento."""
    if task_id not in task_status:
        return JSONResponse(content={"error": "Tarea no encontrada"}, status_code=404)
    
    status_info = task_status[task_id].copy()
    
    # Si la tarea está completa, devolver también las URLs
    if status_info["status"] == "completed":
        status_info["audio_url"] = f"/audio/{task_id}.mp3"
        
        # Limpiar el estado después de completado y reportado
        if "text" in status_info:
            text = status_info["text"]
            del status_info["text"]  # No enviar todo el texto en cada consulta de estado
        else:
            # Si el texto ya fue eliminado, leer el archivo de texto
            try:
                with open(f"temp/text_{task_id}.txt", "r", encoding="utf-8") as f:
                    text = f.read()
            except:
                text = "El texto extraído no está disponible"
                
        status_info["text"] = text
    
    # Actualizar el tiempo transcurrido
    if status_info["status"] == "processing":
        elapsed = time.time() - status_info["start_time"]
        status_info["elapsed_time"] = elapsed
        
        # Actualizar la estimación restante
        if status_info["progress"] > 0:
            remaining = (elapsed / status_info["progress"]) * (100 - status_info["progress"])
            status_info["remaining_time"] = remaining
    
    return JSONResponse(content=status_info)

def estimate_processing_time(file_size, file_ext):
    """Estima el tiempo de procesamiento basado en el tamaño del archivo."""
    # Estos valores deberían calibrarse según las características del servidor
    base_time = 10  # segundos base
    
    # Factores de tiempo por MB según tipo de archivo
    factors = {
        "pdf": 2.5,  # segundos por MB para PDF
        "docx": 1.8  # segundos por MB para DOCX
    }
    
    # Calcular tiempo estimado
    size_mb = file_size / (1024 * 1024)
    factor = factors.get(file_ext, 3.0)  # Por defecto usar un factor más conservador
    
    estimated_time = base_time + (size_mb * factor)
    
    # Añadir factor para archivos muy grandes (más de 20MB)
    if size_mb > 20:
        estimated_time *= 1.2
    
    return math.ceil(estimated_time)

def process_file_thread(task_id, file_path, file_ext, mp3_filename):
    """Procesa un archivo en un hilo separado, actualizando el progreso."""
    try:
        # Extraer texto según el tipo de archivo
        task_status[task_id]["progress"] = 10
        
        # Extraer texto según el tipo de archivo
        if file_ext == "pdf":
            text = extract_text_from_pdf(file_path)
        else:  # docx
            text = extract_text_from_docx(file_path)
        
        task_status[task_id]["progress"] = 60
        
        if not text or not text.strip():
            task_status[task_id]["status"] = "error"
            task_status[task_id]["error"] = "No se pudo extraer texto del archivo."
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            return
            
        # Guardar el texto extraído
        text_filename = f"temp/text_{task_id}.txt"
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(text)
            
        # Almacenar el texto para consultas posteriores
        task_status[task_id]["text"] = text
        
        # Dividir el texto en fragmentos si es muy largo para evitar problemas con gTTS
        text_chunks = split_text(text)
        task_status[task_id]["progress"] = 70
        
        # Procesar cada fragmento y concatenar los audios
        temp_audio_files = []
        for i, chunk in enumerate(text_chunks):
            chunk_filename = f"temp/chunk_{task_id}_{i}.mp3"
            
            # Convertir texto a voz (llamada síncrona)
            try:
                text_to_speech(chunk, chunk_filename)
            except Exception as e:
                print(f"Error al procesar fragmento {i}: {str(e)}")
                # Crear un archivo vacío si falla
                with open(chunk_filename, 'wb') as f:
                    f.write(b'')
            
            temp_audio_files.append(chunk_filename)
            
            # Actualizar progreso
            chunk_progress = 20 * (i + 1) / len(text_chunks)
            task_status[task_id]["progress"] = 70 + chunk_progress
        
        # Concatenar los archivos de audio si hay más de uno
        if len(temp_audio_files) > 1:
            concatenate_audio_files(temp_audio_files, mp3_filename)
        elif len(temp_audio_files) == 1:
            # Si solo hay un archivo, copiarlo en lugar de renombrarlo
            # (evita problemas entre diferentes sistemas de archivos)
            shutil.copy2(temp_audio_files[0], mp3_filename)
        
        # Limpiar archivos temporales de forma segura
        for temp_file in temp_audio_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        task_status[task_id]["progress"] = 100
        task_status[task_id]["status"] = "completed"
        task_status[task_id]["completion_time"] = time.time()
        
        # Eliminar el archivo original para liberar espacio
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
            
    except Exception as e:
        print(f"Error en el procesamiento de archivo: {str(e)}")
        task_status[task_id]["status"] = "error"
        task_status[task_id]["error"] = str(e)
        
        # Limpiar archivos en caso de error
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae el texto del PDF usando pdfminer.six con optimizaciones."""
    try:
        # Utilizar parámetros optimizados para la extracción
        return extract_text(pdf_path, page_numbers=None, maxpages=0, caching=True)
    except Exception as e:
        print(f"Error al extraer texto de PDF: {str(e)}")
        return ""

def extract_text_from_docx(docx_path: str) -> str:
    """Extrae el texto de un archivo DOCX usando python-docx."""
    try:
        doc = Document(docx_path)
        # Incluir texto de párrafos, tablas y encabezados para mayor completitud
        text_parts = []
        
        # Extraer texto de párrafos
        for para in doc.paragraphs:
            text_parts.append(para.text)
        
        # Extraer texto de tablas
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    row_text.append(cell.text)
                text_parts.append(" | ".join(row_text))
        
        return "\n".join(text_parts)
    except Exception as e:
        print(f"Error al extraer texto de DOCX: {str(e)}")
        return ""

def split_text(text: str, max_length: int = 5000) -> list:
    """Divide el texto en fragmentos más pequeños para procesamiento eficiente."""
    # Si el texto es más corto que el máximo, devolverlo como un solo fragmento
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    # Dividir por párrafos primero
    paragraphs = text.split('\n')
    current_chunk = ""
    
    for para in paragraphs:
        # Si añadir este párrafo excede el tamaño máximo, guardar el chunk actual y empezar uno nuevo
        if len(current_chunk) + len(para) + 1 > max_length and current_chunk:
            chunks.append(current_chunk)
            current_chunk = para
        else:
            if current_chunk:
                current_chunk += '\n' + para
            else:
                current_chunk = para
    
    # Añadir el último chunk si tiene contenido
    if current_chunk:
        chunks.append(current_chunk)
    
    # Si algún párrafo individual es mayor que max_length, dividirlo por frases
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            final_chunks.append(chunk)
        else:
            # Dividir por frases (puntos, exclamaciones, interrogaciones)
            sentences = []
            for sentence_end in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
                if sentence_end in chunk:
                    parts = chunk.split(sentence_end)
                    for i in range(len(parts) - 1):
                        sentences.append(parts[i] + sentence_end)
                    # El último elemento no termina con el separador
                    sentences.append(parts[-1])
                    chunk = ''.join(sentences)
                    break
            
            # Agrupar frases en chunks de tamaño adecuado
            current_sentence_chunk = ""
            for sentence in sentences:
                if len(current_sentence_chunk) + len(sentence) > max_length and current_sentence_chunk:
                    final_chunks.append(current_sentence_chunk)
                    current_sentence_chunk = sentence
                else:
                    current_sentence_chunk += sentence
            
            if current_sentence_chunk:
                final_chunks.append(current_sentence_chunk)
    
    return final_chunks

def text_to_speech(text: str, output_filename: str):
    """Convierte texto a voz usando gTTS y guarda el audio en un archivo MP3."""
    try:
        tts = gTTS(text=text, lang="es", slow=False)
        tts.save(output_filename)
    except Exception as e:
        print(f"Error en text-to-speech: {str(e)}")
        # Crear un archivo de audio vacío para evitar errores
        with open(output_filename, 'wb') as f:
            f.write(b'')

def concatenate_audio_files(input_files: list, output_file: str):
    """Concatena múltiples archivos de audio en uno solo."""
    try:
        # Para concatenar archivos MP3 se necesita ffmpeg,
        # pero podemos usar una solución simple concatenando bytes
        with open(output_file, 'wb') as outfile:
            for fname in input_files:
                if os.path.exists(fname):
                    with open(fname, 'rb') as infile:
                        outfile.write(infile.read())
    except Exception as e:
        print(f"Error al concatenar archivos de audio: {str(e)}")
        # Crear un archivo de salida vacío si falla
        with open(output_file, 'wb') as f:
            f.write(b'')

# Eliminación periódica de tareas antiguas (ahora usando un hilo normal en lugar de asyncio)
def cleanup_thread():
    """Función para limpiar periódicamente las tareas y archivos antiguos."""
    while True:
        try:
            current_time = time.time()
            to_delete = []
            
            # Hacer una copia del diccionario para evitar errores al modificarlo durante la iteración
            tasks_copy = task_status.copy()
            
            for task_id, task_info in tasks_copy.items():
                # Limpiar tareas completadas después de 1 hora
                if task_info["status"] in ["completed", "error"]:
                    if "completion_time" in task_info and (current_time - task_info["completion_time"]) > 3600:
                        to_delete.append(task_id)
            
            # Eliminar tareas antiguas
            for task_id in to_delete:
                if task_id in task_status:
                    del task_status[task_id]
                
                # Eliminar archivos de texto asociados
                text_file = f"temp/text_{task_id}.txt"
                if os.path.exists(text_file):
                    try:
                        os.remove(text_file)
                    except:
                        pass
            
            # Dormir durante 5 minutos
            time.sleep(300)
            
        except Exception as e:
            print(f"Error en el hilo de limpieza: {str(e)}")
            time.sleep(60)  # Esperar un minuto y reintentar

@app.on_event("startup")
def startup_event():
    """Iniciar el hilo de limpieza al arrancar la aplicación."""
    cleanup_thread_instance = threading.Thread(target=cleanup_thread)
    cleanup_thread_instance.daemon = True
    cleanup_thread_instance.start()