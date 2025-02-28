# Pagina-Web---Interamericano
**Primero se instala las librerias de python necesarias**
```
pip install fastapi uvicorn PyPDF2 pyttsx3
```
**Y el programa tendra la siguiente estructura**
```
.
├── main.py        (archivo principal FastAPI)
├── templates
│   └── index.html (formulario de subida)
└── static
    └── style.css  (hoja de estilo opcional)
```

**Para ejecutar la aplicación de manera local corremos el siguiente comando**
```
uvicorn main:app --reload
```
