  # Convertidor de Documentos a Audio

  Una aplicación web que convierte archivos PDF y DOCX a formato de audio MP3, permitiendo escuchar el contenido de tus documentos en lugar de leerlos.

  ## 📋 Características

  - Interfaz web intuitiva y moderna
  - Soporte para archivos PDF y DOCX
  - Conversión de texto a voz en español
  - Procesamiento asíncrono de archivos grandes
  - Visualización del texto extraído
  - Descarga de archivos de audio generados
  - Indicador de progreso en tiempo real
  - Estimación de tiempo restante para la conversión

  ## 🔄 Flujo de trabajo

  1. **Carga de archivos**: 
    - El usuario sube un archivo PDF o DOCX a través de una interfaz con arrastrar y soltar o selección de archivo
    - El archivo se valida (formato y tamaño máximo de 50MB)

  2. **Procesamiento en el servidor**:
    - El archivo se envía al servidor y se guarda temporalmente con un ID único
    - El procesamiento ocurre en segundo plano (usando hilos) para no bloquear la interfaz
    - Fases del procesamiento:
      - Extracción del texto del PDF (usando pdfminer.six) o DOCX (usando python-docx)
      - El texto extraído se guarda en un archivo temporal (`temp/text_{task_id}.txt`)
      - División del texto en fragmentos manejables si es muy extenso
      - Conversión de cada fragmento a audio mediante gTTS (Google Text-to-Speech) en español
      - Concatenación de los fragmentos de audio en un solo archivo MP3 final
      - Almacenamiento del archivo MP3 resultante en la carpeta "audio"
    - La interfaz de usuario consulta periódicamente al servidor para mostrar el progreso en tiempo real

  3. **Resultado**:
    - Una vez completado el proceso, el usuario puede:
      - Ver el texto extraído del documento
      - Reproducir el audio generado directamente en la web
      - Descargar el archivo MP3 generado
      - Descargar el texto extraído como archivo TXT

  ## 🛠️ Requisitos previos

  - Python 3.7 o superior
  - Conexión a internet (para la síntesis de voz con gTTS)
  - Al menos 200MB de espacio libre en disco

  ## ⚙️ Instalación

  ### 1. Clonar el repositorio

  ```bash
  git clone https://github.com/drivas022/Pagina-Web---Interamericano.git
  ```

  ### 2. Instalar las dependencias

  ```bash
  pip install -r requirements.txt
  ```

  Si no existe el archivo requirements.txt, instala las dependencias manualmente:

  ```bash
  pip install fastapi uvicorn python-multipart gtts pdfminer.six python-docx
  ```

  ### 3. Crear las carpetas necesarias

  ```bash
  mkdir -p templates static audio temp
  ```

  ## 🚀 Ejecución de la aplicación

  ### Iniciar el servidor

  ```bash
  uvicorn main:app --reload
  ```

  O también se puede utilizar:

  ```bash
  python -m uvicorn main:app --reload
  ```

  Para uso en producción, se recomienda:

  ```bash
  uvicorn main:app --workers 1 --host 0.0.0.0 --port 8000
  ```

  ### Acceso a la aplicación

  Abre tu navegador web y visita:
  ```
  http://127.0.0.1:8000
  ```

  ## 📖 Guía de uso

  1. **Carga de archivos**: 
    - Arrastra y suelta un archivo PDF o DOCX en la zona indicada o haz clic en "Seleccionar archivo"
    - El tamaño máximo permitido es de 50MB

  2. **Procesamiento**:
    - Una vez cargado el archivo, haz clic en "Convertir"
    - Se mostrará una barra de progreso y una estimación del tiempo restante
    - El proceso tiene 4 fases: Recepción, Extracción, Sintetización y Finalización

  3. **Resultado**:
    - Una vez completado el proceso, podrás:
      - Ver el texto extraído del documento
      - Reproducir el audio generado directamente en la web
      - Descargar el archivo MP3 generado
      - Descargar el texto extraído como archivo TXT

  ## 🗂️ Estructura del proyecto

  ```
  📂 convertidor-documentos-audio
  ├── 📂 audio         # Archivos MP3 generados (se crea automáticamente)
  ├── 📂 static        # Archivos estáticos (CSS, JS)
  │   └── style.css    # Estilos de la interfaz web
  ├── 📂 templates     # Plantillas HTML
  │   └── index.html   # Página principal de la aplicación
  ├── 📂 temp          # Archivos temporales (se crea automáticamente)
  ├── .gitignore       # Archivos y carpetas ignoradas por Git
  ├── main.py          # Código principal de la aplicación
  ├── requirements.txt # Dependencias del proyecto
  └── README.md        # Documentación del proyecto
  ```

  ## 🔧 Configuración avanzada

  Para optimizar el procesamiento de archivos grandes, puedes ajustar estos parámetros en main.py:

  - `max_length` en la función `split_text`: Controla el tamaño de los fragmentos de texto
  - `factors` en la función `estimate_processing_time`: Ajusta los tiempos estimados según el tipo de archivo

  ## ⚠️ Solución de problemas comunes

  - **Error "cannot schedule new futures after shutdown"**: 
    - Reinicia completamente el servidor (detén y vuelve a iniciar)
    - Verifica que no haya otros procesos usando el mismo puerto

  - **Proceso de conversión demasiado lento**:
    - Divide documentos grandes en partes más pequeñas
    - Verifica tu conexión a internet (necesaria para gTTS)
    - Asegúrate de que tu servidor tenga suficiente CPU disponible

  - **Error al cargar archivos**:
    - Verifica que el formato sea PDF o DOCX
    - Comprueba que el archivo no esté dañado o protegido con contraseña
    - El tamaño debe ser menor a 50MB

  - **La conversión se completa pero el audio no se reproduce**:
    - Verifica que el archivo MP3 se haya generado correctamente en la carpeta "audio"
    - Comprueba que tu navegador tenga permisos para reproducir audio
    - Intenta descargar el archivo y reproducirlo en otro reproductor

  Desarrollado por Diego Rivas