from django.contrib import admin
from django.urls import path, include  # 'include' é a chave aqui

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Esta é a única linha que precisamos para as contas.
    # Ela diz: "Qualquer URL que comece com 'contas/' deve ser gerenciada pelo arquivo 'users.urls'".
    path('contas/', include('users.urls')),
]