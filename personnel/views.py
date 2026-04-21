from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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
    """Vue du tableau de bord Employé - données réelles depuis la BDD"""
    if not hasattr(request.user, 'employe') or request.user.employe.role != 'employe':
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')

    employe = request.user.employe
    today = date.today()
    from datetime import timedelta, datetime

    # ── Présence d'aujourd'hui ──
    presence_aujourd_hui = Presence.objects.filter(employe=employe, date=today).first()

    # ── Stats du mois en cours ──
    presences_mois = Presence.objects.filter(
        employe=employe,
        date__year=today.year,
        date__month=today.month
    )
    nb_presents  = presences_mois.filter(statut__in=['present', 'retard']).count()
    nb_retards   = presences_mois.filter(statut='retard').count()
    nb_absents   = presences_mois.filter(statut='absent').count()

    # ── 7 derniers jours pour le graphique ──
    chart_labels = []
    chart_values = []   # 1=ponctuel, 2=retard, 0=absent, -1=pas de données (week-end)
    chart_colors = []
    JOURS_FR = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    for i in range(6, -1, -1):
        jour = today - timedelta(days=i)
        label = f"{JOURS_FR[jour.weekday()]} {jour.day:02d}"
        chart_labels.append(label)
        p = Presence.objects.filter(employe=employe, date=jour).first()
        if p:
            if p.statut == 'present':
                chart_values.append(1)
                chart_colors.append('#1F7A63')
            elif p.statut == 'retard':
                chart_values.append(2)
                chart_colors.append('#ffc107')
            else:
                chart_values.append(0)
                chart_colors.append('#dc3545')
        else:
            chart_values.append(0)
            chart_colors.append('#E8ECEF')

    # ── Historique du mois ──
    historique = presences_mois.order_by('-date')

    # ── Congés en cours / à venir ──
    conges_actifs = employe.conges.filter(
        date_fin__gte=today,
        statut='approuve'
    ).order_by('date_debut')[:3]

    import json
    context = {
        'employe': employe,
        'today': today,
        'presence_aujourd_hui': presence_aujourd_hui,
        'nb_presents': nb_presents,
        'nb_retards': nb_retards,
        'nb_absents': nb_absents,
        'historique': historique,
        'conges_actifs': conges_actifs,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_values_json': json.dumps(chart_values),
        'chart_colors_json': json.dumps(chart_colors),
    }
    return render(request, 'personnel/dashboard_employe.html', context)


@login_required
def marquer_presence(request):
    """Endpoint AJAX : marque la présence de l'employé une seule fois par jour"""
    import json
    from datetime import datetime, time as dtime

    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    if not hasattr(request.user, 'employe'):
        return JsonResponse({'error': 'Accès refusé'}, status=403)

    employe = request.user.employe
    today = date.today()

    # Vérifier si déjà pointé aujourd'hui
    if Presence.objects.filter(employe=employe, date=today).exists():
        return JsonResponse({'error': 'already_marked'}, status=400)

    # Déterminer le statut selon l'heure
    now_time = datetime.now().time()
    heure_limite = dtime(8, 0)
    statut = 'present' if now_time <= heure_limite else 'retard'

    presence = Presence.objects.create(
        employe=employe,
        date=today,
        heure_arrivee=now_time,
        statut=statut,
        commentaire=''
    )

    return JsonResponse({
        'success': True,
        'statut': statut,
        'heure': now_time.strftime('%H:%M'),
        'date': today.strftime('%d/%m/%Y'),
    })


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
    
    # Départements (pour le graphique et les filtres)
    departements = Departement.objects.all()
    
    context = {
        'employe': request.user.employe,
        'employes': employes,
        'total_employes': total_employes,
        'presences_aujourdhui': presences_aujourdhui,
        'retards_aujourdhui': retards_aujourdhui,
        'conges_en_attente': conges_en_attente,
        'departements': departements,
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
    from datetime import date
    from django.db.models import Prefetch
    
    query = request.GET.get('q', '')
    assiduite_filter = request.GET.get('assiduite', '')
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
    
    today = date.today()
    
    # Filtre par assiduité (présence d'aujourd'hui)
    if assiduite_filter:
        if assiduite_filter == 'non_pointe':
            employes = employes.exclude(presences__date=today)
        else:
            employes = employes.filter(presences__date=today, presences__statut=assiduite_filter)
    
    # Filtre par département
    if departement_filter:
        employes = employes.filter(departement_id=departement_filter)
    
    # Tri par nom
    employes = employes.order_by('nom', 'prenom')
    
    # Charger la présence d'aujourd'hui
    presences_today = Presence.objects.filter(date=today)
    employes = employes.prefetch_related(
        Prefetch('presences', queryset=presences_today, to_attr='presence_today')
    )
    
    context = {
        'employes': employes,
        'query': query,
        'assiduite_filter': assiduite_filter,
        'departement_filter': departement_filter,
        'departements': Departement.objects.all(),
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




@login_required
@user_passes_test(is_admin_rh)
def gestion_conges(request):
    """
    Vue RH : liste toutes les demandes de congé avec filtres par statut.
    Remplace demande_conge() pour les admins RH.
    """
    statut_actif = request.GET.get('statut', 'en_attente')

    # Base queryset avec les relations
    conges_qs = Conge.objects.select_related(
        'employe', 'employe__departement'
    ).order_by('-date_debut')

    # Compteurs globaux (avant filtre)
    nb_en_attente = conges_qs.filter(statut='en_attente').count()
    nb_approuve   = conges_qs.filter(statut='approuve').count()
    nb_refuse     = conges_qs.filter(statut='refuse').count()
    total         = conges_qs.count()

    # Filtre selon l'onglet actif
    if statut_actif != 'tous':
        conges_qs = conges_qs.filter(statut=statut_actif)

    # Injecter le nombre de jours sur chaque objet (sans modifier le modèle)
    for conge in conges_qs:
        conge.nb_jours = (conge.date_fin - conge.date_debut).days + 1

    context = {
        'conges':        conges_qs,
        'statut_actif':  statut_actif,
        'nb_en_attente': nb_en_attente,
        'nb_approuve':   nb_approuve,
        'nb_refuse':     nb_refuse,
        'total':         total,
        'employe':       request.user.employe,   # pour la sidebar
    }
    return render(request, 'personnel/gestion_conges.html', context)


@login_required
@user_passes_test(is_admin_rh)
def conge_action(request, pk, action):
    """
    Endpoint POST : approuver ou refuser un congé.
    action ∈ {'approuver', 'refuser'}
    """
    if request.method != 'POST':
        return redirect('gestion_conges')

    conge = get_object_or_404(Conge, pk=pk)

    if conge.statut != 'en_attente':
        messages.warning(request, 'Cette demande a déjà été traitée.')
        return redirect('gestion_conges')

    if action == 'approuver':
        conge.statut = 'approuve'
        conge.commentaire = ''
        conge.save()
        messages.success(
            request,
            f'Congé de {conge.employe.prenom} {conge.employe.nom} approuvé avec succès !'
        )

    elif action == 'refuser':
        commentaire = request.POST.get('commentaire', '').strip()
        if not commentaire:
            messages.error(request, 'Veuillez saisir un motif de refus.')
            return redirect(f'{request.META.get("HTTP_REFERER", "/conges/gestion/")}')
        conge.statut     = 'refuse'
        conge.commentaire = commentaire
        conge.save()
        messages.success(
            request,
            f'Congé de {conge.employe.prenom} {conge.employe.nom} refusé.'
        )

    # Rester sur l'onglet actif
    statut_qs = request.POST.get('statut_actif', 'en_attente')
    return redirect(f'/conges/gestion/?statut={statut_qs}')