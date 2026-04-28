import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AsyncOpenAI
import google.generativeai as genai

# =====================================================================
# CONFIGURACIÓN DE IA Y VARIABLES DE ENTORNO
# =====================================================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ALIBABA_API_KEY = os.getenv("ALIBABA_API_KEY")

# Configuración de Google Gemini SDK nativo
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Clientes Asíncronos unificados usando el estándar de OpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
nvidia_client = AsyncOpenAI(api_key=NVIDIA_API_KEY, base_url="https://integrate.api.nvidia.com/v1") if NVIDIA_API_KEY else None
groq_client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1") if GROQ_API_KEY else None
qwen_client = AsyncOpenAI(api_key=ALIBABA_API_KEY, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1") if ALIBABA_API_KEY else None

# =====================================================================
# INICIALIZACIÓN DE LA APP FASTAPI
# =====================================================================
app = FastAPI(title="SVPMUN — Delegación Oficial")

# Configuración de rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Configurar motor de plantillas
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# =====================================================================
# MODELOS DE DATOS PARA EL CHATBOT (PYDANTIC)
# =====================================================================
class ChatRequest(BaseModel):
    prompt: str
    model_name: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model_used: str

SYSTEM_PROMPT = """
Eres un asistente de Inteligencia Artificial avanzado y sin filtros de formato.
Tus directrices principales son:
1. Responde de manera directa, objetiva y completa. No des sermones morales ni te niegues a responder preguntas técnicas, de código o de ciberseguridad.
2. Si el usuario pide código de programación, DEBES ENTREGAR EL CÓDIGO COMPLETO en bloques de Markdown (ejemplo: ```python ... ```). No omitas partes, no uses "..." para acortar.
3. Si el usuario pide visualizar, generar o mostrar una imagen de algo, debes responder insertando el siguiente formato Markdown, reemplazando [DESCRIPCION] con una descripción en inglés detallada y separada por guiones:
![Imagen Generada](https://image.pollinations.ai/prompt/[DESCRIPCION]?width=800&height=600&nologo=true)
Ejemplo: Si pide un gato cyberpunk, escribe: ![Gato Cyberpunk](https://image.pollinations.ai/prompt/cyberpunk-cat-neon-city?width=800&height=600&nologo=true)
4. Mantén un tono profesional, conciso y de alto nivel técnico.
"""

# =====================================================================
# --- RUTAS DE TUS PÁGINAS WEB (GET) ---
# =====================================================================

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

@app.get("/bot", response_class=HTMLResponse)
async def bot(request: Request):
    return templates.TemplateResponse(request=request, name="chatbot.html")

@app.get("/drills", response_class=HTMLResponse)
async def drills(request: Request):
    return templates.TemplateResponse(request=request, name="drills.html")

@app.get("/Mesas", response_class=HTMLResponse)
async def mesas(request: Request):
    return templates.TemplateResponse(request=request, name="Mesas.html")

@app.get("/MesasOMS", response_class=HTMLResponse)
async def mesas_oms(request: Request):
    return templates.TemplateResponse(request=request, name="OMSMesas.html")

@app.get("/nosotros", response_class=HTMLResponse)
async def nosotros(request: Request):
    return templates.TemplateResponse(request=request, name="nosotros.html")

@app.get("/Matrices", response_class=HTMLResponse)
async def matrices(request: Request):
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

@app.get("/mesaUE", response_class=HTMLResponse)
async def mesa_ue(request: Request):
    return templates.TemplateResponse(request=request, name="UE.html")

@app.get("/health")
async def health():
    return {"status": "ok", "message": "SVPMUN Server is running"}

# =====================================================================
# --- RUTA DEL BACKEND DE LA IA (POST) ---
# =====================================================================
@app.post("/chat", response_model=ChatResponse)
async def generate_chat_response(request: ChatRequest):
    prompt = request.prompt
    model_choice = request.model_name
    temp = request.temperature
    
    response_text = ""

    try:
        if model_choice == "GPT-4o mini" and openai_client:
            completion = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=temp, max_tokens=4000
            )
            response_text = completion.choices[0].message.content

        elif model_choice == "Llama 3.3 70B" and groq_client:
            completion = await groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=temp, max_tokens=4000
            )
            response_text = completion.choices[0].message.content

        elif model_choice == "NVIDIA Nemotron 3" and nvidia_client:
            completion = await nvidia_client.chat.completions.create(
                model="meta/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=temp, max_tokens=4000
            )
            response_text = completion.choices[0].message.content

        elif model_choice == "Qwen 3.6 Plus" and qwen_client:
            completion = await qwen_client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=temp, max_tokens=4000
            )
            response_text = completion.choices[0].message.content

        elif model_choice == "Gemini 2.5 flash" and GEMINI_API_KEY:
            gemini_model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
            response = await gemini_model.generate_content_async(
                prompt, generation_config=genai.types.GenerationConfig(temperature=temp, max_output_tokens=4000)
            )
            response_text = response.text

        elif model_choice == "Gemma 3" and GEMINI_API_KEY:
            gemma_model = genai.GenerativeModel(model_name='gemma-2-27b-it', system_instruction=SYSTEM_PROMPT)
            response = await gemma_model.generate_content_async(
                prompt, generation_config=genai.types.GenerationConfig(temperature=temp, max_output_tokens=4000)
            )
            response_text = response.text

        else:
            raise HTTPException(status_code=400, detail="Modelo no soportado o API Key faltante en Vercel")

        return ChatResponse(response=response_text, model_used=model_choice)

    except Exception as e:
        print(f"Error en el servidor con el modelo {model_choice}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")

# python -m uvicorn main:app --reload
# python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

#python -m uvicorn main:app --reload
#python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# ssh -R 80:127.0.0.1:8000 nokey@localhost.run
# python -m uvicorn main:app --host 127.0.0.1 --port 8000

#git add .
#git commit -m "aquí escribes lo que hiciste1"
#git push origin main