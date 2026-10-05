from src.nlp_emotion import NLPProcessor

processor = NLPProcessor()
text = "J'ai pris du Doliprane pour ma fièvre et j'ai mal à l'estomac."

print(f"Texte: {text}")
print(f"Émotion: {processor.detect_emotion(text)}")
entities = processor.extract_entities(text)
print(f"Entités: {entities}")
print(f"Résumé: {processor.summarize_text(text, 5)}")
