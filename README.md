# BudgetWise - Gestionnaire de Budget Simple

BudgetWise est une application web simple et intuitive pour gérer votre budget personnel. 

##  Fonctionnalités

###  Fonctionnalités principales
- **Dashboard** : Vue d'ensemble de la situation financière
- **Gestion des revenus** : Ajout et suivi de tous les revenus
- **Gestion des dépenses** : Ajout et catégorisation des dépenses
- **Calcul automatique du solde** : Suivi en temps réel de la situation financière
- **Statistiques détaillées** : Analyse des habitudes de dépense


##  Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, CSS3, Bootstrap 5

## Lien github

https://github.com/KamelWappi/3DVP_BUDGETWISE

##  Prérequis

- Python 3.12.7
- PostgreSQL 17
- pip 24.2

##  Installation locale

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd budgetwise
```


### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données
```bash
createdb budgetwise
psql -c "CREATE DATABASE budgetwise;"
```

### 5. Configuration
```bash
nano .env
```

### 6. Lancer l'application
```bash
python app.py
```

L'application est accessible sur `http://localhost:5000`


##  Structure du projet

3DVP_BUDGETWISE/
├── app.py                 
├── requirements.txt       
├── .env         
├── README.md             
└── templates/            
    ├── base.html         
    ├── dashboard.html    
    ├── revenus.html      
    ├── depenses.html     
    ├── ajouter_revenu.html    
    ├── ajouter_depense.html   
    ├── statistiques.html      
    └── error.html             


##  Utilisation

### Premier démarrage
1. Accédez à `http://localhost:5000`
2. L'application créera automatiquement les tables nécessaires


### Tables principales
- `revenus` : Stockage des revenus
- `depenses` : Stockage des dépenses
- `budgets` : Budgets mensuels 


### Variables d'environnement de production

DATABASE_URL=postgresql://localhost:kawa2005@host:5432/budgetwise
SECRET_KEY=flask_secret
PORT=5000







