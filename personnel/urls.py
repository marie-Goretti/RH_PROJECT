from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    path('dashboard/rh/', views.dashboard, name='dashboard'),
    
    path('conges/demander/', views.demande_conge, name='demande_conge'),
    #path('conges/historique/', views.historique_conges, name='historique_conges'),  # optionnel
    path('presence/marquer/', views.marquer_presence, name='marquer_presence'),
    
    path('employes/', views.employes_list, name='employes_list'),
    path('employes/ajouter/', views.employe_create, name='employe_create'),
    path('employes/<int:pk>/details/', views.employe_detail, name='employe_detail'),
    path('employes/<int:pk>/modifier/', views.employe_update, name='employe_update'),
    path('employes/<int:pk>/supprimer/', views.employe_delete, name='employe_delete'),
    #path('employes/search/', views.employes_search, name='employes_search'),
    
]