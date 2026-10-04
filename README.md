# Application d'Analyse du Risque de Crédit Bancaire

Application web professionnelle locale pour l'analyse statistique et la prédiction du risque de crédit bancaire. Développée en Python (bibliothèque standard pour le serveur) et JavaScript vanilla avec Bootstrap 5.

## Fonctionnalités
- Chargement et nettoyage automatique de fichiers CSV/Excel.
- Génération de données simulées réalistes (500 clients).
- Analyse statistique descriptive complète (moyenne, médiane, écart-type, IQR).
- Modélisation par Loi de Gauss (Revenus) et Loi de Poisson (Incidents).
- Régression linéaire simple et multiple pour la prédiction des montants.
- Régression logistique pour la classification du risque de défaut (avec matrice de confusion et courbe ROC).
- Tableau de bord interactif avec KPI et graphiques (Chart.js).
- Export de rapports complets au format Excel (6 feuilles).
- Mode Clair / Sombre avec sauvegarde des préférences.

## Architecture
- **Backend** : `http.server` (Python standard) + `pandas`, `numpy`, `scipy`, `scikit-learn`, `openpyxl`.
- **Frontend** : HTML5, CSS3, JavaScript vanilla, Bootstrap 5 (CDN), Chart.js (CDN).
- **Données** : Stockage local dans le dossier `data/`.

## Prérequis
- Python 3.12 ou supérieur.
- Connexion Internet (uniquement pour charger les bibliothèques frontend via CDN au premier lancement).

## Installation et Lancement
1. Cloner ou télécharger le projet.
2. Installer les dépendances Python :