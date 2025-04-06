from django import forms
from .models import Athlet
from django.contrib.auth.models import User

class AthletForm(forms.ModelForm):
    class Meta:
        model = Athlet
        fields = ['name', 'gender', 'rank', 'date_birthday', 'team', 'region']

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

class CompetitionLoginForm(forms.Form):
    competition_name = forms.CharField(label='Название соревнования')
    password = forms.CharField(widget=forms.PasswordInput)
