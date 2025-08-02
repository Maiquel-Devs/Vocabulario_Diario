from django.urls import path
from . import views

urlpatterns = [
    # Esta rota corresponde à página inicial do nosso site (ex: http://127.0.0.1:8000/)
    # Demos a ela o nome 'home', o mesmo que usamos no LOGIN_REDIRECT_URL.
    path('', views.HomeView.as_view(), name='home'),

    # NOVA ROTA PARA A SESSÃO DE ESTUDO
    path('sessao-de-estudo/', views.StudySessionView.as_view(), name='study_session'),

    # NOVA ROTA PARA A NOSSA API
    path('api/check-answer/', views.CheckAnswerView.as_view(), name='check_answer'),

    # NOVA ROTA PARA A API DE CORREÇÃO MANUAL
    path('api/mark-as-correct/', views.MarkAsCorrectView.as_view(), name='mark_as_correct'),

    # NOVA ROTA PARA O PAINEL DE CONTROLE
    path('painel/', views.DashboardView.as_view(), name='dashboard'),

    # NOVA ROTA PARA A API DO GRÁFICO
    path('api/chart-data/', views.DashboardChartDataView.as_view(), name='chart_data'),

    # NOVA ROTA PARA A SESSÃO DE TREINO
    path('sessao-de-treino/', views.TrainingSessionView.as_view(), name='training_session'),

    # NOVA ROTA PARA A API DE REMOÇÃO DO TREINO
    path('api/remove-from-training/', views.RemoveFromTrainingView.as_view(), name='remove_from_training'),
]