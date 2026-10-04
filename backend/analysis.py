"""
Analyses statistiques et modèles de machine learning.
"""
import pandas as pd
import numpy as np
from scipy import stats
from backend.models import train_simple_regression, train_multiple_regression, train_logistic_regression

def get_descriptive_stats(df):
    """Calcule les statistiques descriptives pour les variables quantitatives clés."""
    cols = ['Age', 'Revenu_Mensuel', 'Montant_Credit', 'Duree_Credit', 'Mensualite', 'Nombre_Retards']
    existing_cols = [c for c in cols if c in df.columns]
    
    stats_dict = {}
    for col in existing_cols:
        data = df[col].dropna()
        if len(data) == 0:
            continue
        q1, q2, q3 = np.percentile(data, [25, 50, 75])
        mean_val = float(np.mean(data))
        std_val = float(np.std(data))
        
        stats_dict[col] = {
            'moyenne': mean_val,
            'mediane': float(np.median(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'variance': float(np.var(data)),
            'ecart_type': std_val,
            'q1': float(q1),
            'q2': float(q2),
            'q3': float(q3),
            'cv': float(std_val / mean_val) if mean_val != 0 else 0
        }
    
    # Interprétation automatique
    interpretations = []
    if 'Revenu_Mensuel' in stats_dict:
        interpretations.append(f"Le revenu moyen des clients est de {stats_dict['Revenu_Mensuel']['moyenne']:,.0f} FCFA.")
    if 'Montant_Credit' in stats_dict:
        interpretations.append(f"Le montant moyen des crédits est de {stats_dict['Montant_Credit']['moyenne']:,.0f} FCFA.")
    if stats_dict:
        max_cv_col = max(stats_dict, key=lambda k: stats_dict[k]['cv'])
        interpretations.append(f"La variable avec la plus forte dispersion (CV) est : {max_cv_col}.")
    
    # Détection des valeurs aberrantes (IQR) pour Revenu_Mensuel
    outliers = 0
    if 'Revenu_Mensuel' in df.columns:
        q1 = df['Revenu_Mensuel'].quantile(0.25)
        q3 = df['Revenu_Mensuel'].quantile(0.75)
        iqr = q3 - q1
        outliers = len(df[(df['Revenu_Mensuel'] < (q1 - 1.5 * iqr)) | (df['Revenu_Mensuel'] > (q3 + 1.5 * iqr))])
    
    return {
        'stats': stats_dict,
        'interpretations': interpretations,
        'outliers_count': int(outliers),
        'total_clients': int(len(df)),
        'default_rate': float(df['Defaut'].mean() * 100) if 'Defaut' in df.columns else 0
    }

def get_gaussian_analysis(df):
    """Analyse de la distribution des revenus selon la loi de Gauss."""
    if 'Revenu_Mensuel' not in df.columns:
        return {'error': 'Colonne Revenu_Mensuel manquante'}
        
    data = df['Revenu_Mensuel'].dropna()
    mu = float(np.mean(data))
    sigma = float(np.std(data))
    if sigma == 0:
        sigma = 1.0
    
    # Probabilités
    p_low = float(stats.norm.cdf(300000, mu, sigma))
    p_mid = float(stats.norm.cdf(800000, mu, sigma) - stats.norm.cdf(300000, mu, sigma))
    p_high = float(1 - stats.norm.cdf(1000000, mu, sigma))
    
    # Données pour l'histogramme et la courbe
    counts, bins = np.histogram(data, bins=30, density=True)
    x_curve = np.linspace(min(data), max(data), 100)
    y_curve = stats.norm.pdf(x_curve, mu, sigma)
    
    return {
        'mu': mu,
        'sigma': sigma,
        'probabilities': {
            'P_X_inf_300k': p_low,
            'P_300k_X_800k': p_mid,
            'P_X_sup_1M': p_high
        },
        'histogram': {'counts': counts.tolist(), 'bins': bins.tolist()},
        'curve': {'x': x_curve.tolist(), 'y': y_curve.tolist()},
        'interpretation': [
            f"Environ {p_low*100:.1f}% des clients ont un revenu faible (< 300 000 FCFA).",
            f"Environ {p_mid*100:.1f}% des clients ont un revenu moyen (300 000 - 800 000 FCFA).",
            f"Environ {p_high*100:.1f}% des clients ont un revenu élevé (> 1 000 000 FCFA)."
        ]
    }

def get_poisson_analysis(df):
    """Analyse du nombre d'incidents de paiement selon la loi de Poisson."""
    if 'Incident_Paiement' not in df.columns:
        return {'error': 'Colonne Incident_Paiement manquante'}
        
    data = df['Incident_Paiement'].dropna()
    lambda_val = float(np.mean(data))
    
    # Probabilités théoriques
    p0 = float(stats.poisson.pmf(0, lambda_val))
    p1 = float(stats.poisson.pmf(1, lambda_val))
    p2 = float(stats.poisson.pmf(2, lambda_val))
    
    # Comparaison réel vs théorique
    max_val = int(min(data.max(), 10))
    x_vals = list(range(max_val + 1))
    real_probs = [float(np.mean(data == x)) for x in x_vals]
    theo_probs = [float(stats.poisson.pmf(x, lambda_val)) for x in x_vals]
    
    return {
        'lambda': lambda_val,
        'probabilities': {'P_X_0': p0, 'P_X_1': p1, 'P_X_2': p2},
        'comparison': {
            'x': x_vals,
            'reel': real_probs,
            'theorique': theo_probs
        },
        'interpretation': "La loi de Poisson est adaptée pour modéliser le nombre d'incidents de paiement, car il s'agit d'événements rares et indépendants sur une période donnée."
    }

def get_simple_regression(df, prediction_value=750000):
    """Régression linéaire simple : Montant_Credit = f(Revenu_Mensuel)."""
    model, beta_0, beta_1, r2 = train_simple_regression(df)
    
    prediction = float(beta_0 + beta_1 * prediction_value)
    
    return {
        'beta_0': float(beta_0),
        'beta_1': float(beta_1),
        'r2': float(r2),
        'prediction_value': prediction_value,
        'prediction_result': prediction,
        'interpretation': [
            f"Pour chaque augmentation de 1 FCFA du revenu, le montant du crédit augmente en moyenne de {beta_1:.4f} FCFA.",
            f"Le modèle explique {r2*100:.2f}% de la variance du montant du crédit (R²)."
        ]
    }

def get_multiple_regression(df):
    """Régression linéaire multiple : Montant_Credit = f(Revenu, Age, Anciennete)."""
    model, scaler, coeffs, r2, mae, mse, rmse = train_multiple_regression(df)
    
    # CORRECTION : coeffs est déjà un dictionnaire correctement formaté
    # On ne fait pas float() sur le dict entier, juste sur les valeurs
    clean_coeffs = {}
    for key, value in coeffs.items():
        if isinstance(value, dict):
            clean_coeffs[key] = {
                'raw': float(value['raw']),
                'standardized': float(value['standardized'])
            }
        else:
            clean_coeffs[key] = float(value)
    
    return {
        'coefficients': clean_coeffs,
        'r2': float(r2),
        'mae': float(mae),
        'mse': float(mse),
        'rmse': float(rmse),
        'most_influential': max(coeffs, key=lambda k: abs(coeffs[k]['standardized'])),
        'interpretation': "Le modèle multiple prend en compte plusieurs facteurs, offrant généralement une meilleure prédiction que la régression simple si les variables ajoutées sont pertinentes."
    }

def get_logistic_regression(df):
    """Régression logistique pour prédire le défaut de paiement."""
    metrics, confusion, fpr, tpr, roc_auc = train_logistic_regression(df)
    
    # CORRECTION : Conversion sécurisée des métriques avec gestion des NaN
    clean_metrics = {}
    for key, value in metrics.items():
        try:
            val = float(value)
            # Remplacer NaN par 0.0 pour éviter les erreurs JSON
            if np.isnan(val) or np.isinf(val):
                val = 0.0
            clean_metrics[key] = val
        except (TypeError, ValueError):
            clean_metrics[key] = 0.0
    
    return {
        'metrics': clean_metrics,
        'confusion_matrix': confusion.tolist(),
        'roc_curve': {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'auc': float(roc_auc) if not (np.isnan(roc_auc) or np.isinf(roc_auc)) else 0.0
        },
        'interpretation': "La régression logistique est adaptée ici car la variable cible (Défaut) est binaire (0 ou 1). Une régression linéaire classique pourrait prédire des valeurs hors de l'intervalle [0, 1], ce qui n'a pas de sens pour une probabilité."
    }