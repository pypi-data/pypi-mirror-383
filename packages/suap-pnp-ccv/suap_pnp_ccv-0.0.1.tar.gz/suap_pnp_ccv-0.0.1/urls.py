from django.urls import path
from . import views

urlpatterns = [
    path('sincronizacao_inicial/', views.sincronizacao_inicial),
    path('importar_dados/', views.importar_dados),
    path('exportar_dados/', views.exportar_dados),
    path('alunos_ciclo/<int:pk>/', views.alunos_ciclo),
    path('inscritos_ciclo/<int:pk>/', views.inscritos_ciclo),
    path('evadidos_ciclo/<int:pk>/', views.evadidos_ciclo),
]