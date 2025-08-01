from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Word, UserWordStatus 

# Usamos TemplateView para uma página simples que só precisa de um template.
# Usamos LoginRequiredMixin para garantir que apenas usuários logados possam ver esta página.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


# NOVA VIEW DA SESSÃO DE ESTUDO
class StudySessionView(LoginRequiredMixin, View):
    
    def get(self, request, *args, **kwargs):
        # Lógica para selecionar a palavra
        
        # 1. Encontrar todas as palavras que o usuário já viu.
        palavras_ja_vistas_ids = UserWordStatus.objects.filter(user=request.user).values_list('word__id', flat=True)

        # 2. Encontrar uma palavra nova (que não está na lista de vistas) de forma aleatória.
        #    O '?' no final ordena de forma aleatória no banco de dados.
        palavra_nova = Word.objects.exclude(id__in=palavras_ja_vistas_ids).order_by('?').first()
        
        # Se não houver palavras novas, podemos redirecionar ou mostrar uma mensagem.
        # Por enquanto, vamos apenas focar no caso onde há palavras novas.
        if not palavra_nova:
            # Lógica para quando o vocabulário acabar (faremos depois)
            return render(request, 'session_finished.html')

        # O 'context' é um dicionário que envia informações para o nosso HTML.
        context = {
            'word': palavra_nova
        }
        
        return render(request, 'flashcard.html', context)