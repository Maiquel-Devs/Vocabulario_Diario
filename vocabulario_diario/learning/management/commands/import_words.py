import pandas as pd
from django.core.management.base import BaseCommand
from learning.models import Word

class Command(BaseCommand):
    help = 'Importa palavras de um arquivo XLSX (Excel) para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('xlsx_file_path', type=str, help='O caminho para o arquivo XLSX')

    def handle(self, *args, **kwargs):
        file_path = kwargs['xlsx_file_path']
        self.stdout.write(f"Iniciando a importação do arquivo Excel: {file_path}")

        try:
            df = pd.read_excel(file_path)

            palavras_criadas = 0
            palavras_existentes = 0

            for index, row in df.iterrows():
                if 'Sig_Ingles' not in row or 'Sig_Portugues' not in row or 'Complexidade_Comprimento' not in row:
                    self.stdout.write(self.style.WARNING(f"Aviso: Linha {index+2} ignorada por não conter as colunas necessárias."))
                    continue
                
                word, created = Word.objects.get_or_create(
                    text_english=row['Sig_Ingles'],
                    defaults={
                        'text_portuguese': row['Sig_Portugues'],
                        'complexity': int(row['Complexidade_Comprimento']),
                    }
                )

                if created:
                    palavras_criadas += 1
                else:
                    palavras_existentes += 1
            
            self.stdout.write(self.style.SUCCESS(f"\nImportação concluída!"))
            # LINHA CORRIGIDA ABAIXO
            self.stdout.write(f"{palavras_criadas} novas palavras foram adicionadas.")
            self.stdout.write(f"{palavras_existentes} palavras já existiam no banco de dados.")

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("Erro: Arquivo não encontrado. Verifique o caminho."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocorreu um erro inesperado: {e}"))