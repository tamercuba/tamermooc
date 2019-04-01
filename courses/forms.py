from django import forms

class ContactCourse(forms.Form):
    name    = forms.CharField(label='Nome', max_length=75)
    email   = forms.EmailField(label='E-mail')
    message = forms.CharField(label='Mensagem', widget = forms.Textarea)
