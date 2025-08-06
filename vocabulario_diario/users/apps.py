from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # Adicione esta função para importar os sinais
    def ready(self):
        import users.signals
