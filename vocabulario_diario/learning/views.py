from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Usamos TemplateView para uma página simples que só precisa de um template.
# Usamos LoginRequiredMixin para garantir que apenas usuários logados possam ver esta página.
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'