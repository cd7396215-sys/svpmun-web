import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="SVPMUN — Delegación Oficial")

# Configuración de rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar motor de plantillas
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- RUTAS ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/galeria", response_class=HTMLResponse)
async def galeria(request: Request):
    return templates.TemplateResponse(request=request, name="galeria.html")

@app.get("/crisis-roma", response_class=HTMLResponse)
async def crisis_roma(request: Request):
    return templates.TemplateResponse(request=request, name="crisis_roma.html")

@app.get("/crisis_ue_2035", response_class=HTMLResponse)
async def crisis_ue(request: Request):
    return templates.TemplateResponse(request=request, name="crisis_ue_2035.html")

@app.get("/drills", response_class=HTMLResponse)
async def drills(request: Request):
    return templates.TemplateResponse(request=request, name="drills.html")

@app.get("/nosotros", response_class=HTMLResponse)
async def nosotros(request: Request):
    return templates.TemplateResponse(request=request, name="nosotros.html")

@app.get("/Matrices", response_class=HTMLResponse)
async def nosotros(request: Request):
    return templates.TemplateResponse(request=request, name="Matrices.html")

@app.get("/inscripciones", response_class=HTMLResponse)
async def inscripciones(request: Request):
    return templates.TemplateResponse(request=request, name="inscripciones.html")

@app.get("/inscripciones-drills", response_class=HTMLResponse)
async def inscripcionesdrills(request: Request):
    return templates.TemplateResponse(request=request, name="inscripciones-drills.html")

@app.get("/oms", response_class=HTMLResponse)
async def oms(request: Request):
    return templates.TemplateResponse(request=request, name="oms.html")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "SVPMUN Server is running"}

#python -m uvicorn main:app --reload
#python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# ssh -R 80:127.0.0.1:8000 nokey@localhost.run
# python -m uvicorn main:app --host 127.0.0.1 --port 8000

#git add .
#git commit -m "aquí escribes lo que hiciste1"
#git push origin main