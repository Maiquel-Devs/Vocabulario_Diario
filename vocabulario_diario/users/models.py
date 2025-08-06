from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # Cria uma relação de um-para-um com o modelo de utilizador padrão do Django.
    # Cada utilizador terá exatamente um perfil.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Campo para guardar a meta diária de domínio do utilizador.
    # `default=10` significa que, se o utilizador não definir uma meta, será 10.
    daily_goal = models.IntegerField(default=10, verbose_name="Meta Diária de Domínio")

    def __str__(self):
        return f"Perfil de {self.user.username}"