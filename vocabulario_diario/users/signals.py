from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# Este "receiver" escuta pelo sinal "post_save" do modelo User.
# Ou seja, ele é acionado toda vez que um User é salvo.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # Se um novo utilizador foi CRIADO (`created` is True)...
    if created:
        # ...cria um perfil para ele.
        Profile.objects.create(user=instance)