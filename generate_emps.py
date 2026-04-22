import os
import sys
import django

# Configuration de l'environnement Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_rh.settings')
django.setup()

import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from personnel.models import Employe, Departement

# Vérifier et créer des départements si nécessaire
depts = list(Departement.objects.all())
if not depts:
    for name in ['Ressources Humaines', 'Informatique', 'Marketing', 'Ventes', 'Comptabilité', 'Logistique']:
        dept = Departement.objects.create(nom=name, description=f"Département {name}")
        depts.append(dept)

# Poids pour une répartition inégale (Certains départements auront beaucoup plus d'employés)
weights = [10, 1, 8, 2, 5, 1][:len(depts)]
if len(weights) < len(depts):
    weights.extend([1] * (len(depts) - len(weights)))

first_names = [
    "Jean", "Marie", "Pierre", "Sophie", "Luc", "Julie", "Marc", "Camille", 
    "Thomas", "Sarah", "Nicolas", "Emma", "Paul", "Léa", "Antoine", "Chloé",
    "Alexandre", "Manon", "David", "Laura", "Maxime", "Céline", "Julien", "Alice"
]

last_names = [
    "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois",
    "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David",
    "Bertrand", "Morel", "Fournier", "Girard", "Bonnet", "Dupont", "Lambert", "Fontaine"
]

postes = [
    "Développeur", "Analyste", "Chef de Projet", "Assistant", "Manager", 
    "Consultant", "Technicien", "Directeur", "Coordinateur", "Spécialiste"
]

print("Création de 20 employés...")
created = 0
attempts = 0

while created < 20 and attempts < 100:
    attempts += 1
    prenom = random.choice(first_names)
    nom = random.choice(last_names)
    
    # Génération d'un email unique
    email = f"{prenom.lower()}.{nom.lower()}{random.randint(100,9999)}@entreprise.com"
    matricule = f"EMP{random.randint(10000, 99999)}"
    
    # Vérifier l'unicité
    if User.objects.filter(username=email).exists() or Employe.objects.filter(matricule=matricule).exists() or Employe.objects.filter(email=email).exists():
        continue
        
    telephone = f"+225 {random.randint(0,9)}{random.randint(0,9)} {random.randint(0,9)}{random.randint(0,9)} {random.randint(0,9)}{random.randint(0,9)} {random.randint(0,9)}{random.randint(0,9)}"
    poste = random.choice(postes)
    
    departement = random.choices(depts, weights=weights, k=1)[0]
    
    # Date d'embauche aléatoire sur les 5 dernières années
    days_ago = random.randint(1, 365 * 5)
    date_embauche = datetime.now() - timedelta(days=days_ago)
    
    try:
        user = User.objects.create_user(
            username=email,
            email=email,
            password='Password123!'
        )
        
        Employe.objects.create(
            user=user,
            matricule=matricule,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            poste=poste,
            departement=departement,
            date_embauche=date_embauche.date(),
            statut='actif', # "Actif" pour tous comme demandé
            role='employe'  # "Employé" pour tous
        )
        created += 1
    except Exception as e:
        print(f"Erreur lors de la création d'un employé: {e}")

print(f"{created} employés créés avec succès !")
