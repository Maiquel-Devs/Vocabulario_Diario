# learning/views.py

import json
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Word, UserWordStatus, TrainingSet, DailyMasteryLog

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class StudySessionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        palavras_para_revisar = UserWordStatus.objects.filter(
            user=user, status__in=['Em Revisao', 'Dominado'], next_review_date__lte=timezone.now()
        ).order_by('next_review_date')
        word_to_study = None
        if palavras_para_revisar.exists():
            word_to_study = palavras_para_revisar.first().word
        else:
            palavras_ja_vistas_ids = UserWordStatus.objects.filter(user=user).values_list('word__id', flat=True)
            palavra_nova = Word.objects.exclude(id__in=palavras_ja_vistas_ids).order_by('?').first()
            if palavra_nova:
                word_to_study = palavra_nova
        if not word_to_study:
            return render(request, 'session_finished.html')
        context = {'word': word_to_study, 'is_training_session': False}
        return render(request, 'flashcard.html', context)

class TrainingSetListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        training_sets = TrainingSet.objects.filter(
            user=user, 
            is_mastered=False,
            words__isnull=False
        ).distinct().order_by('creation_date')
        daily_goal = user.profile.daily_goal
        log_hoje = DailyMasteryLog.objects.filter(user=user, date=timezone.now().date()).first()
        progresso_hoje = log_hoje.mastered_words_count if log_hoje else 0
        progresso_percentagem = int((progresso_hoje / daily_goal) * 100) if daily_goal > 0 else 0
        if progresso_percentagem > 100:
            progresso_percentagem = 100
        context = {'training_sets': training_sets, 'daily_goal': daily_goal, 'progresso_hoje': progresso_hoje, 'progresso_percentagem': progresso_percentagem}
        return render(request, 'training_set_list.html', context)

class TrainingSessionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        set_id = kwargs.get('set_id')
        training_set = get_object_or_404(TrainingSet, id=set_id, user=user)
        palavras_para_treinar = UserWordStatus.objects.filter(training_set=training_set)
        session_key = f'training_set_{set_id}_correct_words'
        palavras_corretas_na_sessao = request.session.get(session_key, [])
        palavras_pendentes = palavras_para_treinar.exclude(word__id__in=palavras_corretas_na_sessao)
        if not palavras_pendentes.exists():
            context = {'training_set': training_set}
            request.session.pop(session_key, None)
            return render(request, 'training_set_mastered.html', context)
        palavra_selecionada_status = palavras_pendentes.order_by('?').first()
        word_to_study = palavra_selecionada_status.word
        context = {'word': word_to_study, 'is_training_session': True, 'set_id': set_id}
        return render(request, 'flashcard.html', context)

class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        palavras_ja_sabe = UserWordStatus.objects.filter(user=user, status='Acertou de Primeira').count()
        palavras_dominadas = UserWordStatus.objects.filter(user=user, status='Dominado').count()
        palavras_em_revisao = UserWordStatus.objects.filter(user=user, training_set__is_mastered=False).count()
        vocabulario_total = palavras_ja_sabe + palavras_dominadas
        context = {'palavras_ja_sabe': palavras_ja_sabe, 'palavras_aprendidas_com_esforco': palavras_dominadas, 'palavras_em_revisao': palavras_em_revisao, 'vocabulario_total': vocabulario_total}
        return render(request, 'dashboard.html', context)

class CheckAnswerView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_id = data.get('word_id')
        user_answer = data.get('user_answer')
        word = get_object_or_404(Word, id=word_id)
        is_correct = user_answer.strip().lower() == word.text_portuguese.strip().lower()
        status, created = UserWordStatus.objects.get_or_create(user=request.user, word=word)
        if is_correct:
            if status.training_set:
                status.consecutive_correct_answers += 1
                set_id = status.training_set.id
                session_key = f'training_set_{set_id}_correct_words'
                palavras_corretas_na_sessao = request.session.get(session_key, [])
                if status.word.id not in palavras_corretas_na_sessao:
                    palavras_corretas_na_sessao.append(status.word.id)
                request.session[session_key] = palavras_corretas_na_sessao
            else:
                status.status = 'Acertou de Primeira' if created else 'Dominado'
                status.consecutive_correct_answers += 1
                status.next_review_date = timezone.now() + timedelta(days=status.consecutive_correct_answers)
                status.training_set = None
        else:
            status.status = 'Em Revisao'
            status.consecutive_correct_answers = 0
            status.next_review_date = timezone.now() + timedelta(minutes=10)
            today_set = TrainingSet.objects.filter(user=request.user, creation_date=timezone.now().date(), is_mastered=False).first()
            if not today_set:
                today_set = TrainingSet.objects.create(user=request.user, creation_date=timezone.now().date())
            status.training_set = today_set
        status.save()
        return JsonResponse({'correct': is_correct, 'correct_answer': word.text_portuguese})

class MarkAsCorrectView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        word_id = data.get('word_id')
        word = get_object_or_404(Word, id=word_id)
        status, created = UserWordStatus.objects.get_or_create(user=request.user, word=word)
        status.status = 'Dominado'
        status.consecutive_correct_answers = 1
        status.next_review_date = timezone.now() + timedelta(days=1)
        status.training_set = None # Remove a palavra de qualquer conjunto
        status.save()
        return JsonResponse({'status': 'success'})

class MasterSetView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        set_id = data.get('set_id')
        training_set = get_object_or_404(TrainingSet, id=set_id, user=request.user)
        word_count = UserWordStatus.objects.filter(training_set=training_set).count()
        if word_count > 0:
            log, created = DailyMasteryLog.objects.get_or_create(
                user=request.user, date=timezone.now().date(), defaults={'mastered_words_count': 0}
            )
            log.mastered_words_count += word_count
            log.save()
        training_set.is_mastered = True
        training_set.save()
        words_in_set = UserWordStatus.objects.filter(training_set=training_set)
        for status in words_in_set:
            status.status = 'Dominado'
            status.training_set = None
            status.consecutive_correct_answers = 1
            status.next_review_date = timezone.now() + timedelta(days=1)
            status.save()
        return JsonResponse({'status': 'success'})

class DashboardChartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        progress_data = UserWordStatus.objects.filter(user=user, status__in=['Acertou de Primeira', 'Dominado']).exclude(next_review_date__isnull=True).annotate(date=TruncDate('next_review_date')).values('date').annotate(words_learned_on_day=Count('id')).order_by('date')
        labels, cumulative_data, total_learned = [], [], 0
        for entry in progress_data:
            if entry['date']:
                total_learned += entry['words_learned_on_day']
                labels.append(entry['date'].strftime('%d/%m/%Y'))
                cumulative_data.append(total_learned)
        data = {'labels': labels, 'data': cumulative_data}
        return JsonResponse(data)