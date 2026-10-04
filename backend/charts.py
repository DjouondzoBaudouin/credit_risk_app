"""
Préparation des données pour l'affichage des graphiques côté frontend (Chart.js).
"""
import pandas as pd
import numpy as np

def get_dashboard_charts(df):
    """Prépare les données pour les graphiques du tableau de bord."""
    charts = {}
    
    # 1. Distribution des revenus (Histogramme simplifié)
    if 'Revenu_Mensuel' in df.columns:
        counts, bins = np.histogram(df['Revenu_Mensuel'].dropna(), bins=10)
        charts['revenu_dist'] = {
            'labels': [f"{int(bins[i]):,}" for i in range(len(bins)-1)],
            'data': counts.tolist()
        }
        
    # 2. Répartition Défaut vs Non-Défaut
    if 'Defaut' in df.columns:
        default_counts = df['Defaut'].value_counts().to_dict()
        charts['default_pie'] = {
            'labels': ['Fiable (0)', 'Risque (1)'],
            'data': [int(default_counts.get(0, 0)), int(default_counts.get(1, 0))]
        }
        
    # 3. Relation Revenu / Crédit (Scatter simplifié : moyennes par tranches)
    if 'Revenu_Mensuel' in df.columns and 'Montant_Credit' in df.columns:
        df['Revenu_Tranche'] = pd.cut(df['Revenu_Mensuel'], bins=5)
        scatter_data = df.groupby('Revenu_Tranche')['Montant_Credit'].mean().reset_index()
        charts['revenu_credit_scatter'] = {
            'labels': [str(idx).split(',')[0] + 'k' for idx in scatter_data['Revenu_Tranche']],
            'data': scatter_data['Montant_Credit'].round(0).tolist()
        }
        
    return charts