from django.contrib import admin
from .models import Employe, Presence, Conge
from django.contrib.auth.models import User


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Employe"""
    
    list_display = ('matricule', 'nom', 'prenom', 'email', 'poste', 'departement', 'role', 'statut', 'date_embauche')
    list_filter = ('statut', 'role', 'departement', 'date_embauche')
    search_fields = ('matricule', 'nom', 'prenom', 'email', 'poste')
    ordering = ('nom', 'prenom')
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('matricule', 'nom', 'prenom', 'email', 'telephone')
        }),
        ('Informations professionnelles', {
            'fields': ('poste', 'departement', 'date_embauche', 'statut', 'role')
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'classes': ('collapse',),
            'description': 'Lien avec le compte de connexion Django'
        }),
    )
    
    # Actions personnalisées
    actions = ['creer_compte_utilisateur', 'activer_employes', 'desactiver_employes']
    
    def creer_compte_utilisateur(self, request, queryset):
        """Crée automatiquement un compte User pour les employés sélectionnés"""
        count = 0
        for employe in queryset:
            if not employe.user:  # Si l'employé n'a pas encore de compte
                # Créer un username basé sur prénom.nom
                username = f"{employe.prenom.lower()}.{employe.nom.lower()}"
                
                # Vérifier si le username existe déjà
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=employe.email,
                    first_name=employe.prenom,
                    last_name=employe.nom,
                    password='Changeme123!'  # Mot de passe par défaut
                )
                
                # Définir les permissions selon le rôle
                if employe.role == 'admin_rh':
                    user.is_staff = True
                    user.is_superuser = True
                
                user.save()
                
                # Lier l'utilisateur à l'employé
                employe.user = user
                employe.save()
                
                count += 1
        
        self.message_user(request, f"{count} compte(s) utilisateur créé(s). Mot de passe par défaut: Changeme123!")
    creer_compte_utilisateur.short_description = "Créer un compte utilisateur pour les employés sélectionnés"
    
    def activer_employes(self, request, queryset):
        """Active les employés sélectionnés"""
        queryset.update(statut='actif')
        self.message_user(request, f"{queryset.count()} employé(s) activé(s)")
    activer_employes.short_description = "Activer les employés sélectionnés"
    
    def desactiver_employes(self, request, queryset):
        """Désactive les employés sélectionnés"""
        queryset.update(statut='inactif')
        self.message_user(request, f"{queryset.count()} employé(s) désactivé(s)")
    desactiver_employes.short_description = "Désactiver les employés sélectionnés"


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Presence"""
    
    list_display = ('employe', 'date', 'heure_arrivee', 'statut', 'get_departement')
    list_filter = ('statut', 'date', 'employe__departement')
    search_fields = ('employe__nom', 'employe__prenom', 'employe__matricule')
    date_hierarchy = 'date'
    ordering = ('-date', 'employe')
    
    def get_departement(self, obj):
        """Affiche le département de l'employé"""
        return obj.employe.departement
    get_departement.short_description = 'Département'
    
    # Actions personnalisées
    actions = ['marquer_present', 'marquer_absent']
    
    def marquer_present(self, request, queryset):
        queryset.update(statut='present')
        self.message_user(request, f"{queryset.count()} présence(s) marquée(s) comme présent")
    marquer_present.short_description = "Marquer comme présent"
    
    def marquer_absent(self, request, queryset):
        queryset.update(statut='absent')
        self.message_user(request, f"{queryset.count()} présence(s) marquée(s) comme absent")
    marquer_absent.short_description = "Marquer comme absent"


@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour le modèle Conge"""
    
    list_display = ('employe', 'type_conge', 'date_debut', 'date_fin', 'nombre_jours', 'statut', 'get_departement')
    list_filter = ('statut', 'type_conge', 'date_debut', 'employe__departement')
    search_fields = ('employe__nom', 'employe__prenom', 'employe__matricule', 'justificatif_texte')
    date_hierarchy = 'date_debut'
    ordering = ('-date_debut',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('employe', 'type_conge', 'date_debut', 'date_fin')
        }),
        ('Justification', {
            'fields': ('justificatif_texte', 'justificatif_fichier')
        }),
        ('Gestion', {
            'fields': ('statut', 'commentaire'),
            'classes': ('collapse',)
        }),
    )
    
    def get_departement(self, obj):
        """Affiche le département de l'employé"""
        return obj.employe.departement
    get_departement.short_description = 'Département'
    
    def nombre_jours(self, obj):
        """Calcule le nombre de jours de congé"""
        if obj.date_debut and obj.date_fin:
            return (obj.date_fin - obj.date_debut).days + 1
        return 0
    nombre_jours.short_description = 'Nb jours'
    
    # Actions personnalisées
    actions = ['approuver_conges', 'refuser_conges', 'mettre_en_attente']
    
    def approuver_conges(self, request, queryset):
        queryset.update(statut='approuve')
        self.message_user(request, f"{queryset.count()} congé(s) approuvé(s)")
    approuver_conges.short_description = "✅ Approuver les congés sélectionnés"
    
    def refuser_conges(self, request, queryset):
        queryset.update(statut='refuse')
        self.message_user(request, f"{queryset.count()} congé(s) refusé(s)")
    refuser_conges.short_description = "❌ Refuser les congés sélectionnés"
    
    def mettre_en_attente(self, request, queryset):
        queryset.update(statut='en_attente')
        self.message_user(request, f"{queryset.count()} congé(s) mis en attente")
    mettre_en_attente.short_description = "⏳ Mettre en attente"


# Personnalisation du site admin
admin.site.site_header = "Gestion RH - Administration"
admin.site.site_title = "Gestion RH Admin"
admin.site.index_title = "Bienvenue dans l'interface d'administration"