#!/usr/bin/env python3
"""
Script de migration de la base de données pour ajouter les colonnes bpm, ir, ecg
"""
import sqlite3
import os

PROJECT_ROOT = os.path.dirname(__file__)
DB_FILENAME = os.path.join(PROJECT_ROOT, 'esp32_data.db')

def migrate():
    print(f"Migration de la base de données: {DB_FILENAME}")
    
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    
    # Vérifier si les colonnes existent déjà
    cur.execute("PRAGMA table_info(sensor_data)")
    columns = [col[1] for col in cur.fetchall()]
    
    print(f"Colonnes actuelles: {columns}")
    
    # Ajouter les nouvelles colonnes si elles n'existent pas
    if 'bpm' not in columns:
        print("  → Ajout de la colonne 'bpm'")
        cur.execute("ALTER TABLE sensor_data ADD COLUMN bpm REAL")
    
    if 'ir' not in columns:
        print("  → Ajout de la colonne 'ir'")
        cur.execute("ALTER TABLE sensor_data ADD COLUMN ir INTEGER")
    
    if 'ecg' not in columns:
        print("  → Ajout de la colonne 'ecg'")
        cur.execute("ALTER TABLE sensor_data ADD COLUMN ecg INTEGER")
    
    conn.commit()
    
    # Vérifier les colonnes finales
    cur.execute("PRAGMA table_info(sensor_data)")
    columns = [col[1] for col in cur.fetchall()]
    print(f"Colonnes après migration: {columns}")
    
    conn.close()
    print("✓ Migration terminée !")

if __name__ == '__main__':
    migrate()
