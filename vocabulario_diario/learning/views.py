from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Word, UserWordStatus
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
import json 


# Usamos TemplateView para uma página simples que só precisa de um template.
# Usamos LoginRequiredMixin para garantir que apenas usuários logados possam ver esta página.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


# VIEW INTELIGENTE DA SESSÃO DE ESTUDO
class StudySessionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # --- LÓGICA DE ESCOLHA DA PALAVRA (com prioridade de revisão) ---

        # PRIORIDADE 1: Buscar palavras que precisam de revisão (SRS - Spaced Repetition System)
        # Aqui selecionamos palavras com status "Em Revisao" ou "Dominado",
        # cuja data de revisão (`next_review_date`) já venceu.
        # Usamos `order_by('next_review_date')` para priorizar a revisão mais antiga.
        palavras_para_revisar = UserWordStatus.objects.filter(
            user=user,
            status__in=['Em Revisao', 'Dominado'],
            next_review_date__lte=timezone.now()
        ).order_by('next_review_date')  # Palavra mais "urgente" de revisar primeiro

        word_to_study = None  # Inicializamos como None; será preenchido com a palavra selecionada.

        if palavras_para_revisar.exists():
            # Se há palavras para revisar, selecionamos a primeira (mais antiga)
            word_to_study = palavras_para_revisar.first().word
        else:
            # PRIORIDADE 2: Buscar palavras novas (caso a meta diária permita - essa lógica virá depois)
            
            # Encontrar todas as palavras que o usuário já viu (via status).
            palavras_ja_vistas_ids = UserWordStatus.objects.filter(
                user=user
            ).values_list('word__id', flat=True)

            # Selecionar uma nova palavra aleatória (que ainda não foi vista pelo usuário).
            # O uso de `.order_by('?')` faz o banco escolher uma palavra aleatoriamente.
            palavra_nova = Word.objects.exclude(id__in=palavras_ja_vistas_ids).order_by('?').first()
            
            if palavra_nova:
                word_to_study = palavra_nova

        # Caso não haja nenhuma palavra para revisar ou aprender, a sessão está finalizada.
        if not word_to_study:
            return render(request, 'session_finished.html')

        # Contexto enviado para o template HTML do flashcard.
        context = {
            'word': word_to_study
        }
        
        return render(request, 'flashcard.html', context)

    

class CheckAnswerView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        # Carregamos os dados enviados pelo JavaScript
        data = json.loads(request.body)
        word_id = data.get('word_id')
        user_answer = data.get('user_answer')

        # Buscamos a palavra correta no banco de dados
        word = get_object_or_404(Word, id=word_id)

        # Lógica de verificação flexível (simplificada por enquanto)
        is_correct = user_answer.strip().lower() == word.text_portuguese.strip().lower()
        
        # --- LÓGICA DE SALVAR O PROGRESSO ---
        # Usamos get_or_create para criar um novo status se ele não existir,
        # ou pegar o existente se o usuário já viu esta palavra.
        status, created = UserWordStatus.objects.get_or_create(
            user=request.user,
            word=word
        )

        # Se a resposta estiver correta...
        if is_correct:
            if created: # Se foi a primeira vez que ele viu a palavra e acertou
                status.status = 'Acertou de Primeira'
            
            status.status = 'Dominado' # Simplificando por enquanto, vamos refinar depois
            status.consecutive_correct_answers += 1
            # Lógica simples de SRS: próxima revisão daqui a N dias
            # onde N é o número de acertos consecutivos.
            status.next_review_date = timezone.now() + timedelta(days=status.consecutive_correct_answers)
            status.is_in_training_deck = False

        # Se a resposta estiver errada...
        else:
            status.status = 'Em Revisao'
            status.consecutive_correct_answers = 0 # Zera a contagem
            status.next_review_date = timezone.now() + timedelta(minutes=10) # Revisar logo
            status.is_in_training_deck = True

        status.save() # Salva as alterações no banco de dados!

        # Retornamos uma resposta em formato JSON
        return JsonResponse({'correct': is_correct, 'correct_answer': word.text_portuguese})
    

# NOVA VIEW PARA O BOTÃO "DEFINIR COMO CORRETA"
class MarkAsCorrectView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_id = data.get('word_id')

        word = get_object_or_404(Word, id=word_id)

        # Encontramos o status da palavra que foi marcada como 'Em Revisao'
        status, created = UserWordStatus.objects.get_or_create(
            user=request.user,
            word=word
        )
        
        # Revertemos o erro. A lógica é a mesma de um acerto.
        status.status = 'Dominado' # Simplificando por enquanto
        status.consecutive_correct_answers += 1
        status.next_review_date = timezone.now() + timedelta(days=status.consecutive_correct_answers)
        status.is_in_training_deck = False

        status.save()

        # Retornamos uma resposta de sucesso
        return JsonResponse({'status': 'success', 'message': 'Progresso atualizado com sucesso.'})
    

# NOVA VIEW PARA O PAINEL DE CONTROLE
class DashboardView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user

        # Fazemos as consultas no banco de dados para calcular as estatísticas
        
        # Palavras que o usuário acertou na primeira vez que viu
        palavras_ja_sabe = UserWordStatus.objects.filter(
            user=user, 
            status='Acertou de Primeira'
        ).count()

        # Palavras que o usuário errou, treinou e agora dominou
        palavras_aprendidas_com_esforco = UserWordStatus.objects.filter(
            user=user, 
            status='Dominado'
        ).count()
        
        # Palavras que estão ativamente no ciclo de revisão
        palavras_em_revisao = UserWordStatus.objects.filter(
            user=user, 
            status='Em Revisao'
        ).count()

        # O vocabulário total é a soma das que ele já sabia com as que aprendeu
        vocabulario_total = palavras_ja_sabe + palavras_aprendidas_com_esforco

        context = {
            'palavras_ja_sabe': palavras_ja_sabe,
            'palavras_aprendidas_com_esforco': palavras_aprendidas_com_esforco,
            'palavras_em_revisao': palavras_em_revisao,
            'vocabulario_total': vocabulario_total,
        }

        return render(request, 'dashboard.html', context)
 
    
# NOVA VIEW PARA FORNECER DADOS PARA O GRÁFICO
class DashboardChartDataView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user

        # Agrupamos os status por data de criação para ver o progresso diário
        # Contamos apenas as palavras que foram movidas para 'Acertou de Primeira' ou 'Dominado'
        progress_data = UserWordStatus.objects.filter(
            user=user,
            status__in=['Acertou de Primeira', 'Dominado']
        ).annotate(
            date=TruncDate('next_review_date') # Usamos a data da próxima revisão para marcar o dia
        ).values('date').annotate(
            words_learned_on_day=Count('id')
        ).order_by('date')

        # Formatamos os dados para o gráfico
        labels = [] # As datas (ex: '2025-08-02')
        cumulative_data = [] # O número acumulado de palavras
        total_learned = 0

        for entry in progress_data:
            if entry['date']: # Ignora entradas sem data
                total_learned += entry['words_learned_on_day']
                labels.append(entry['date'].strftime('%d/%m/%Y'))
                cumulative_data.append(total_learned)

        data = {
            'labels': labels,
            'data': cumulative_data,
        }

        return JsonResponse(data)
    

# NOVA VIEW PARA A SESSÃO DE TREINO FOCADO
class TrainingSessionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user = request.user

        # A lógica aqui é mais simples: buscamos apenas as palavras
        # que estão marcadas para o deck de treino.
        palavras_para_treinar = UserWordStatus.objects.filter(
            user=user,
            is_in_training_deck=True
        )

        # Se não houver palavras para treinar, mostramos uma mensagem.
        if not palavras_para_treinar.exists():
            return render(request, 'training_finished.html')

        # Pegamos uma palavra aleatória da lista de treino
        palavra_selecionada_status = palavras_para_treinar.order_by('?').first()
        word_to_study = palavra_selecionada_status.word

        context = {
            'word': word_to_study,
            # Indicamos que esta é uma sessão de treino
            'is_training_session': True, 
        }
        
        # Nós podemos reutilizar o mesmo template do flashcard!
        return render(request, 'flashcard.html', context)
    

# NOVA VIEW PARA REMOVER UMA PALAVRA DO TREINO
class RemoveFromTrainingView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_id = data.get('word_id')

        # Encontramos o status da palavra e o atualizamos
        status = get_object_or_404(UserWordStatus, user=request.user, word_id=word_id)

        # Tiramos ela do deck de treino e consideramos como "graduada"
        status.is_in_training_deck = False
        # Vamos ser conservadores e apenas zerar os acertos, para que o SRS normal decida o futuro dela
        status.consecutive_correct_answers = 0
        # Marcamos para uma revisão normal em 1 dia para confirmar
        status.next_review_date = timezone.now() + timedelta(days=1)

        status.save()

        return JsonResponse({'status': 'success', 'message': 'Palavra removida do treino.'})