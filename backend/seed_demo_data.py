import sys
import os
from datetime import datetime, timedelta

# Ajouter src au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import SessionLocal, User, Conversation, Message, init_db
from src.auth import get_password_hash

def seed_data():
    db = SessionLocal()
    init_db()
    
    print("Nettoyage des anciennes donnees de demo...")
    db.query(User).filter(User.email == "sami@demo.tn").delete()
    db.commit()

    print("Creation de l'utilisateur Sami (Demo)...")
    hashed_pwd = get_password_hash("password123")
    user = User(
        email="sami@demo.tn",
        first_name="Sami",
        last_name="Ben Ali",
        phone="98 123 456",
        age=45,
        hashed_password=hashed_pwd,
        blood_type="O+",
        allergies="Pollen, Penicilline",
        chronic_diseases="Hypertension legere"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # --- Conversation 1 : Nutrition ---
    conv1 = Conversation(user_id=user.id, title="Conseils Nutrition & Sport", created_at=datetime.utcnow() - timedelta(days=2))
    db.add(conv1)
    db.commit()
    db.refresh(conv1)

    m1 = [
        Message(conversation_id=conv1.id, role="user", content="Je veux commencer un regime, que me conseilles-tu ?", emotion="neutre"),
        Message(conversation_id=conv1.id, role="bot", content="C'est une excellente initiative Sami ! Privilegiez les legumes et les proteines maigres."),
        Message(conversation_id=conv1.id, role="user", content="Merci, je me sens deja plus motive !", emotion="joie"),
        Message(conversation_id=conv1.id, role="bot", content="Bravo ! La motivation est la cle du succes.")
    ]
    db.add_all(m1)

    # --- Conversation 2 : Stress ---
    conv2 = Conversation(user_id=user.id, title="Suivi Hypertension", created_at=datetime.utcnow() - timedelta(hours=5))
    db.add(conv2)
    db.commit()
    db.refresh(conv2)

    m2 = [
        Message(conversation_id=conv2.id, role="user", content="Ma tension est a 15/9 ce matin, je m'inquiete.", emotion="stress"),
        Message(conversation_id=conv2.id, role="bot", content="Restez calme Sami. 15/9 est un peu eleve. Reposez-vous 15 minutes et reprenez-la."),
        Message(conversation_id=conv2.id, role="user", content="D'accord, je vais essayer de respirer doucement.", emotion="stress"),
        Message(conversation_id=conv2.id, role="bot", content="C'est la bonne approche. Je reste la si vous avez besoin.")
    ]
    db.add_all(m2)

    # --- Conversation 3 : Confusion ---
    conv3 = Conversation(user_id=user.id, title="Question Ordonnance", created_at=datetime.utcnow() - timedelta(minutes=30))
    db.add(conv3)
    db.commit()
    db.refresh(conv3)

    m3 = [
        Message(conversation_id=conv3.id, role="user", content="Je ne comprends pas quand prendre mon medicament.", emotion="confusion"),
        Message(conversation_id=conv3.id, role="bot", content="D'apres les standards, ce type de traitement se prend generalement le matin a jeun."),
        Message(conversation_id=conv3.id, role="user", content="Ah d'accord, merci pour l'explication.", emotion="neutre")
    ]
    db.add_all(m3)

    db.commit()
    print("\nSUCCES : Donnees de demo injectees !")
    print(f"Login : sami@demo.tn")
    print(f"Password : password123")
    db.close()

if __name__ == "__main__":
    seed_data()
