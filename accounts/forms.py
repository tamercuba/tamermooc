from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from core.mail import send_mail_template
from core.utils import generate_hash_key

from .models import PasswordReset

User = get_user_model()

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='E-mail')
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            return email
        raise forms.ValidationError('Nenhum usuário registrado com este e-mail')


    def save(self):
        user = User.objects.get(email=self.cleaned_data['email'])
        key = generate_hash_key(user.username)
        reset = PasswordReset(key=key, user=user)
        reset.save()
        template_name = 'password_reset_mail.html'
        subject = 'TâmerMOOC - Resete sua senha'
        context = {
            'reset': reset,
        }
        send_mail_template(subject, template_name, context, [user.email])


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmação de Senha', widget=forms.PasswordInput)
    # def clean_email(self):                                        # AGORA O CAMPO E-MAIL É OBRIGATÓRIO
    #     email = self.cleaned_data['email']                        # ENTÃO ESSE MÉTODO NAO FAZ MAIS SENTIDO
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError('E-mail já cadastrado')
    #     return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Por favor digite a confirmação de senha corretamente')
        return password2

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        #user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email']      #infos para hora do cadastro

class EditAccountForm(forms.ModelForm):

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     queryset = User.objects.filter(email=email).exclude(pk=self.instance.pk)
    #     if queryset.exists():
    #         raise forms.ValidationError('E-mail já cadastrado')
    #     return email

    class Meta:
        model = User
        fields = ['username','email' ,'first_name' , 'last_name']
