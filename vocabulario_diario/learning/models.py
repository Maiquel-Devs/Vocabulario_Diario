from django.db import models
from django.contrib.auth.models import User # Vamos precisar do modelo de usuário padrão do Django
from django.utils import timezone

# Modelo para guardar cada palavra do vocabulário
class Word(models.Model):
    text_english = models.CharField(max_length=100, unique=True, verbose_name="Palavra em Inglês")
    text_portuguese = models.CharField(max_length=100, verbose_name="Tradução Principal")
    synonyms_portuguese = models.TextField(blank=True, null=True, verbose_name="Sinônimos em Português")
    complexity = models.IntegerField(default=0, verbose_name="Complexidade (Comprimento)")

    def __str__(self):
        return self.text_english
 
    
# --- NOVA ADIÇÃO ---
# Modelo para representar um conjunto de palavras que o usuário errou em um dia.
class TrainingSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    creation_date = models.DateField(default=timezone.now, verbose_name="Data de Criação")
    is_mastered = models.BooleanField(default=False, verbose_name="Conjunto Dominado?")

    def __str__(self):
        return f"Conjunto de Treino de {self.user.username} - {self.creation_date.strftime('%d/%m/%Y')}"

# --- ALTERAÇÃO ---
# O modelo UserWordStatus agora se conecta ao TrainingSet.
class UserWordStatus(models.Model):
    # Lista de opções para o status de aprendizado da palavra
    STATUS_CHOICES = [
        ('Nao Visto', 'Não Visto'),                 # O usuário ainda não teve contato com a palavra
        ('Acertou de Primeira', 'Acertou de Primeira'),  # Acertou logo no primeiro teste
        ('Em Revisao', 'Em Revisão'),               # Ainda está revisando essa palavra (errou ou ainda não domina)
        ('Dominado', 'Dominado'),                   # Já acertou várias vezes e domina a palavra
    ]

    # Relacionamento com o usuário que está aprendendo
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")

    # Relacionamento com a palavra sendo aprendida
    word = models.ForeignKey(Word, on_delete=models.CASCADE, verbose_name="Palavra")

    # Status atual da palavra para o usuário (escolhido dentre os valores definidos acima)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Nao Visto')

    # ------------------------------
    # Campos para o algoritmo de Repetição Espaçada (SRS)
    # ------------------------------

    # Número de acertos consecutivos com essa palavra
    consecutive_correct_answers = models.IntegerField(default=0, verbose_name="Acertos Consecutivos")

    # Próxima data em que a palavra deverá aparecer para revisão
    next_review_date = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Revisão")

    # ------------------------------
    # Campo NOVO: ligação com TrainingSet
    # ------------------------------

    # CAMPO ANTIGO REMOVIDO: 'is_in_training_deck' foi removido
    #
    # Campo NOVO ADICIONADO:
    # Liga esta palavra a um conjunto de treino específico (TrainingSet),
    # normalmente quando o usuário erra a palavra em uma sessão.
    #
    # - null=True e blank=True tornam o campo opcional.
    # - on_delete=models.SET_NULL garante que, se o conjunto de treino for deletado,
    #   o status da palavra não será excluído — apenas desassociado do conjunto.
    # - related_name='words' permite acessar as palavras do conjunto com training_set.words.all()
    training_set = models.ForeignKey(
        TrainingSet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='words'
    )

    # ------------------------------
    # Regras de unicidade
    # ------------------------------

    # Garante que cada par (usuário, palavra) seja único no banco
    class Meta:
        unique_together = ('user', 'word')

    # Representação legível para admin, debug ou logs
    def __str__(self):
        return f"{self.user.username} - {self.word.text_english}: {self.status}"
