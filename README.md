# Pagina-Web---Interamericano
@Autor Diego Rivas
**Y el programa tendra la siguiente estructura**
```
.
├── main.py        (archivo principal FastAPI)
├── templates
│   └── index.html (formulario de subida)
└── static
    └── style.css  (hoja de estilo opcional)
```
**Primero se instala las librerias de python necesarias (instale las que sean necesarias)**
**OJO DEBE TENER INSTALADO PIP**
**Puede probar instalando este script, si le da error puede instalar uno por uno.**
```
pip install fastapi uvicorn PyPDF2 gtts pdfminer.six
```
**Si en dado caso le dio error el script de arriba instale lo siguiente:**    
```
pip install fastapi uvicorn PyPDF2 pyttsx3
```
```
pip install gtts
```
```
pip install pdfminer.six
```
**Finalmente instale el siguiente: **
```
pip install python-multipart
```


**Para ejecutar la aplicación de manera local corremos el siguiente comando**
```
uvicorn main:app --reload
```
**Si este no corre, puede probar con el siguiente comando**
```
python -m uvicorn main:app --reload
```

