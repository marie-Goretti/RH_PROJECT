
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, CongeForm
from .models import Employe, Conge, Presence
from datetime import date
from django.db.models import Count, Q

def register_view(request):
    """Vue pour l'inscription"""
    
    if request.user.is_authenticated:
        # Si l'utilisateur est déjà connecté, rediriger
        if hasattr(request.user, 'employe'):
            if request.user.employe.role == 'admin_rh':
                return redirect('dashboard_rh')
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
                    return redirect('dashboard_rh')
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
                return redirect('dashboard_rh')
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
                        return redirect('dashboard_rh')
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


@login_required
def dashboard(request):
    """Vue temporaire pour le tableau de bord général"""
    return render(request, 'personnel/dashboard.html')


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
def dashboard_rh(request):
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
    
    return render(request, 'personnel/dashboard_rh.html', context)


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