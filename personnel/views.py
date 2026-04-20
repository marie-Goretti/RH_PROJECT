
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, CongeForm, EmployeForm
from .models import Employe, Conge, Presence, Departement
from datetime import date
from django.db.models import Count, Q


def register_view(request):
    """Vue pour l'inscription"""
    
    if request.user.is_authenticated:
        # Si l'utilisateur est déjà connecté, rediriger
        if hasattr(request.user, 'employe'):
            if request.user.employe.role == 'admin_rh':
                return redirect('dashboard')
            else:
                return redirect('dashboard_employe')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            # Créer l'utilisateur et l'employé
            user = form.save()
            
            # Connecter automatiquement l'utilisateur après inscription
            login(request, user)
            
            messages.success(request, 'Votre compte a été créé avec succès !')
            
            # Rediriger selon le rôle
            if hasattr(user, 'employe'):
                if user.employe.role == 'admin_rh':
                    return redirect('dashboard')
                else:
                    return redirect('dashboard_employe')
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = RegisterForm()
    
    return render(request, 'personnel/register.html', {'form': form})


def login_view(request):
    """Vue pour la connexion avec email"""
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'employe'):
            if request.user.employe.role == 'admin_rh':
                return redirect('dashboard')
            else:
                return redirect('dashboard_employe')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Trouver l'utilisateur par email
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect.')
                return render(request, 'personnel/login.html', {'form': form})
            
            # Authentifier l'utilisateur avec le username
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Message de bienvenue personnalisé
                if hasattr(user, 'employe'):
                    nom_complet = f"{user.employe.prenom} {user.employe.nom}"
                    messages.success(request, f'Bienvenue {nom_complet} !')
                else:
                    messages.success(request, f'Bienvenue {user.username} !')
                
                # Rediriger selon le rôle
                if hasattr(user, 'employe'):
                    if user.employe.role == 'admin_rh':
                        return redirect('dashboard')
                    else:
                        return redirect('dashboard_employe')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
    
    return render(request, 'personnel/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vue pour la déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')


#@login_required
#def dashboard(request):
 #   """Vue temporaire pour le tableau de bord général"""
  #  return render(request, 'personnel/dashboard.html')


@login_required
def dashboard_employe(request):
    """Vue du tableau de bord Employé"""
    # Vérifier que l'utilisateur est bien un employé
    if not hasattr(request.user, 'employe') or request.user.employe.role != 'employe':
        messages.error(request, 'Accès refusé. Vous n\'êtes pas un employé.')
        return redirect('dashboard')
    
    context = {
        'employe': request.user.employe
    }
    return render(request, 'personnel/dashboard_employe.html', context)


@login_required
def dashboard(request):
    """Vue du tableau de bord Admin RH avec statistiques"""
    # Vérifier que l'utilisateur est bien un admin RH
    if not hasattr(request.user, 'employe') or request.user.employe.role != 'admin_rh':
        messages.error(request, 'Accès refusé. Vous n\'êtes pas administrateur RH.')
        return redirect('dashboard')
    
    from datetime import date
    from django.db.models import Count, Q
    
    # Récupérer tous les employés
    employes = Employe.objects.all().order_by('nom')
    
    # Statistiques
    total_employes = employes.filter(statut='actif').count()
    
    # Présences aujourd'hui
    today = date.today()
    presences_aujourdhui = Presence.objects.filter(
        date=today,
        statut__in=['present', 'retard']
    ).count()
    
    # Retards ce mois
    retards_aujourdhui = Presence.objects.filter(
        date__year=today.year,
        date__month=today.month,
        statut='retard'
    ).count()
    
    # Congés en attente
    conges_en_attente = Conge.objects.filter(statut='en_attente').count()
    
    context = {
        'employe': request.user.employe,
        'employes': employes,
        'total_employes': total_employes,
        'presences_aujourdhui': presences_aujourdhui,
        'retards_aujourdhui': retards_aujourdhui,
        'conges_en_attente': conges_en_attente,
    }
    
    return render(request, 'personnel/dashboard.html', context)


@login_required
def demande_conge(request):
    """Vue pour la demande de congé et l'historique"""
    
    # Vérifier que l'utilisateur est bien un employé
    if not hasattr(request.user, 'employe'):
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard')
    
    employe = request.user.employe
    
    if request.method == 'POST':
        form = CongeForm(request.POST, request.FILES)
        
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut']
            date_fin = form.cleaned_data['date_fin']
            
            # Validation : la période ne doit pas dépasser 2 mois (60 jours)
            duree = (date_fin - date_debut).days + 1
            
            if duree > 60:
                messages.error(request, 'La durée du congé ne peut pas dépasser 2 mois (60 jours).')
                return render(request, 'personnel/demande_conge.html', {
                    'form': form,
                    'employe': employe,
                    'conges': Conge.objects.filter(employe=employe).order_by('-date_debut')
                })
            
            if duree <= 0:
                messages.error(request, 'La date de fin doit être après la date de début.')
                return render(request, 'personnel/demande_conge.html', {
                    'form': form,
                    'employe': employe,
                    'conges': Conge.objects.filter(employe=employe).order_by('-date_debut')
                })
            
            # Créer la demande de congé
            conge = form.save(commit=False)
            conge.employe = employe
            conge.statut = 'en_attente'
            conge.save()
            
            messages.success(request, f'Votre demande de congé de {duree} jour(s) a été soumise avec succès.')
            return redirect('demande_conge')
    else:
        form = CongeForm()
    
    # Récupérer l'historique des congés de l'employé
    conges = Conge.objects.filter(employe=employe).order_by('-date_debut')
    
    context = {
        'form': form,
        'employe': employe,
        'conges': conges
    }
    
    return render(request, 'personnel/demande_conge.html', context)



def liste_employes(request):
    query = request.GET.get('q')

    employes = Employe.objects.select_related('departement').all()

    if query:
        employes = employes.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(poste__icontains=query) |
            Q(departement__nom__icontains=query)
        )

    context = {
        'employes': employes,
        'query': query
    }
    return render(request, 'personnel/liste_employes.html', context)


def is_admin_rh(user):
    """Vérifie si l'utilisateur est admin RH"""
    return hasattr(user, 'employe') and user.employe.role == 'admin_rh'

@login_required
@user_passes_test(is_admin_rh)
def employes_list(request):
    """Liste tous les employés avec recherche et filtres"""
    
    query = request.GET.get('q', '')
    statut_filter = request.GET.get('statut', '')
    departement_filter = request.GET.get('departement', '')
    
    employes = Employe.objects.select_related('departement').all()
    
    # Filtre de recherche (nom, prénom, email, téléphone, matricule, poste)
    if query:
        employes = employes.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(telephone__icontains=query) |
            Q(matricule__icontains=query) |
            Q(poste__icontains=query)
        )
    
    # Filtre par statut
    if statut_filter:
        employes = employes.filter(statut=statut_filter)
    
    # Filtre par département
    if departement_filter:
        employes = employes.filter(departement_id=departement_filter)
    
    # Tri par nom
    employes = employes.order_by('nom', 'prenom')
    
    context = {
        'employes': employes,
        'query': query,
        'statut_filter': statut_filter,
        'departement_filter': departement_filter,
        'departements': Departement.objects.all(),
        'statuts_choices': Employe._meta.get_field('statut').choices
    }
    
    return render(request, 'personnel/employes_list.html', context)


@login_required
@user_passes_test(is_admin_rh)
def employe_create(request):
    """Créer un nouvel employé"""
    
    password_errors = []
 
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
 
        # Validation des mots de passe
        if not password1:
            password_errors.append('Le mot de passe est obligatoire.')
        elif len(password1) < 8:
            password_errors.append('Le mot de passe doit contenir au moins 8 caractères.')
        elif password1 != password2:
            password_errors.append('Les mots de passe ne correspondent pas.')

 
        if form.is_valid() and not password_errors:
            email = form.cleaned_data['email']
 
            # Vérifier que l'email n'est pas déjà utilisé comme username
            if User.objects.filter(username=email).exists():
                form.add_error('email', 'Un compte avec cet email existe déjà.')
            else:
                # Créer le User Django
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password1
                )
 
                # Créer l'employé lié au User
                employe = form.save(commit=False)
                employe.user = user
                employe.statut = employe.statut or 'actif'
                employe.save()
 
                messages.success(request, f'Employé {employe.prenom} {employe.nom} ajouté avec succès !')
                return redirect('employes_list')
        else:
            if not password_errors:
                messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = EmployeForm()
 
    return render(request, 'personnel/employe_form.html', {
        'form': form,
        'action': 'create',
        'title': 'Ajouter un employé',
        'password_errors': password_errors,
    })
                
                
                
                

@login_required
@user_passes_test(is_admin_rh)
def employe_detail(request, pk):
    """Voir les détails d'un employé"""
    
    employe = get_object_or_404(Employe.objects.select_related('departement', 'user'), pk=pk)
    
    # Stats de l'employé
    conges = employe.conges.all().order_by('-date_debut')[:5]
    presences = employe.presences.filter(date__month=date.today().month).order_by('-date')[:10]
    
    context = {
        'employe': employe,
        'conges': conges,
        'presences': presences
    }
    
    return render(request, 'personnel/employe_detail.html', context)


@login_required
@user_passes_test(is_admin_rh)
def employe_update(request, pk):
    """Modifier un employé"""
    
    employe = get_object_or_404(Employe, pk=pk)
    
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            # Mettre à jour l'email dans le User lié si nécessaire
            if employe.user:
                employe.user.email = employe.email
                employe.user.username = employe.email
                employe.user.save()
            messages.success(request, f'Employé {employe.prenom} {employe.nom} modifié avec succès !')
            return redirect('employes_list')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = EmployeForm(instance=employe)
    
    return render(request, 'personnel/employe_form.html', {
        'form': form,
        'action': 'update',
        'title': f'Modifier {employe.prenom} {employe.nom}',
        'employe': employe
    })


@login_required
@user_passes_test(is_admin_rh)
def employe_delete(request, pk):
    """Supprimer un employé (avec confirmation)"""
    
    employe = get_object_or_404(Employe, pk=pk)
    
    if request.method == 'POST':
        nom = employe.nom
        # Supprimer aussi l'utilisateur lié
        if employe.user:
            employe.user.delete()
        else:
            employe.delete()
        messages.success(request, f'Employé {nom} supprimé avec succès !')
        return redirect('employes_list')
    
    return render(request, 'personnel/employe_confirm_delete.html', {'employe': employe})