from django.db import models
from django.contrib.auth.models import User # Vamos precisar do modelo de usuário padrão do Django

# Modelo para guardar cada palavra do vocabulário
class Word(models.Model):
    text_english = models.CharField(max_length=100, unique=True, verbose_name="Palavra em Inglês")
    text_portuguese = models.CharField(max_length=100, verbose_name="Tradução Principal")
    synonyms_portuguese = models.TextField(blank=True, null=True, verbose_name="Sinônimos em Português")
    complexity = models.IntegerField(default=0, verbose_name="Complexidade (Comprimento)")

    def __str__(self):
        return self.text_english

# Modelo para rastrear o progresso de CADA palavra para CADA usuário
class UserWordStatus(models.Model):
    # Definindo as opções para o campo 'status'
    STATUS_CHOICES = [
        ('Nao Visto', 'Não Visto'),
        ('Acertou de Primeira', 'Acertou de Primeira'),
        ('Em Revisao', 'Em Revisão'),
        ('Dominado', 'Dominado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name="Palavra")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Nao Visto')
    
    # Campos para o nosso algoritmo de Repetição Espaçada (SRS)
    consecutive_correct_answers = models.IntegerField(default=0, verbose_name="Acertos Consecutivos")
    next_review_date = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Revisão")
    is_in_training_deck = models.BooleanField(default=False, verbose_name="Está no Deck de Treino?")

    # Garante que cada usuário só tenha um status para cada palavra
    class Meta:
        unique_together = ('user', 'word')

    def __str__(self):
        return f"{self.user.username} - {self.word.text_english}: {self.status}"