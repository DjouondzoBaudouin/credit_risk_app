"""
Définition et entraînement des modèles de Machine Learning avec scikit-learn.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve, confusion_matrix

def train_simple_regression(df):
    """Entraîne un modèle de régression linéaire simple."""
    X = df[['Revenu_Mensuel']].values
    y = df['Montant_Credit'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    
    return model, model.intercept_, model.coef_[0], r2

def train_multiple_regression(df):
    """Entraîne un modèle de régression linéaire multiple."""
    features = ['Revenu_Mensuel', 'Age', 'Anciennete_Emploi']
    existing_features = [f for f in features if f in df.columns]
    
    X = df[existing_features].values
    y = df['Montant_Credit'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    y_pred = model.predict(X_scaled)
    
    # Coefficients standardisés pour l'interprétation
    coeffs = {}
    for i, feat in enumerate(existing_features):
        coeffs[feat] = {
            'raw': float(model.coef_[i]),
            'standardized': float(model.coef_[i] * np.std(X[:, i]) / np.std(y)) if np.std(y) > 0 else 0.0
        }
    coeffs['Intercept'] = {'raw': float(model.intercept_), 'standardized': 0.0}
    
    return model, scaler, coeffs, r2_score(y, y_pred), mean_absolute_error(y, y_pred), mean_squared_error(y, y_pred), np.sqrt(mean_squared_error(y, y_pred))

def train_logistic_regression(df):
    """Entraîne un modèle de régression logistique pour la classification binaire."""
    features = ['Revenu_Mensuel', 'Montant_Credit', 'Duree_Credit', 'Nombre_Retards', 'Anciennete_Emploi', 'Taux_Interet']
    existing_features = [f for f in features if f in df.columns]
    
    X = df[existing_features].values
    y = df['Defaut'].values
    
    # Vérifier qu'il y a au moins 2 classes dans y
    unique_classes = np.unique(y)
    if len(unique_classes) < 2:
        # Si une seule classe, créer un split artificiel
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0)
    }
    
    # CORRECTION : Gestion sécurisée du ROC-AUC
    try:
        # Vérifier qu'il y a au moins 2 classes dans y_test
        if len(np.unique(y_test)) > 1:
            metrics['roc_auc'] = roc_auc_score(y_test, y_prob)
        else:
            metrics['roc_auc'] = 0.5  # Valeur par défaut pour une seule classe
    except ValueError:
        metrics['roc_auc'] = 0.5
    
    # CORRECTION : labels=[0, 1] force une matrice 2x2 même si une classe est absente
    conf_matrix = confusion_matrix(y_test, y_pred, labels=[0, 1])
    
    try:
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    except ValueError:
        # Si une seule classe, créer des valeurs par défaut
        fpr = np.array([0.0, 1.0])
        tpr = np.array([0.0, 1.0])
        thresholds = np.array([1.0, 0.0])
    
    return metrics, conf_matrix, fpr, tpr, metrics['roc_auc']