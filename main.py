import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# 1. Inicialización única de la App
app = FastAPI(title="SVPMUN — Delegación Oficial")

# 2. Configuración de rutas de carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos (fotos, videos, css)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar motor de plantillas (HTMLs)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 3. Definición de todas tus rutas
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/galeria", response_class=HTMLResponse)
async def galeria(request: Request):
    return templates.TemplateResponse("galeria.html", {"request": request})

@app.get("/crisis-roma", response_class=HTMLResponse)
async def crisis_roma(request: Request):
    return templates.TemplateResponse("crisis_roma.html", {"request": request})

@app.get("/crisis_ue_2035", response_class=HTMLResponse)
async def crisis_ue(request: Request):
    return templates.TemplateResponse("crisis_ue_2035.html", {"request": request})

@app.get("/drills", response_class=HTMLResponse)
async def drills(request: Request):
    return templates.TemplateResponse("drills.html", {"request": request})

# Rutas adicionales (asegúrate de tener estos archivos en la carpeta templates)
@app.get("/nosotros", response_class=HTMLResponse)
async def nosotros(request: Request):
    return templates.TemplateResponse("nosotros.html", {"request": request})

@app.get("/inscripciones", response_class=HTMLResponse)
async def inscripciones(request: Request):
    return templates.TemplateResponse("inscripciones.html", {"request": request})

@app.get("/oms", response_class=HTMLResponse)
async def oms(request: Request):
    return templates.TemplateResponse("oms.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "app": "SVPMUN"}

# 4. Ejecución local (Vercel ignorará esto, pero sirve para tus pruebas)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

#python -m uvicorn main:app --reload
#python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# ssh -R 80:127.0.0.1:8000 nokey@localhost.run
# python -m uvicorn main:app --host 127.0.0.1 --port 8000