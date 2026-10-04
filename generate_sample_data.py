"""
Générateur de données simulées réalistes pour l'analyse de risque de crédit.
"""
import pandas as pd
import numpy as np
import os

def generate_sample_dataset(n_clients=500):
    """Génère un jeu de données de n_clients et le sauvegarde dans le dossier data/."""
    np.random.seed(42)
    
    # 1. Variables de base
    age = np.random.normal(45, 12, n_clients).astype(int)
    age = np.clip(age, 22, 65)
    
    sexe = np.random.choice(['M', 'F'], n_clients, p=[0.52, 0.48])
    
    # Revenu mensuel en FCFA (Normale tronquée)
    revenu = np.random.normal(500000, 150000, n_clients)
    revenu = np.clip(revenu, 150000, 2000000).astype(int)
    
    # Ancienneté emploi (années)
    anciennete = np.random.exponential(5, n_clients).astype(int)
    anciennete = np.clip(anciennete, 0, 40)
    
    # 2. Variables dérivées (corrélées)
    # Le montant du crédit dépend du revenu et de l'ancienneté
    montant_credit = (revenu * np.random.uniform(5, 15, n_clients) + anciennete * 100000).astype(int)
    montant_credit = np.clip(montant_credit, 500000, 50000000)
    
    duree_credit = np.random.choice([12, 24, 36, 48, 60], n_clients, p=[0.1, 0.2, 0.3, 0.25, 0.15])
    
    taux_interet = np.random.normal(6.5, 1.5, n_clients)
    taux_interet = np.clip(taux_interet, 3.0, 15.0).round(2)
    
    # Mensualité approximative (formule simplifiée)
    taux_mensuel = taux_interet / 100 / 12
    mensualite = (montant_credit * taux_mensuel * (1 + taux_mensuel)**duree_credit) / ((1 + taux_mensuel)**duree_credit - 1)
    mensualite = mensualite.astype(int)
    
    # 3. Variables de risque
    # Nombre de retards influencé par le revenu et l'ancienneté
    score_risque = (1000000 / revenu) * 2 + (10 - anciennete) * 0.5
    nombre_retards = np.random.poisson(score_risque, n_clients)
    nombre_retards = np.clip(nombre_retards, 0, 10)
    
    # Incidents de paiement (Poisson)
    incident_paiement = np.random.poisson(0.8, n_clients)
    incident_paiement = np.clip(incident_paiement, 0, 5)
    
    # Nombre de demandes
    nombre_demandes = np.random.poisson(1.5, n_clients)
    nombre_demandes = np.clip(nombre_demandes, 1, 5)
    
    # 4. Variable cible : Défaut (Logistique)
    # Probabilité de défaut basée sur les retards, le ratio crédit/revenu et les incidents
    prob_defaut = 1 / (1 + np.exp(-(-4 + 0.3 * nombre_retards + 0.000002 * (montant_credit/revenu) + 0.5 * incident_paiement)))
    defaut = np.random.binomial(1, prob_defaut, n_clients)
    
    # Création du DataFrame
    df = pd.DataFrame({
        'ID_Client': [f'CLI_{i:04d}' for i in range(1, n_clients + 1)],
        'Age': age,
        'Sexe': sexe,
        'Revenu_Mensuel': revenu,
        'Anciennete_Emploi': anciennete,
        'Montant_Credit': montant_credit,
        'Duree_Credit': duree_credit,
        'Taux_Interet': taux_interet,
        'Mensualite': mensualite,
        'Nombre_Retards': nombre_retards,
        'Incident_Paiement': incident_paiement,
        'Nombre_Demandes': nombre_demandes,
        'Defaut': defaut
    })
    
    # Sauvegarde
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, 'credit_bancaire_sample.csv')
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    # Copie vers le fichier actif
    active_filepath = os.path.join(data_dir, 'credit_bancaire.csv')
    df.to_csv(active_filepath, index=False, encoding='utf-8')
    
    print(f"Données générées avec succès : {n_clients} lignes sauvegardées dans {filepath}")
    return filepath

if __name__ == '__main__':
    generate_sample_dataset()