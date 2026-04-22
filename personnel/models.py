from django.db import models
from django.contrib.auth.models import User

class Departement(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom
    
class Employe(models.Model):
    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)  
    telephone = models.CharField(max_length=20, null=True, blank=True)  
    poste = models.CharField(max_length=50)
    departement = models.ForeignKey(
        Departement,
        on_delete=models.SET_NULL,
        null=True,
        related_name="employes"
    )
    date_embauche = models.DateField()
    statut = models.CharField(max_length=20)
    
    # Lien avec User Django
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='employe'
    ) 
    
    # Rôle
    ROLE_CHOICES = [
        ('admin_rh', 'Administrateur RH'),
        ('employe', 'Employé'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='employe'
    )  

class Conge(models.Model):
    TYPE_CONGE_CHOICES = [
        ("annuel", "Congé annuel"),
        ("maladie", "Congé maladie"),
        ("exceptionnel", "Congé exceptionnel"),
        ("sans_solde", "Congé sans solde"),
    ]

    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("approuve", "Approuvé"),
        ("refuse", "Refusé"),
        ("annule", "Annulé"),
    ]

    employe = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name="conges"
    )

    date_debut = models.DateField()
    date_fin = models.DateField()

    type_conge = models.CharField(
        max_length=50,
        choices=TYPE_CONGE_CHOICES
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="en_attente"
    )

    justificatif_texte = models.TextField(
        null=True,
        blank=True
    )

    justificatif_fichier = models.FileField(
        upload_to="justificatifs/conges/",
        null=True,
        blank=True
    )

    commentaire = models.TextField(
        null=True,
        blank=True
    )

    vu_par_employe = models.BooleanField(
        default=False,
        help_text="Indique si l'employé a vu la réponse (accepté/refusé) des RH"
    )

    @property
    def duree_jours(self):
        if self.date_fin and self.date_debut:
            return (self.date_fin - self.date_debut).days + 1
        return 0

    def __str__(self):
        return f"Congé {self.type_conge} - {self.employe}"

class Presence(models.Model):
    STATUT_CHOICES = [
        ("present", "Présent"),
        ("absent", "Absent"),
        ("retard", "En retard"),
        ("conge", "En congé"),
    ]

    employe = models.ForeignKey(
        Employe,
        on_delete=models.CASCADE,
        related_name="presences"
    )

    date = models.DateField()
    heure_arrivee = models.TimeField(
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES
    )

    commentaire = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ("employe", "date")

    def __str__(self):
        return f"{self.employe} - {self.date}"
