import re
# from transformers import pipeline

class NLPProcessor:
    def __init__(self):
        # Initialiser le modèle d'émotion (commenté pour éviter le téléchargement lourd immédiat)
        # self.emotion_classifier = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
        pass

    def clean_text(self, text):
        """Nettoie le texte en enlevant les caractères spéciaux."""
        text = re.sub(r'[^\w\s]', '', text)
        return text.lower().strip()

    def detect_emergency(self, text):
        """
        Détecte une urgence vitale critique nécessitant un arrêt immédiat du chatbot.
        """
        text_lower = text.lower()
        # Français, Anglais, Arabe (phonétique et standard)
        critical_keywords = [
            'poitrine', 'sang', 'infarctus', 'suicide', 'mourir', 'étouffe', 'crise cardiaque', 'bras gauche', 'vomis', 'avaler',
            'chest', 'blood', 'heart attack', 'die', 'choking', 'left arm', 'vomit', 'swallow',
            'mot', 'mout', 'dam', '9alb', 'sadri', 'intihar', 'nmut', 'sbitar', 'urgences',
            'صدر', 'دم', 'نوبة قلبية', 'انتحار', 'موت', 'أختنق', 'جلطة', 'ذراع أيسر', 'نزيف', 'إسعاف'
        ]
        
        import re
        for word in critical_keywords:
            # On utilise \b pour les mots en caractères latins
            # Pour l'arabe, on vérifie simplement la présence car \b peut varier selon les OS/Python
            if re.search(rf"\b{re.escape(word)}\b", text_lower, re.IGNORECASE):
                return True
        return False

    def extract_entities(self, text):
        """
        Extraction d'Information (NER) : Identifie les symptômes et médicaments.
        """
        text_lower = text.lower()
        entities = {
            "symptoms": [],
            "medications": [],
            "organs": []
        }
        
        # Dictionnaires de patterns (regex)
        symptoms_patterns = {
            "fièvre": r"(fi[èe]vre|temp[ée]rature|skhana|fever)",
            "douleur": r"(douleur|mal|wji3a|pain|ache)",
            "toux": r"(toux|koha|cough)",
            "fatigue": r"(fatigue|fachal|tired|exhausted)",
            "étourdissement": r"(vertige|douwa|dizzy|giddy)"
        }
        
        medications_patterns = {
            "paracétamol": r"(parac[ée]tamol|doliprane|panadol|efferalgan)",
            "antibiotique": r"(antibio|amoxicilline|augmentin)",
            "insuline": r"(insuline|insulin)"
        }
        
        organs_patterns = {
            "cœur": r"(cœur|9alb|heart)",
            "estomac": r"(estomac|m[ée]da|stomach|belly)",
            "tête": r"(tête|ras|head)"
        }
        
        for name, pattern in symptoms_patterns.items():
            if re.search(pattern, text_lower): entities["symptoms"].append(name)
        for name, pattern in medications_patterns.items():
            if re.search(pattern, text_lower): entities["medications"].append(name)
        for name, pattern in organs_patterns.items():
            if re.search(pattern, text_lower): entities["organs"].append(name)
            
        return entities

    def summarize_text(self, text, max_words=15):
        """
        Résumé automatique : Extrait les points clés si le texte est long.
        """
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."

    def detect_emotion(self, text):
        """
        Détecte l'émotion de l'utilisateur avec support multilingue.
        """
        text_lower = text.lower()
        
        # Français, Anglais, Arabe/Derja
        stress_keywords = ['douleur', 'mal', 'panique', 'stress', 'urgent', 'cœur', 'respire', 'peur', 'angoisse', 'grave',
                           'pain', 'hurt', 'panic', 'urgent', 'heart', 'breathe', 'fear', 'anxious', 'serious', 'ache', 'stomach',
                           'wji3a', '5ayef', '5ayfa', 'mridh', 'te3eb', 'nefja3', 'ألم', 'وجع', 'خوف', 'قلق', 'طوارئ', 'قلب', 'مريض', 'أشعر بألم']
        
        confusion_keywords = ['comprends pas', 'comment', 'ordonnance', 'posologie', 'perdu', 'expliquer', 'signifie',
                              'understand', 'how', 'prescription', 'dosage', 'lost', 'explain', 'mean', 'confused',
                              'mafhemtech', 'kifech', 'dwe', 'tbib', 'fasarli', 'كيف', 'ماذا', 'لم أفهم', 'شرح', 'ضياع']
                              
        joy_keywords = ['super', 'génial', 'parfait', 'merci', 'soulagé', 'rassuré', 'bon', 'heureux', 'heureuse', 'content', 'contente', 'bien', 'mieux',
                        'great', 'awesome', 'perfect', 'thanks', 'thank you', 'relieved', 'good', 'happy', 'better',
                        'behi', 'merci', 'chokran', 'ya3tik saha', 'cv', 'labes', 'farhan', 'farhana', 'شكرا', 'سعيد', 'فرح', 'ممتاز', 'جيد']
                        
        tristesse_keywords = ['triste', 'déprimé', 'pleurer', 'seul', 'fatigué', 'insurmontable', 'énergie', 'désespoir', 'malheur', 'pleur',
                              'sad', 'depressed', 'cry', 'alone', 'tired', 'hopeless', 'energy', 'overwhelmed',
                              'hzina', 'hzin', 'fachel', 'fachela', 'nebki', 'wahdi', 'tayeh', 'حزين', 'اكتئاب', 'يأس', 'تعبان', 'وحيد', 'أبكي']
        
        if any(word in text_lower for word in stress_keywords):
            return "stress"
        elif any(word in text_lower for word in tristesse_keywords):
            return "tristesse"
        elif any(word in text_lower for word in confusion_keywords):
            return "confusion"
        elif any(word in text_lower for word in joy_keywords):
            return "joie"
        else:
            return "neutre"

if __name__ == "__main__":
    # Test simple
    processor = NLPProcessor()
    test_text = "Mon vol est annulé, je suis en panique totale !"
    cleaned = processor.clean_text(test_text)
    emotion = processor.detect_emotion(test_text)
    print(f"Texte: {test_text}")
    print(f"Nettoyé: {cleaned}")
    print(f"Émotion détectée: {emotion}")
