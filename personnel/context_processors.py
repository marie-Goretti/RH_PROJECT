from .models import Conge
 
def conges_count(request):
    """Injecte le nombre de congés en attente dans tous les templates pour RH, et les nouveaux traités pour employé."""
    context = {'conges_en_attente_count': 0, 'conges_nouvelles_count': 0}
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