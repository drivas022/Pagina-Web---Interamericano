# Archivo README.md

## Proyecto: Convertir archivos a Audio

Este proyecto es una API desarrollada con FastAPI que permite subir archivos en formato PDF o DOCX, extraer su contenido de texto y convertirlo en un archivo de audio MP3 utilizando gTTS.

### Requisitos previos
- Tener instalado Python 3.7 o superior.
- Tener `pip` actualizado.

### Instalación
1. Clonar este repositorio:
   ```sh
   git clone https://github.com/tu-repositorio/tu-proyecto.git
   cd tu-proyecto
   ```
2. Instalar las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

### Uso
1. Ejecutar el servidor con Uvicorn:
   ```sh
   uvicorn main:app --reload
   ```
2. Acceder a la API en el navegador:
   ```
   http://127.0.0.1:8000
   ```
3. Para probar la API, sube un archivo PDF o DOCX en el endpoint `/convert` y obtendrás un enlace de descarga del archivo MP3 generado.

### Estructura del Proyecto
```
📂 tu-proyecto
├── 📂 static        # Archivos estáticos como CSS, JS e imágenes
├── 📂 audio         # Carpeta donde se almacenan los audios generados
├── 📂 templates     # Plantillas HTML
├── main.py         # Código principal de la API
├── requirements.txt # Dependencias necesarias para correr el proyecto
├── README.md       # Instrucciones y documentación del proyecto
```

### Notas
- Los archivos de audio generados se almacenarán en la carpeta `audio/`.
- Se recomienda usar un entorno virtual para evitar conflictos con otras dependencias.

### Licencia
Este proyecto está bajo la licencia MIT.
