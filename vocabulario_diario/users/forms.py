from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['daily_goal']
        labels = {
            'daily_goal': 'Sua meta diária de palavras a dominar'
        }
        widgets = {
            'daily_goal': forms.NumberInput(attrs={'min': 1, 'max': 100})
        }