"""
Gestion des données : chargement, nettoyage, mappage et sauvegarde.
"""
import pandas as pd
import numpy as np
import os
from backend.config import COLUMN_MAPPING, REQUIRED_COLUMNS

def load_data(filepath):
    """Charge un fichier CSV ou Excel avec détection automatique de l'encodage."""
    if filepath.endswith('.csv'):
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                df = pd.read_csv(filepath, encoding=enc, sep=None, engine='python')
                return df
            except UnicodeDecodeError:
                continue
        raise ValueError("Impossible de lire le fichier CSV avec les encodages supportés.")
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Format de fichier non supporté. Utilisez CSV ou Excel.")

def map_columns(df):
    """Normalise les noms de colonnes selon la configuration."""
    df.columns = df.columns.str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.replace(' ', '_')
    
    rename_dict = {}
    for canonical_name, variants in COLUMN_MAPPING.items():
        for col in df.columns:
            if col in variants or col == canonical_name.lower():
                rename_dict[col] = canonical_name
                break
                
    df = df.rename(columns=rename_dict)
    return df

def clean_data(df):
    """Nettoie les données : conversion numérique, gestion des manquants, suppression des doublons."""
    numeric_cols = ['Age', 'Revenu_Mensuel', 'Anciennete_Emploi', 'Montant_Credit', 
                    'Duree_Credit', 'Taux_Interet', 'Mensualite', 'Nombre_Retards', 
                    'Incident_Paiement', 'Nombre_Demandes']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    if 'Defaut' in df.columns:
        df['Defaut'] = pd.to_numeric(df['Defaut'], errors='coerce').fillna(0).astype(int)
    if 'Sexe' in df.columns:
        df['Sexe'] = df['Sexe'].astype(str).str.strip()

    initial_len = len(df)
    df = df.drop_duplicates()
    
    for col in numeric_cols:
        if col in df.columns:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            
    return df

def save_data(df, filepath):
    """Sauvegarde le DataFrame dans un fichier CSV."""
    df.to_csv(filepath, index=False, encoding='utf-8')

def get_data_info():
    """Retourne les métadonnées du jeu de données actuel."""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'credit_bancaire.csv')
    if not os.path.exists(filepath):
        return {'exists': False, 'message': 'Aucune donnée chargée. Veuillez charger ou générer des données.'}
    
    df = load_data(filepath)
    return {
        'exists': True,
        'rows': len(df),
        'cols': len(df.columns),
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'preview': df.head(10).to_dict(orient='records')
    }