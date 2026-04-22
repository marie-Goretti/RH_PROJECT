from .models import Conge, ParametresApp
 
def conges_count(request):
    """Injecte le nombre de congés en attente et les paramètres dans tous les templates."""
    context = {'conges_en_attente_count': 0, 'conges_nouvelles_count': 0, 'app_parametres': ParametresApp.load()}
    if request.user.is_authenticated and hasattr(request.user, 'employe'):
        if request.user.employe.role == 'admin_rh':
            context['conges_en_attente_count'] = Conge.objects.filter(statut='en_attente').count()
        else:
            context['conges_nouvelles_count'] = Conge.objects.filter(
                employe=request.user.employe, 
                statut__in=['approuve', 'refuse'], 
                vu_par_employe=False
            ).count()
    return context