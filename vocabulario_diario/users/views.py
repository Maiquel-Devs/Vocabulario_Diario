from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

class SignUpView(generic.CreateView):
    # O formulário que vamos usar é o formulário de criação de usuário padrão do Django.
    # Ele já vem com os campos de "usuário", "senha" e "confirmação de senha".
    form_class = UserCreationForm
    
    # Em caso de sucesso no cadastro, o usuário será redirecionado para a página de login.
    # 'reverse_lazy' é a forma correta de fazer isso em class-based views.
    success_url = reverse_lazy('login')
    
    # O arquivo HTML que será usado para renderizar esta página.
    template_name = 'registration/signup.html'