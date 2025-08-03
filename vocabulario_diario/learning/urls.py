from django.urls import path
from . import views

urlpatterns = [
    # Esta rota corresponde à página inicial do nosso site (ex: http://127.0.0.1:8000/)
    # Demos a ela o nome 'home', o mesmo que usamos no LOGIN_REDIRECT_URL.
    path('', views.HomeView.as_view(), name='home'),

    # ROTA PARA O PAINEL DE CONTROLE
    path('painel/', views.DashboardView.as_view(), name='dashboard'),

    # ROTA PARA A LISTA DE CONJUNTOS DE TREINO
    path('treinos/', views.TrainingSetListView.as_view(), name='training_set_list'),

    # ROTA PARA A SESSÃO DE ESTUDO
    path('sessao-de-estudo/', views.StudySessionView.as_view(), name='study_session'),

    # ROTA PARA A SESSÃO DE TREINO (com ID do conjunto)
    path('sessao-de-treino/<int:set_id>/', views.TrainingSessionView.as_view(), name='training_session'),
    
    # --- ROTAS DE API ---
    
    # API PARA VERIFICAR A RESPOSTA DO USUÁRIO (durante sessão de estudo ou treino)
    path('api/check-answer/', views.CheckAnswerView.as_view(), name='check_answer'),

    # API PARA MARCAR UMA PALAVRA COMO CORRETA MANUALMENTE
    path('api/mark-as-correct/', views.MarkAsCorrectView.as_view(), name='mark_as_correct'),

    # API PARA MARCAR UM CONJUNTO COMO DOMINADO
    path('api/master-set/', views.MasterSetView.as_view(), name='master_set'),

    # API PARA OBTER OS DADOS DO GRÁFICO DO PAINEL
    path('api/chart-data/', views.DashboardChartDataView.as_view(), name='chart_data'),
]
