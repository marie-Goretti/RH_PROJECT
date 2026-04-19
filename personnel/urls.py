
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('conges/demande/', views.demande_conge, name='demande_conge'),

]