# users/views.py

from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic, View
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from learning.models import UserWordStatus, TrainingSet, DailyMasteryLog
from .forms import ProfileForm
from .models import Profile
from django.contrib.auth import logout

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class SettingsView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'registration/settings.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, 'A sua meta foi atualizada com sucesso!')
        return super().form_valid(form)

class ResetProgressView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user_to_reset = request.user
        UserWordStatus.objects.filter(user=user_to_reset).delete()
        TrainingSet.objects.filter(user=user_to_reset).delete()
        DailyMasteryLog.objects.filter(user=user_to_reset).delete()
        
        try:
            profile = user_to_reset.profile
            profile.daily_goal = 10
            profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=user_to_reset, daily_goal=10)

        return JsonResponse({'status': 'success', 'message': 'Progresso reiniciado com sucesso.'})
   
    
class LogoutAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logout realizado com sucesso.'})