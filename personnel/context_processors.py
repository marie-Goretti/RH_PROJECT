from .models import Conge
 
def conges_count(request):
    """Injecte le nombre de congés en attente dans tous les templates."""
    if request.user.is_authenticated and hasattr(request.user, 'employe'):
        if request.user.employe.role == 'admin_rh':
            return {
                'conges_en_attente_count': Conge.objects.filter(statut='en_attente').count()
            }
    return {'conges_en_attente_count': 0}