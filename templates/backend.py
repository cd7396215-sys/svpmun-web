import os
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
import google.generativeai as genai
from fastapi.responses import FileResponse

# =====================================================================
# CARGAR VARIABLES DE ENTORNO (.env)
# =====================================================================
load_dotenv() # Esto lee automáticamente el archivo .env en tu carpeta (En Vercel usa las Environment Variables del dashboard)

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
# CONFIGURACIÓN DE FASTAPI
# =====================================================================
app = FastAPI(title="AI Chat UI Backend", version="1.0.0")

# Permitir CORS para que tu HTML pueda comunicarse sin problemas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde tu HTML local y Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# MODELOS DE DATOS (PYDANTIC)
# =====================================================================
class ChatRequest(BaseModel):
    prompt: str
    model_name: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model_used: str

# =====================================================================
# LÓGICA DEL SISTEMA (PROMPT MASTER)
# =====================================================================
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
# RUTAS DE LA API
# =====================================================================

@app.get("/bot")
async def serve_frontend():
    # Esto le dice a FastAPI que muestre tu HTML cuando entren a la página principal
    return FileResponse("chatbot.html")

# CORRECCIÓN AQUÍ: Cambiado de "/bot" a "/chat" para que coincida con el frontend
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
            raise HTTPException(status_code=400, detail="Modelo no soportado o API Key faltante en las variables de entorno de Vercel")

        return ChatResponse(response=response_text, model_used=model_choice)

    except Exception as e:
        print(f"Error en el servidor con el modelo {model_choice}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando la solicitud: {str(e)}")