import sys
import os
import fitz # PyMuPDF
import base64
import uuid
from io import BytesIO
import tempfile
import subprocess
from typing import Optional, List

import shutil
from fastapi import FastAPI, Request, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import speech_recognition as sr
from gtts import gTTS
import imageio_ffmpeg
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.nlp_emotion import NLPProcessor
from src.llm_rag import RAGPipeline, LLMCompanion
from src.database import init_db, get_db, User, Conversation, Message
from src.auth import get_password_hash, verify_password, create_access_token, get_current_user

# Initialisation
init_db()
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp_processor = NLPProcessor()
rag = RAGPipeline("data/health_dataset.json")
companion = LLMCompanion(rag)

# Monter le dossier static pour servir l'interface web
# app.mount("/static", StaticFiles(directory="static"), name="static") # Désactivé pour la migration JavaFX

# S'assurer que le dossier temp existe
os.makedirs("temp", exist_ok=True)

# --- Models ---
class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str
    age: int
    password: str
    password_confirm: str
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    chronic_diseases: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    text: str
    language: str
    conversation_id: Optional[int] = None
    profile: Optional[dict] = None

# --- Auth Endpoints ---
@app.post("/api/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if user.password != user.password_confirm:
        raise HTTPException(status_code=400, detail="Les mots de passe ne correspondent pas.")
        
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà enregistré.")
        
    new_user = User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        age=user.age,
        hashed_password=get_password_hash(user.password),
        blood_type=user.blood_type,
        allergies=user.allergies,
        chronic_diseases=user.chronic_diseases
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur créé avec succès"}

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username' field for the login identifier (which will be the email)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        return {"logged_in": False}
    return {
        "logged_in": True, 
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": getattr(current_user, 'phone', 'N/A'),
        "age": getattr(current_user, 'age', 0),
        "blood_type": getattr(current_user, 'blood_type', 'NC'),
        "allergies": getattr(current_user, 'allergies', ''),
        "chronic_diseases": getattr(current_user, 'chronic_diseases', '')
    }

@app.put("/api/auth/profile")
def update_profile(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Non autorisé")
    
    try:
        if 'age' in data:
            current_user.age = int(data['age'])
        if 'phone' in data:
            current_user.phone = data['phone']
        if 'blood_type' in data:
            current_user.blood_type = data['blood_type']
        if 'allergies' in data:
            current_user.allergies = data['allergies']
        if 'chronic_diseases' in data:
            current_user.chronic_diseases = data['chronic_diseases']
            
        db.commit()
        return {"success": True, "message": "Profil mis à jour"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour : {str(e)}")

@app.get("/api/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Récupérer tous les messages de l'utilisateur pour les émotions
    messages = db.query(Message).join(Conversation).filter(Conversation.user_id == current_user.id).all()
    
    emotions = {"neutre": 0, "joie": 0, "stress": 0, "tristesse": 0, "confusion": 0}
    for m in messages:
        if m.emotion in emotions:
            emotions[m.emotion] += 1
            
    # Formater pour le frontend (Recharts)
    emotion_data = [
        {"name": "Stress", "value": emotions["stress"]},
        {"name": "Tristesse", "value": emotions["tristesse"]},
        {"name": "Joie", "value": emotions["joie"]},
        {"name": "Neutre", "value": emotions["neutre"]},
        {"name": "Confusion", "value": emotions["confusion"]}
    ]
    
    return {
        "emotion_data": emotion_data,
        "total_messages": len(messages)
    }

# --- Conversation Endpoints ---
@app.get("/api/conversations")
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return []
    return db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()).all()

@app.post("/api/conversations")
def create_conversation(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        return {"id": -1, "title": "Session d'essai"}
    new_conv = Conversation(user_id=current_user.id)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

@app.put("/api/conversations/{conv_id}")
def rename_conversation(conv_id: int, title: str = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or (current_user and conv.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    conv.title = title
    db.commit()
    return {"message": "Titre mis à jour"}

@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv or (current_user and conv.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Non autorisé")
    db.delete(conv)
    db.commit()
    return {"message": "Discussion supprimée"}

@app.get("/api/conversations/{conv_id}/messages")
def get_messages(conv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if conv_id != -1:
        conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Discussion non trouvée")
        # Check ownership
        if current_user and conv.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Non autorisé")
        return conv.messages
    return []

# --- Core Logic Endpoints ---
@app.get("/")
async def read_root():
    return {"status": "AI Backend Online", "client": "JavaFX-Ready"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cleaned_text = nlp_processor.clean_text(request.text)
    is_emergency = nlp_processor.detect_emergency(cleaned_text)
    emotion_detectee = nlp_processor.detect_emotion(cleaned_text)
    entities = nlp_processor.extract_entities(cleaned_text)

    if is_emergency:
        response_text = "🚨 URGENCE VITALE DÉTECTÉE : Veuillez appeler immédiatement le SAMU (190) ou la Protection Civile (198) en Tunisie." if request.language == "Français" else "🚨 CRITICAL EMERGENCY: Please call SAMU (190) or Civil Protection (198) in Tunisia immediately." if request.language == "English" else "🚨 حالة طوارئ حرجة: يرجى الاتصال بالإسعاف (190) أو الحماية المدنية (198) في تونس فوراً."
        return {"emergency": True, "response": response_text}

    # Fetch history if conversation_id provided
    history = []
    if request.conversation_id and request.conversation_id != -1:
        db_messages = db.query(Message).filter(Message.conversation_id == request.conversation_id).order_by(Message.created_at.asc()).all()
        history = [{"role": m.role, "content": m.content} for m in db_messages]

    # Génération LLM
    try:
        response_text = companion.get_response(cleaned_text, emotion_detectee, request.profile, request.language, history, entities)
    except Exception as e:
        print(f"Erreur LLM: {e}")
        return {"emergency": False, "response": "Désolé, j'ai rencontré un problème pour générer une réponse. Vérifiez votre connexion internet.", "error": str(e)}
    
    # Save to DB if authenticated and in a conversation
    if request.conversation_id and request.conversation_id != -1 and current_user:
        # Save user message
        new_msg = Message(conversation_id=request.conversation_id, role="user", content=request.text, emotion=emotion_detectee)
        db.add(new_msg)
        
        # Save bot response
        bot_msg = Message(conversation_id=request.conversation_id, role="bot", content=response_text)
        db.add(bot_msg)
        # Auto-update title if it's the first message
        conv = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if conv and conv.title == "Nouvelle discussion":
            conv.title = (request.text[:30] + '...') if len(request.text) > 30 else request.text
        
        db.commit()

    # TTS
    gtts_lang = "fr" if request.language == "Français" else "en" if request.language == "English" else "ar"
    try:
        tts = gTTS(text=response_text, lang=gtts_lang, slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        audio_base64 = base64.b64encode(fp.getvalue()).decode('utf-8')
    except Exception:
        audio_base64 = None

    return {
        "emergency": False,
        "emotion": emotion_detectee,
        "response": response_text,
        "audio": audio_base64,
        "conversation_id": request.conversation_id
    }


@app.post("/api/audio")
async def transcribe_audio(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    try:
        # Sauvegarde temporaire du fichier
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Utilisation de Groq Whisper pour la transcription
        with open(temp_filename, "rb") as audio_file:
            transcription = companion.client.audio.transcriptions.create(
                file=(temp_filename, audio_file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        
        os.remove(temp_filename)
        return {"text": transcription}
    except Exception as e:
        print(f"Erreur transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...), language: str = Form(...), current_user: User = Depends(get_current_user)):
    try:
        contents = await file.read()
        
        # Gestion du PDF : Texte + Image
        pdf_text = ""
        if file.filename.lower().endswith('.pdf'):
            try:
                print(f"DEBUG: Traitement du PDF {file.filename}...")
                pdf_doc = fitz.open(stream=contents, filetype="pdf")
                # 1. Extraire le texte s'il existe
                for page in pdf_doc:
                    pdf_text += page.get_text()
                
                # 2. Convertir la première page en image haute qualité
                page = pdf_doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                contents = pix.tobytes("jpeg")
                pdf_doc.close()
                print(f"DEBUG: Texte extrait ({len(pdf_text)} chars).")
            except Exception as pdf_err:
                print(f"DEBUG PDF ERROR: {pdf_err}")

        base64_image = base64.b64encode(contents).decode('utf-8')
        
        full_prompt = (
            f"Vous êtes un assistant médical expert. Répondez en {language}.\n"
            "Analysez ce document médical (image et texte extrait).\n"
        )
        if pdf_text:
            full_prompt += f"Texte extrait du document : \n{pdf_text[:2000]}\n"
        
        full_prompt += "Expliquez le contenu de manière simple, empathique et rassurante."

        chat_completion = companion.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        
        analysis = chat_completion.choices[0].message.content
        return {"analysis": analysis}
    except Exception as e:
        detailed_error = f"Détails : {str(e)}"
        print(f"Erreur Vision: {detailed_error}")
        return {"analysis": f"Désolé, l'analyse a échoué. {detailed_error}"}

if __name__ == "__main__":
    import uvicorn
    print("Démarrage du serveur sur http://localhost:8000 ...")
    uvicorn.run(app, host="0.0.0.0", port=8000)


