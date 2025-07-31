from django.urls import path
from . import views  # Importa as views do app 'users'
from . import views as user_views # Renomeamos nossas views para evitar conflito de nome
from django.contrib.auth import views as auth_views # Importamos as views de autenticação do Django



urlpatterns = [
    # O Django já sabe que estamos dentro de "/contas/".
    # Então, esta linha corresponde à URL final "/contas/cadastro/".
    # Demos o nome 'signup' para esta rota.
    path('cadastro/', views.SignUpView.as_view(), name='signup'),

    # Rota de Login
    # Usamos a LoginView pronta do Django. Só precisamos dizer a ela qual template usar.
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Rota de Logout
    # A LogoutView do Django é tão simples que nem precisa de um template.
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]