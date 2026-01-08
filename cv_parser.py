import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
import fitz  # PyMuPDF

# Configure Gemini API
# User must ensure GEMINI_API_KEY is set in environment variables
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """
Eres un especialista en extracción de datos para CVs optimizados para ATS.
Analiza la información provista y genera un objeto JSON con la estructura EXACTA detallada abajo.

ESTRUCTURA JSON REQUERIDA:
{
  "nombre": "Nombre completo",
  "telefono": "+54 9 XXXXXXXXXX",
  "email": "email@ejemplo.com",
  "ciudad": "Ciudad, Provincia",
  "linkedin": "link o vacío",
  "perfil": "Resumen profesional atractivo y humano",
  "experiencia": [
    {
      "puesto": "Título del cargo",
      "empresa": "Nombre de la empresa",
      "fechas": "Mes AAAA – Mes AAAA (u 'Actualidad')",
      "ubicacion": "Ciudad/Barrio (solo si es específico)",
      "logros": ["Tarea o logro con punto final."]
    }
  ],
  "educacion": [
    {
      "titulo": "Nombre del estudio o curso",
      "institucion": "Institución",
      "fechas": "Rango de fechas o año",
      "ubicacion": "Ciudad/Barrio (solo si es específico)"
    }
  ],
  "habilidades": ["Habilidad 1", "...", "Habilidad 8"],
  "idiomas": [{"idioma": "Español", "nivel": "Nativo"}, {"idioma": "Inglés", "nivel": "Nivel"}],
  "licencias": ["Información extra como movilidad o disponibilidad"]
}

REGLAS CRÍTICAS DE INTELIGENCIA Y FORMATO:
1. PROHIBICIÓN DE INVENCIÓN: No inventes NUNCA información que el usuario no proveyó. No uses palabras como "Desconocida", "No informado", o similares. Si un dato no está, usa string vacío ("").
2. UBICACIONES: Si no hay una ciudad o barrio específico, deja el campo de ubicación vacío (""). No pongas "Argentina" como ubicación genérica.
3. REFERENCIAS: Si se provee una referencia laboral (nombre/teléfono) para un trabajo, agrégala como el ÚLTIMO punto de la lista de 'logros' de esa experiencia específica. Formato: "Referencia: Nombre - Contacto".
4. ORDEN: Cronológico descendente (más reciente primero) para experiencia y educación.
5. HABILIDADES: Mínimo 8 habilidades profesionales.
6. LOGROS: Mínimo 2 por experiencia profesional. Si el usuario no los brinda, genera tareas profesionales realistas (pero NO inventes fechas ni empresas).
7. IDIOMA: Si hay otros idiomas, incluye siempre 'Español – Nativo'.
8. FECHAS: Si no hay una fecha o rango temporal claro, deja el campo vacío (""). PROHIBIDO inventar meses o años.
    9. Devuelve ÚNICAMENTE el JSON.
    """
    
import mimetypes
import time

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file locally using pypdf."""
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

def upload_to_gemini(path: str, mime_type: str = None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    # print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def parse_cv_multimodal(file_paths: list[str]) -> Dict[str, Any]:
    """
    Sends multiple files (text, images, PDFs) to Gemini and returns structured JSON data.
    """
    if not API_KEY:
         raise ValueError("GEMINI_API_KEY environment variable not found.")

    model = genai.GenerativeModel('gemini-flash-latest') 
    
    content_parts = [SYSTEM_PROMPT, "\n\nINFORMACIÓN DEL USUARIO (Analiza todos los archivos adjuntos):"]
    
    # Process each file
    for path in file_paths:
        mime_type, _ = mimetypes.guess_type(path)
        
        # Determine if it's a file we should upload or read as text
        # Text files are better read directly to save upload overhead/complexity for simple text
        if mime_type and mime_type.startswith('text'):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                    content_parts.append(f"\n--- Archivo (Texto): {os.path.basename(path)} ---\n{text_content}")
            except Exception as e:
                print(f"Error reading text file {path}: {e}")
        elif mime_type == 'application/pdf':
            # Local extraction for PDF to avoid upload timeouts
            print(f"Extracting text from PDF locally: {os.path.basename(path)}...")
            pdf_text = extract_text_from_pdf(path)
            if pdf_text:
                content_parts.append(f"\n--- Archivo (PDF): {os.path.basename(path)} ---\n{pdf_text}")
            else:
                # Fallback to upload if extraction fails
                try:
                    print(f"Fallback: Uploading to Gemini: {os.path.basename(path)}...")
                    uploaded_file = upload_to_gemini(path, mime_type=mime_type)
                    content_parts.append(uploaded_file)
                except Exception as e:
                    print(f"Error uploading file {path}: {e}")
        else:
            # Upload binary files (Images)
            try:
                print(f"Uploading to Gemini: {os.path.basename(path)}...")
                uploaded_file = upload_to_gemini(path, mime_type=mime_type)
                content_parts.append(uploaded_file)
            except Exception as e:
                print(f"Error uploading file {path}: {e}")

    try:
        response = model.generate_content(
            contents=content_parts,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error parsing CV data with Gemini: {e}")
        raise e
