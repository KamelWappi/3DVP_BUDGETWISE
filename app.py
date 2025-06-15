from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import date
from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env
load_dotenv()

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'flask_secret')

# Configuration de la base de données PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://localhost/budgetwise')

def get_db_connection():
    """
    Fonction pour se connecter à la base de données PostgreSQL
    Retourne une connexion à la base de données
    """
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données: {e}")
        return None

def init_database():
    """
    Initialise la base de données en créant les tables nécessaires
    """
    conn = get_db_connection()
    if conn is None:
        return
    
    try:
        cur = conn.cursor()
        
        # Création de la table des revenus
        cur.execute('''
            CREATE TABLE IF NOT EXISTS revenus (
                id SERIAL PRIMARY KEY,
                montant DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                source VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Création de la table des dépenses
        cur.execute('''
            CREATE TABLE IF NOT EXISTS depenses (
                id SERIAL PRIMARY KEY,
                montant DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL,
                description TEXT NOT NULL,
                categorie VARCHAR(100) NOT NULL,
                tags VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Création de la table des budgets mensuels
        cur.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                mois INTEGER NOT NULL,
                annee INTEGER NOT NULL,
                montant_budget DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(mois, annee)
            )
        ''')
        
        conn.commit()
        print("Base de données initialisée avec succès")
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

@app.route('/')
def dashboard():
    """
    Page d'accueil - Dashboard principal
    Affiche un résumé du budget avec totaux et solde
    """
    conn = get_db_connection()
    if conn is None:
        flash('Erreur de connexion à la base de données', 'error')
        return render_template('error.html')
    
    try:
        cur = conn.cursor()
        
        # Récupération du total des revenus
        cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM revenus')
        total_revenus = float(cur.fetchone()['total'])
        
        # Récupération du total des dépenses
        cur.execute('SELECT COALESCE(SUM(montant), 0) as total FROM depenses')
        total_depenses = float(cur.fetchone()['total'])
        
        # Calcul du solde
        solde = total_revenus - total_depenses
        
        # Récupération des dernières transactions (5 plus récentes)
        cur.execute('''
            SELECT 'revenu' as type, montant, date, description, source as extra
            FROM revenus
            UNION ALL
            SELECT 'depense' as type, montant, date, description, categorie as extra
            FROM depenses
            ORDER BY date DESC
            LIMIT 5
        ''')
        dernieres_transactions = cur.fetchall()
        
        # Récupération des statistiques par catégorie
        cur.execute('''
            SELECT categorie, SUM(montant) as total
            FROM depenses
            GROUP BY categorie
            ORDER BY total DESC
        ''')
        stats_categories = cur.fetchall()
        
        return render_template('dashboard.html',
                               total_revenus=total_revenus,
                               total_depenses=total_depenses,
                               solde=solde,
                               dernieres_transactions=dernieres_transactions,
                               stats_categories=stats_categories)
    
    except Exception as e:
        flash(f'Erreur lors du chargement du dashboard: {e}', 'error')
        return render_template('error.html')
    finally:
        cur.close()
        conn.close()

@app.route('/revenus')
def liste_revenus():
    """
    Affiche la liste de tous les revenus
    """
    conn = get_db_connection()
    if conn is None:
        flash('Erreur de connexion à la base de données', 'error')
        return render_template('error.html')
    
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM revenus ORDER BY date DESC')
        revenus = cur.fetchall()
        
        return render_template('revenus.html', revenus=revenus)
    
    except Exception as e:
        flash(f'Erreur lors du chargement des revenus: {e}', 'error')
        return render_template('error.html')
    finally:
        cur.close()
        conn.close()

@app.route('/depenses')
def liste_depenses():
    """
    Affiche la liste de toutes les dépenses
    """
    conn = get_db_connection()
    if conn is None:
        flash('Erreur de connexion à la base de données', 'error')
        return render_template('error.html')
    
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM depenses ORDER BY date DESC')
        depenses = cur.fetchall()
        
        return render_template('depenses.html', depenses=depenses)
    
    except Exception as e:
        flash(f'Erreur lors du chargement des dépenses: {e}', 'error')
        return render_template('error.html')
    finally:
        cur.close()
        conn.close()

@app.route('/ajouter-revenu', methods=['GET', 'POST'])
def ajouter_revenu():
    """
    Formulaire pour ajouter un nouveau revenu
    """
    if request.method == 'POST':
        montant = request.form['montant']
        date_revenu = request.form['date']
        description = request.form['description']
        source = request.form['source']

        # Validation simple des données
        if not all([montant, date_revenu, description, source]):
            flash('Tous les champs sont obligatoires', 'error')
            return render_template('ajouter_revenu.html')
        
        conn = get_db_connection()
        if conn is None:
            flash('Erreur de connexion à la base de données', 'error')
            return render_template('error.html')
        
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO revenus (montant, date, description, source)
                VALUES (%s, %s, %s, %s)
            ''', (montant, date_revenu, description, source))
            
            conn.commit()
            flash('Revenu ajouté avec succès!', 'success')
            return redirect(url_for('liste_revenus'))
        
        except Exception as e:
            flash(f'Erreur lors de l\'ajout du revenu: {e}', 'error')
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    
    today = date.today().isoformat()
    return render_template('ajouter_revenu.html', today=today)

@app.route('/ajouter-depense', methods=['GET', 'POST'])
def ajouter_depense():
    """
    Formulaire pour ajouter une nouvelle dépense
    """
    if request.method == 'POST':
        montant = request.form['montant']
        date_depense = request.form['date']
        description = request.form['description']
        categorie = request.form['categorie']
        tags = request.form.get('tags', '')  # Optionnel
        
        if not all([montant, date_depense, description, categorie]):
            flash('Tous les champs obligatoires doivent être remplis', 'error')
            return render_template('ajouter_depense.html', categories=categories)
        
        conn = get_db_connection()
        if conn is None:
            flash('Erreur de connexion à la base de données', 'error')
            return render_template('error.html')
        
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO depenses (montant, date, description, categorie, tags)
                VALUES (%s, %s, %s, %s, %s)
            ''', (montant, date_depense, description, categorie, tags))
            
            conn.commit()
            flash('Dépense ajoutée avec succès!', 'success')
            return redirect(url_for('liste_depenses'))
        
        except Exception as e:
            flash(f'Erreur lors de l\'ajout de la dépense: {e}', 'error')
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    
    
    categories = [
        'Alimentation', 'Transport', 'Logement', 'Santé',
        'Loisirs', 'Vêtements', 'Éducation', 'Autre'
    ]

    today = date.today().isoformat()
    return render_template('ajouter_depense.html', categories=categories, today=today)


@app.route('/statistiques')
def statistiques():
    """
    Page des statistiques détaillées
    """
    conn = get_db_connection()
    if conn is None:
        flash('Erreur de connexion à la base de données', 'error')
        return render_template('error.html')
    
    try:
        cur = conn.cursor()
        
        # Statistiques par catégorie
        cur.execute('''
            SELECT categorie, COUNT(*) as nombre, SUM(montant) as total
            FROM depenses
            GROUP BY categorie
            ORDER BY total DESC
        ''')
        stats_categories = cur.fetchall()
        
        # Statistiques par mois
        cur.execute('''
            SELECT 
                EXTRACT(YEAR FROM date) as annee,
                EXTRACT(MONTH FROM date) as mois,
                SUM(montant) as total
            FROM depenses
            GROUP BY annee, mois
            ORDER BY annee DESC, mois DESC
        ''')
        stats_mois = cur.fetchall()
        
        return render_template('statistiques.html',
                               stats_categories=stats_categories,
                               stats_mois=stats_mois)
    
    except Exception as e:
        flash(f'Erreur lors du chargement des statistiques: {e}', 'error')
        return render_template('error.html')
    finally:
        cur.close()
        conn.close()




if __name__ == '__main__':
    # Initialisation de la base de données au démarrage
    init_database()
    
    # Lancement de l'application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)






