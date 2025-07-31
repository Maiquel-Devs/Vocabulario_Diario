from django.urls import path
from . import views

urlpatterns = [
    # Esta rota corresponde à página inicial do nosso site (ex: http://127.0.0.1:8000/)
    # Demos a ela o nome 'home', o mesmo que usamos no LOGIN_REDIRECT_URL.
    path('', views.HomeView.as_view(), name='home'),
]