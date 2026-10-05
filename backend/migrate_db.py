import pymysql
from sqlalchemy import create_engine, text

# URL de la base de données (à adapter si nécessaire)
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/health_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # On ajoute les colonnes une par une si elles n'existent pas
    cols = [
        ("blood_type", "VARCHAR(10)"),
        ("allergies", "TEXT"),
        ("chronic_diseases", "TEXT")
    ]
    
    for col_name, col_type in cols:
        try:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
            print(f"Colonne {col_name} ajoutée.")
        except Exception as e:
            print(f"Colonne {col_name} probablement déjà existante ou erreur: {e}")
    
    conn.commit()
    print("Migration terminée.")
