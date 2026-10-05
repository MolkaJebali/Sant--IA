import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Ajouter le chemin pour trouver src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import Base, DATABASE_URL

print(f"Connexion à la base de données : {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

try:
    # Suppression des tables existantes pour repartir à neuf
    print("Suppression des anciennes tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Création des nouvelles tables avec les nouveaux champs
    print("Création des nouvelles tables...")
    Base.metadata.create_all(bind=engine)
    
    print("SUCCÈS : La base de données a été réinitialisée avec les nouveaux champs !")
except Exception as e:
    print(f"ERREUR lors de la réinitialisation : {e}")
