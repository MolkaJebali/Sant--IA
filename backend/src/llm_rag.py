import json
import os
from groq import Groq
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Remplacement de langchain.schema.Document par une classe personnalisée pour le prototype
class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

class RAGPipeline:
    def __init__(self, data_path="data/health_dataset.json"):
        self.data_path = data_path
        self.documents = []
        self.vectorstore = None
        self.setup()

    def load_data(self):
        """Charge les données JSON et les convertit en documents LangChain."""
        if not os.path.exists(self.data_path):
            print(f"Fichier non trouvé: {self.data_path}")
            return
            
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            doc = Document(
                page_content=item['content'],
                metadata={"type": item.get('type', ''), "tags": ",".join(item.get('tags', []))}
            )
            self.documents.append(doc)
            
    def setup_vectorstore(self):
        """Initialise la base de données vectorielle (Chroma) avec les embeddings HuggingFace."""
        # Commenté pour éviter le téléchargement d'embeddings lourds pour le moment
        # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # self.vectorstore = Chroma.from_documents(documents=self.documents, embedding=embeddings)
        pass

    def setup(self):
        self.load_data()
        self.setup_vectorstore()

    def retrieve_context(self, query, k=2):
        """Récupère le contexte le plus pertinent pour la requête."""
        if self.vectorstore:
            # docs = self.vectorstore.similarity_search(query, k=k)
            # return "\n".join([doc.page_content for doc in docs])
            pass
        
        # Fallback pour le prototype sans Chroma : recherche par mots-clés
        stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'd', 'l', 'je', 'tu', 'il', 'nous', 'vous', 'ils', 'et', 'ou', 'est', 'sont', 'a', 'à', 'pour', 'dans', 'sur', 'ce', 'qui', 'que', 'quoi', 'mon', 'ma', 'mes'}
        
        # Nettoyage plus robuste pour le RAG
        import re
        query_clean = re.sub(r'[^\w\s]', ' ', query.lower())
        query_words = [w for w in query_clean.split() if w not in stop_words and len(w) > 2]
        
        scored_docs = []
        for doc in self.documents:
            search_area = (doc.page_content + " " + " ".join(doc.metadata.get("tags", []))).lower()
            # Calcul du score : combien de mots de la requête sont dans le document
            score = sum(1 for word in query_words if word in search_area)
            
            if score > 0:
                scored_docs.append((score, doc.page_content))
                
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        # Retourner les meilleurs résultats
        context_docs = [doc for score, doc in scored_docs]
        return "\n\n".join(context_docs[:k]) if context_docs else ""

class LLMCompanion:
    def __init__(self, rag_pipeline):
        self.rag = rag_pipeline
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        
    def generate_prompt(self, user_query, emotion, context, user_profile=None, language="Français", history=None, entities=None):
        """Génère un prompt adapté à l'émotion détectée, à la langue et à l'historique."""
        user_name = user_profile.get('first_name', 'Utilisateur') if user_profile else 'Utilisateur'
        
        system_prompt = (
            f"Vous êtes un assistant santé expert, chaleureux et empathique. Votre objectif est d'aider {user_name}.\n"
            f"CONSIGNE DE PERSONNALISATION : Adressez-vous à {user_name} de manière naturelle. Soyez très empathique et bienveillant.\n"
            f"CONSIGNE DE RIGUEUR : Ne parlez QUE des faits mentionnés par l'utilisateur. N'inventez JAMAIS de résultats médicaux.\n"
            f"LOCALISATION : Vous connaissez les numéros d'urgence de la Tunisie (SAMU: 190, Protection Civile: 198, Police: 197).\n"
            f"Vous devez répondre STRICTEMENT en {language}.\n"
        )
        
        if emotion == "stress":
            system_prompt += f"L'utilisateur ({user_name}) semble stressé. Rassurez-le calmement et rappelez-lui de respirer. Si c'est grave, orientez vers le 190 (Tunisie).\n"
        elif emotion == "tristesse":
            system_prompt += f"{user_name} semble triste. Faites preuve d'une grande compassion, validez ses émotions et soyez réconfortant.\n"
        elif emotion == "confusion":
            system_prompt += "L'utilisateur est confus. Expliquez les concepts de manière simple et rassurante.\n"
        elif emotion == "joie":
            system_prompt += f"Partagez la joie ou le soulagement de {user_name} avec enthousiasme.\n"
            
        entity_context = ""
        if entities:
            if entities.get("symptoms"):
                entity_context += f"- Symptômes détectés : {', '.join(entities['symptoms'])}\n"
            if entities.get("medications"):
                entity_context += f"- Médicaments mentionnés : {', '.join(entities['medications'])}\n"
            if entity_context:
                entity_context = "\nAnalyse NLP (Entités extraites) :\n" + entity_context

        profile_text = ""
        if user_profile:
            profile_text = "Profil Patient:\n"
            if user_profile.get("name"):
                profile_text += f"- Nom: {user_profile['name']}\n"
            if user_profile.get("age"):
                profile_text += f"- Âge: {user_profile['age']}\n"
            if user_profile.get("conditions"):
                profile_text += f"- Antécédents / Maladies chroniques: {user_profile['conditions']}\n"
            profile_text += "\nVeillez à personnaliser la réponse en fonction de ce profil.\n\n"

        history_text = ""
        if history:
            history_text = "Historique récent de la conversation :\n"
            for msg in history[-5:]: # On garde les 5 derniers messages pour le contexte
                role = "Assistant" if msg['role'] == 'bot' else "Utilisateur"
                history_text += f"{role}: {msg['content']}\n"
            history_text += "\n"

        prompt = f"""{system_prompt}
        {entity_context}
        {profile_text}{history_text}Contexte médical pertinent :
        {context}
        
        Question actuelle de l'utilisateur : {user_query}
        
        Réponse en {language} :"""
        return prompt

    def get_response(self, user_query, emotion, user_profile=None, language="Français", history=None, entities=None):
        """Génère la réponse finale en tenant compte de l'historique."""
        # Si une émotion forte est détectée sans question complexe, on privilégie l'empathie
        if emotion != "neutre" and len(user_query.split()) < 4:
            context = "" # Pas besoin de RAG pour un "je suis heureux"
        else:
            context = self.rag.retrieve_context(user_query)
        
        if not context:
            if language == "English":
                context = "I couldn't find specific medical information about this in my knowledge base."
            elif language == "العربية":
                context = "لم أتمكن من العثور على معلومات طبية محددة حول هذا الموضوع في قاعدة بياناتي."
            else:
                context = "Je n'ai pas d'informations médicales précises sur ce sujet dans ma base de connaissances."
                
        prompt = self.generate_prompt(user_query, emotion, context, user_profile, language, history, entities)
        
        # SI UNE CLÉ API EST PRÉSENTE, ON UTILISE LE VRAI LLM (GROK)
        if self.client:
            try:
                # On peut passer l'historique directement dans les messages si on veut être plus "natif" LLM
                messages = [{"role": "system", "content": "You are a helpful and empathetic health assistant."}]
                if history:
                    for msg in history[-5:]:
                        role = "assistant" if msg['role'] == 'bot' else "user"
                        messages.append({"role": role, "content": msg['content']})
                messages.append({"role": "user", "content": prompt})

                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                )
                return response.choices[0].message.content

            except Exception as e:
                print(f"Erreur API Groq: {e}. Passage au mode simulation.")
        
        # Simulation du rôle du LLM : Traduire et adapter le contexte dans la langue demandée
        if language == "English" and context != "I couldn't find specific medical information about this in my knowledge base.":
            if "douleur aiguë" in context:
                context = "In case of acute or severe stomach pain, especially if sudden, persistent, or accompanied by vomiting, fever, or difficulty breathing, it is urgent to consult a doctor or go to the emergency room. For mild stomach aches, eat light meals, drink water, and avoid spicy foods."
            elif "téléconsultation" in context:
                context = "Teleconsultation allows for a quick medical opinion. If symptoms persist, contact emergency services."
            elif "diabète" in context:
                context = "Diabetes is a chronic disease characterized by excess sugar in the blood. It is crucial to monitor your blood sugar regularly, eat a balanced diet, and exercise."
        elif language == "العربية" and context != "لم أتمكن من العثور على معلومات طبية محددة حول هذا الموضوع في قاعدة بياناتي.":
            if "douleur aiguë" in context:
                context = "في حالة ألم المعدة الحاد أو الشديد، خاصة إذا كان مفاجئاً، مستمراً، أو مصحوباً بقيء، حمى، أو صعوبة في التنفس، يجب استشارة الطبيب أو الذهاب إلى الطوارئ فوراً. بالنسبة لآلام المعدة الخفيفة، تناول وجبات خفيفة، اشرب الماء وتجنب الأطعمة الحارة أو الدهنية."
            elif "téléconsultation" in context:
                context = "تتيح الاستشارة الطبية عن بعد الحصول على رأي طبي سريع. إذا استمرت الأعراض، اتصل بخدمات الطوارئ."
            elif "diabète" in context:
                context = "مرض السكري هو مرض مزمن يتميز بزيادة السكر في الدم. من المهم مراقبة نسبة السكر في الدم بانتظام، واتباع نظام غذائي متوازن، وممارسة الرياضة."
        
        # Prototype: réponses simulées traduites basiquement pour la démo
        # Dans un vrai système, on utiliserait le LLM via self.llm(prompt)
        if language == "English":
            if emotion == "stress":
                return f"I completely understand your concern. Breathe, we will figure this out. Based on my info:\n\n{context}\n\nPlease don't worry."
            elif emotion == "tristesse":
                return f"I am so sorry you are feeling this way. It's completely understandable to feel overwhelmed. Please know you are not alone. Here is some guidance:\n\n{context}\n\nI'm here for you."
            elif emotion == "confusion":
                return f"It's normal to feel a bit lost. Let me explain simply:\n\n{context}\n\nHope that helps!"
            elif emotion == "joie":
                return "That's wonderful news! I am so happy and relieved for you. Keep taking good care of yourself!"
            else:
                return f"I hear you. Here is the information I found:\n\n{context}\n\nLet me know if you need more details."
        elif language == "العربية":
            if emotion == "stress":
                return f"أنا أتفهم قلقك تماما. تنفس، سنجد حلا. بناء على معلوماتي:\n\n{context}\n\nلا تقلق."
            elif emotion == "tristesse":
                return f"أنا آسف جدا لأنك تشعر هكذا. من المفهوم تماما أن تشعر بالإرهاق. تذكر أنك لست وحدك. إليك بعض التوجيهات:\n\n{context}\n\nأنا هنا من أجلك."
            elif emotion == "confusion":
                return f"من الطبيعي أن تشعر بالضياع قليلاً. دعني أشرح لك ببساطة:\n\n{context}\n\nأتمنى أن يكون هذا أوضح!"
            elif emotion == "joie":
                return "هذه أخبار رائعة! أنا سعيد جداً ومنتشي لأجلك. استمر في الاعتناء بنفسك جيداً!"
            else:
                return f"إليك المعلومات التي وجدتها:\n\n{context}\n\nلا تتردد في التحدث إلي إذا احتجت إلى ذلك."
        else: # Français par défaut
            if emotion == "stress":
                return f"Je comprends tout à fait votre inquiétude. Respirez, nous allons trouver une solution. D'après mes informations :\n\n{context}\n\nNe vous inquiétez pas."
            elif emotion == "tristesse":
                return f"Je suis vraiment désolé d'entendre que vous traversez une période si difficile. C'est tout à fait normal de se sentir épuisé ou dépassé. Sachez que vous n'êtes pas seul(e). Voici quelques éléments :\n\n{context}\n\nJe suis là pour vous."
            elif emotion == "confusion":
                return f"C'est normal de se sentir un peu perdu. Laissez-moi vous expliquer simplement :\n\n{context}\n\nJ'espère que c'est plus clair !"
            elif emotion == "joie":
                return "C'est une excellente nouvelle ! Je suis ravi et soulagé pour vous. Continuez à bien prendre soin de vous !"
            else:
                return f"Voici les informations que j'ai trouvées à ce sujet :\n\n{context}\n\nN'hésitez pas si vous avez d'autres questions."

if __name__ == "__main__":
    rag = RAGPipeline("../data/tourism_dataset.json")
    companion = LLMCompanion(rag)
    
    query = "Mon vol est annulé, aidez-moi !"
    emotion = "stress"
    
    print("Test LLM Companion:")
    print(companion.get_response(query, emotion))
