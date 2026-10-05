import sys
import os
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nlp_emotion import NLPProcessor
from src.llm_rag import RAGPipeline, LLMCompanion

def test_nlp():
    print("\n--- TEST NLP ---")
    nlp = NLPProcessor()
    
    # Test Emergency
    emergency_text = "J'ai une douleur atroce dans la poitrine et mon bras gauche est engourdi"
    is_emergency = nlp.detect_emergency(emergency_text)
    print(f"Urgence détectée (FR): {is_emergency} (Attendu: True)")
    
    # Test Emotion
    sad_text = "Je me sens vraiment seul et fatigué de tout ça..."
    emotion = nlp.detect_emotion(sad_text)
    print(f"Émotion détectée: {emotion} (Attendu: tristesse)")
    
    stress_text = "i am so stressed about my results help me"
    emotion_en = nlp.detect_emotion(stress_text)
    print(f"Émotion détectée (EN): {emotion_en} (Attendu: stress)")

    # Test Entities (NER)
    ner_text = "J'ai pris du doliprane pour ma fièvre"
    entities = nlp.extract_entities(ner_text)
    print(f"Entités détectées: {entities}")

def test_rag():
    print("\n--- TEST RAG (100 Entités) ---")
    rag = RAGPipeline("data/health_dataset.json")
    
    # Test retrieval
    query = "Comment soigner la grippe ?"
    context = rag.retrieve_context(query)
    print(f"Contexte trouvé pour 'grippe': {context[:100]}...")
    
    # Test retrieval Arabic
    query_ar = "كيفية علاج السكري"
    context_ar = rag.retrieve_context(query_ar)
    print(f"Contexte trouvé pour 'السكري': {context_ar[:100]}...")

def test_empathy_and_llm():
    print("\n--- TEST EMPATHIE & LLM ---")
    rag = RAGPipeline("data/health_dataset.json")
    companion = LLMCompanion(rag)
    
    # Simuler un utilisateur stressé
    query = "Je panique, j'ai mal au ventre"
    emotion = "stress"
    language = "Français"
    
    prompt = companion.generate_prompt(query, emotion, "Contexte: Douleur abdominale", None, language)
    print("Prompt généré (Vérifier les consignes d'empathie) :")
    print(prompt[:300] + "...")
    
    # Si la clé API est présente, on peut tester une réponse réelle
    if os.getenv("GROQ_API_KEY"):
        print("\nTest de réponse réelle via Groq...")
        response = companion.get_response(query, emotion, language=language)
        print(f"Réponse IA: {response}")
    else:
        print("\n(Clé API manquante dans l'environnement de test, simulation ignorée)")

def verify_files():
    print("\n--- VERIFICATION DES FICHIERS ---")
    paths = [
        "frontend/public/avatars/neutral.png",
        "frontend/public/avatars/stress.png",
        "frontend/public/avatars/sadness.png",
        "frontend/public/avatars/confusion.png",
        "data/health_dataset.json"
    ]
    for p in paths:
        exists = os.path.exists(p)
        print(f"Fichier {p}: {'OK' if exists else 'MANQUANT'}")

if __name__ == "__main__":
    try:
        test_nlp()
        test_rag()
        test_empathy_and_llm()
        verify_files()
        print("\n--- TOUS LES TESTS LOGIQUES SONT TERMINÉS ---")
    except Exception as e:
        print(f"\nERREUR DURANT LES TESTS: {e}")
