"""
Configuration et mappage des colonnes pour l'application.
Permet de détecter des noms de colonnes variants et de les normaliser.
"""

# Dictionnaire de mappage : {nom_normalisé: [liste_des_variantes_acceptees]}
COLUMN_MAPPING = {
    'ID_Client': ['id', 'id_client', 'client_id', 'identifiant'],
    'Age': ['age', 'âge', 'client_age'],
    'Sexe': ['sexe', 'genre', 'gender', 'sex'],
    'Revenu_Mensuel': ['revenu', 'rev', 'revenu_mensuel', 'revenu mensuel', 'salaire', 'income'],
    'Anciennete_Emploi': ['anciennete', 'ancienneté', 'anciennete_emploi', 'years_employed', 'emploi'],
    'Montant_Credit': ['montant', 'credit', 'montant_credit', 'loan_amount', 'crédit'],
    'Duree_Credit': ['duree', 'durée', 'duree_credit', 'loan_duration', 'mois'],
    'Taux_Interet': ['taux', 'taux_interet', 'taux intérêt', 'interest_rate', 'rate'],
    'Mensualite': ['mensualite', 'mensualité', 'monthly_payment', 'payment'],
    'Nombre_Retards': ['retards', 'nombre_retards', 'late_payments', 'delays'],
    'Incident_Paiement': ['incidents', 'incident_paiement', 'payment_incidents', 'incidents'],
    'Defaut': ['defaut', 'défaut', 'default', 'target', 'y'],
    'Nombre_Demandes': ['demandes', 'nombre_demandes', 'credit_requests', 'requests']
}

# Colonnes obligatoires pour l'analyse complète
REQUIRED_COLUMNS = [
    'Revenu_Mensuel', 'Montant_Credit', 'Duree_Credit', 
    'Nombre_Retards', 'Incident_Paiement', 'Defaut'
]

# Couleurs pour les graphiques (Chart.js)
CHART_COLORS = {
    'primary': '#1a237e',
    'secondary': '#1565c0',
    'success': '#2e7d32',
    'danger': '#c62828',
    'warning': '#ef6c00',
    'info': '#0288d1'
}