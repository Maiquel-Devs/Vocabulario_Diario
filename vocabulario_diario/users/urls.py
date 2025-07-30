from django.urls import path
from . import views  # Importa as views do app 'users'

urlpatterns = [
    # O Django já sabe que estamos dentro de "/contas/".
    # Então, esta linha corresponde à URL final "/contas/cadastro/".
    # Demos o nome 'signup' para esta rota.
    path('cadastro/', views.SignUpView.as_view(), name='signup'),
]