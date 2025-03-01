from django import forms
from .models import Incaltaminte, Marca, Recenzie, CustomUser
import re, random, string
from datetime import datetime, date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
import logging
logger = logging.getLogger('django')
from django.core.mail import mail_admins
from django.utils.html import strip_tags

from django.template.loader import render_to_string

class ProduseForm(forms.Form):
    nume = forms.CharField(
        required=False, 
        label='Nume produs', 
        widget=forms.TextInput
    )
    pret_min = forms.DecimalField(
        required=False, 
        label='Pret minim', 
        widget=forms.NumberInput
    )
    pret_max = forms.DecimalField(
        required=False, 
        label='Pret maxim', 
        widget=forms.NumberInput
    )
    culoare = forms.CharField(
        required=False, 
        label='Culoare', 
        widget=forms.TextInput
    )
    categorie = forms.ChoiceField(
        required=False, 
        label='Categorie', 
        choices=[('', 'Toate')] + Incaltaminte.tip_categorie,
        widget=forms.Select
    )
    marca = forms.ModelChoiceField(
        required=False, 
        label='Marca', 
        queryset=Marca.objects.all(),
        empty_label='Toate',
        widget=forms.Select
    )

def validare(text):
    if not text[0].isupper():
        raise forms.ValidationError("Textul trebuie sa inceapa cu litera mare.")
    if not all(c.isalpha() or c.isspace() for c in text):
        raise forms.ValidationError("Textul trebuie sa contina doar spatii si cuvinte formate din litere.")

class ContactForm(forms.Form):
    nume = forms.CharField(
        max_length=10,
        required=True,
        label="Nume",
        validators=[validare],
        error_messages={
            'required': 'Numele este obligatoriu.',
            'max_length': 'Numele nu poate avea mai mult de 10 caractere.',
        }
    )
    prenume = forms.CharField(
        required=False,
        label="Prenume",
        validators=[validare],
    )
    data_nasterii = forms.DateField(
        required=True,
        label="Data nasterii",
        widget=forms.DateInput(attrs={'type': 'date'}),
        error_messages={'required': 'Data nasterii este obligatorie.'},
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={'required': 'Adresa de email este obligatorie.'},
    )
    confirmare_email = forms.EmailField(
        required=True,
        label="Confirmare Email",
        error_messages={'required': 'Confirmarea adresei de email este obligatorie.'},
    )
    tip_mesaj = forms.ChoiceField(
        required=True,
        label="Tip Mesaj",
        choices=[
            ('reclamatie', 'Reclamatie'),
            ('intrebare', 'Intrebare'),
            ('review', 'Review'),
            ('cerere', 'Cerere'),
            ('programare', 'Programare'),
        ],
    )
    subiect = forms.CharField(
        required=True,
        label="Subiect",
        validators=[validare],
        error_messages={'required': 'Subiectul este obligatoriu.'},
    )
    zile_asteptare = forms.IntegerField(
        required=False,
        label="Minim zile asteptare",
        min_value=1,
        error_messages={
            'min_value': 'Trebuie sa introduceti un numar mai mare decat 0.'
        },
    )
    mesaj = forms.CharField(
        required=True,
        label="Mesaj (Semneaza-te la final!)",
        widget=forms.Textarea,
        error_messages={'required': 'Mesajul este obligatoriu.'},
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirmare_email = cleaned_data.get('confirmare_email')
        data_nasterii = cleaned_data.get('data_nasterii')
        mesaj = cleaned_data.get('mesaj')
        nume = cleaned_data.get('nume')

        if email and confirmare_email and email != confirmare_email:
            raise forms.ValidationError("Adresele de email nu coincid.")

        if data_nasterii:
            today = date.today()
            age_years = today.year - data_nasterii.year
            if today.month < data_nasterii.month or (today.month == data_nasterii.month and today.day < data_nasterii.day):
                age_years -= 1
            if age_years < 18:
                raise forms.ValidationError("Trebuie sa fiti major pentru a trimite acest mesaj.")

        if mesaj:
            cuvinte = re.findall(r'\w+', mesaj)
            if len(cuvinte) < 5 or len(cuvinte) > 100:
                raise forms.ValidationError("Mesajul trebuie sa contina intre 5 si 100 de cuvinte.")
            if any(cuvant.startswith(('http://', 'https://')) for cuvant in cuvinte):
                raise forms.ValidationError("Mesajul nu poate contine linkuri.")
            if not mesaj.strip().endswith(nume):
                raise forms.ValidationError("Mesajul trebuie sa fie semnat cu numele dvs.")

        return cleaned_data

class RecenzieForm(forms.ModelForm):
    titlu_recenzie = forms.CharField(
        label="Titlu recenzie",
        max_length=50,
        required=True,
        help_text="Introduceti un titlu pentru recenzie.",
        error_messages={
            'required': "Titlul este obligatoriu.",
            'max_length': "Titlul nu poate depasi 50 de caractere."
        },
    )
    comentariu_recenzie = forms.CharField(
        label="Recenzie",
        widget=forms.Textarea,
        required=False,
        help_text="Optional: puteti adauga un comentariu despre produs.",
    )

    class Meta:
        model = Recenzie
        fields = ['id_incaltaminte', 'stele']
        labels = {
            'id_incaltaminte': "Produs",
            'stele': "Numar de stele",
        }
        widgets = {
            'id_incaltaminte': forms.Select(),
            'stele': forms.Select(choices=Recenzie.nr_stele),
        }
        error_messages = {
            'id_incaltaminte': {
                'required': "Trebuie sa selectati un produs."
            },
            'stele': {
                'required': "Trebuie sa selectati un numar de stele."
            },
        }

    def clean_titlu_recenzie(self):
        titlu = self.cleaned_data.get('titlu_recenzie')
        if len(titlu) < 5:
            raise forms.ValidationError("Titlul trebuie sa contina cel putin 5 caractere.")
        if not titlu.isalnum():
            raise forms.ValidationError("Titlul trebuie sa contina doar litere si cifre.")
        titluri_interzise = ["Titlu", "Recenzie", "Comentariu"]
        if titlu in titluri_interzise:
            raise forms.ValidationError("Alegeti un titlu mai descriptiv.")
        return titlu

    def clean_comentariu_recenzie(self):
        comentariu = self.cleaned_data.get('comentariu_recenzie')
        if comentariu and len(comentariu) < 10:
            raise forms.ValidationError("Comentariul trebuie sa contina cel putin 10 caractere.")
        if comentariu and any(char in "@#$%^&*" for char in comentariu):
            raise forms.ValidationError("Comentariul nu trebuie sa contina caractere speciale precum @, #, $, etc.")
        comentarii_interzise = ["Comentariu interzis", "Comentariu interzis2"]
        if comentariu in comentarii_interzise:
            raise forms.ValidationError(f"Comentariul nu poate sa contina {comentariu}")
        return comentariu

    def clean_stele(self):
        stele = self.cleaned_data.get('stele')
        if not stele or stele < 1 or stele > 5:
            raise forms.ValidationError(
                "Numarul de stele trebuie sa fie intre 1 si 5."
            )
        return stele

    def clean_id_incaltaminte(self):
        id_incaltaminte = self.cleaned_data.get('id_incaltaminte')
        if not id_incaltaminte:
            raise forms.ValidationError("Trebuie sa selectati un produs pentru recenzie.")
        return id_incaltaminte

    def clean(self):
        cleaned_data = super().clean()
        titlu = cleaned_data.get('titlu_recenzie')
        comentariu = cleaned_data.get('comentariu_recenzie')

        # validare care implica doua campuri
        if titlu and comentariu and titlu in comentariu:
            raise forms.ValidationError(
                "Titlul nu trebuie sa fie inclus in comentariu."
            )

        return cleaned_data

    def save(self, commit=True):
        form = super().save(commit=False)

        titlu = self.cleaned_data.get('titlu_recenzie')
        comentariu = self.cleaned_data.get('comentariu_recenzie')

        if titlu:
            form.comentariu = f"{titlu} - {comentariu}" if comentariu else titlu

        if commit:
            form.save()
        return form

class CustomUserRegistrationForm(UserCreationForm):
    numar_telefon = forms.CharField(max_length=15, required=True, help_text="Introdu un numar de telefon valid.")
    adresa = forms.CharField(widget=forms.Textarea, required=False, help_text="Introduceti adresa complet.")
    data_nasterii = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    poza_profil = forms.ImageField(required=False)
    newsletter = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password1', 'password2',
            'numar_telefon', 'adresa', 'data_nasterii', 'poza_profil', 'newsletter'
        ]

    def clean_numar_telefon(self):
        numar_telefon = self.cleaned_data.get('numar_telefon')
        if not numar_telefon.isdigit():
            raise forms.ValidationError("Numarul de telefon trebuie sa contina doar cifre.")
        return numar_telefon

    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        if data_nasterii >= date.today():
            raise forms.ValidationError("Data nasterii trebuie sa fie o data din trecut.")
        return data_nasterii
    
    def clean_adresa(self):
        adresa = self.cleaned_data.get('adresa')
        if adresa and not (adresa.startswith('Strada') or adresa.startswith('Str.')):
            raise forms.ValidationError("Adresa trebuie sa inceapa cu 'Strada' sau 'Str.'")
        return adresa
    
    def clean_username(self):
        username = self.cleaned_data['username']
        logger.debug(f'Incercare de inregistrare cu username-ul: {username}')
        if username.lower() == 'admin':
            logger.critical(f'Incercare de login cu username-ul admin')
            email = self.cleaned_data.get('email','Nespecificat')
            subject = 'Cineva incearca sa ne preia site-ul'
            message = f'Incercare de inregistrare cu username `admin` de la adresa de email: {email}'
            mail_admins(subject, message)
            html_content = render_to_string('admin_alerta_email.html', {'username': username, 'email': email})
            plain_message = strip_tags(html_content)
            mail_admins(subject, plain_message, html_content)
            raise forms.ValidationError('Nu puteti folosi acest username')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.generate_cod()
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False, label="Tine-ma minte")