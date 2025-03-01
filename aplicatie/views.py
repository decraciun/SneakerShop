from django.shortcuts import render, redirect
from django.core.cache import cache
import logging
logger = logging.getLogger('django')
from django.contrib.auth.signals import (user_logged_in,
                                        user_logged_out,
                                        user_login_failed)
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse

from aplicatie.models import Incaltaminte, Vizualizari, Marca, Recenzie, CustomUser

from .forms import ProduseForm, ContactForm, RecenzieForm, CustomUserRegistrationForm, CustomLoginForm

from datetime import datetime, date

from django.utils.html import strip_tags

import re, os, json

from django.contrib.auth import logout, login

from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordChangeForm

from django.contrib.auth import update_session_auth_hash

from django.contrib import messages

from django.shortcuts import get_object_or_404

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.mail import mail_admins
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission

@login_required
def aloca_permisiune(request):
    if request.method == 'POST':
        permisiune = Permission.objects.get(codename='vizualizeaza_oferta')
        request.user.user_permissions.add(permisiune)
        return JsonResponse({"message": "Permisiune alocata cu succes."})
    return HttpResponseForbidden()

def index(request):
    return render(request,'index.html')

@login_required
def oferta(request):
    if not request.user.has_perm('app_name.vizualizeaza_oferta'):
        return render(request, '403.html', {
            'titlu': 'Eroare afisare oferta',
            'mesaj_personalizat': 'Nu ai voie sa vizualizezi oferta.',
        }, status=403)
    return render(request, 'oferta.html', {'titlu': 'Oferta Specială'})

def produse(request):
    produse = Incaltaminte.objects.all()
    marci = Marca.objects.all()

    nume = request.GET.get('nume', '')
    if nume:
        produse = produse.filter(nume__icontains=nume)

    categorie = request.GET.get('categorie', '')
    if categorie:
        produse = produse.filter(categorie=categorie)

    pret_min = request.GET.get('pret_min', '')
    pret_max = request.GET.get('pret_max', '')
    if pret_min:
        produse = produse.filter(pret__gte=pret_min)
    if pret_max:
        produse = produse.filter(pret__lte=pret_max)

    marca = request.GET.get('marca', '')
    if marca:
        produse = produse.filter(id_marca__nume__icontains=marca)

    culoare = request.GET.get('culoare', '')
    if culoare:
        produse = produse.filter(culoare__icontains=culoare)

    dict = {
        'produse' : produse,
        'categorii' : Incaltaminte.tip_categorie,
        'marci' : marci
    }
    messages.debug(request, f"Produse incarcate: {len(produse)}")
    messages.info(request, "Afisam lista tuturor produselor disponibile.")
    return render(request, 'produse.html', dict)

def produse2(request):
    produse = Incaltaminte.objects.all()
    if request.method == 'POST':
        form = ProduseForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['nume']:
                produse = produse.filter(nume__icontains=form.cleaned_data['nume'])
            if form.cleaned_data['pret_min']:
                produse = produse.filter(pret__gte=form.cleaned_data['pret_min'])
            if form.cleaned_data['pret_max']:
                produse = produse.filter(pret__lte=form.cleaned_data['pret_max'])
            if form.cleaned_data['culoare']:
                produse = produse.filter(culoare__icontains=form.cleaned_data['culoare'])
            if form.cleaned_data['categorie']:
                produse = produse.filter(categorie=form.cleaned_data['categorie'])
            if form.cleaned_data['marca']:
                produse = produse.filter(id_marca=form.cleaned_data['marca'])
    else:
        form = ProduseForm()
    return render(request,'produse2.html', {'form' : form, 'produse' : produse})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            nume = cleaned_data['nume']
            prenume = cleaned_data.get('prenume', '')
            data_nasterii = cleaned_data['data_nasterii']
            email = cleaned_data['email']
            tip_mesaj = cleaned_data['tip_mesaj']
            subiect = cleaned_data['subiect']
            zile_asteptare = cleaned_data['zile_asteptare']
            mesaj = cleaned_data['mesaj']
            
            # salvare varsta in ani si luni
            today = date.today()
            ani = today.year - data_nasterii.year
            luni = today.month - data_nasterii.month
            if luni < 0:
                ani -= 1
                luni += 12
            
            # daca in mesaj sunt linii noi, se vor transforma in spatii. daca sunt mai multe spatii succesive, se vor comasa intr-unul singur.
            mesaj = re.sub(r'\s+', ' ', mesaj.replace('\n', ' ')).strip()
            
            # salvare JSON
            folder_mesaje = os.path.join(settings.BASE_DIR, 'mesaje')
            timestamp = int(datetime.now().timestamp())
            nume_fisier = f"mesaj_{timestamp}.json"
            cale_fisier = os.path.join(folder_mesaje, nume_fisier)

            mesaj_json = {
                "nume": nume,
                "prenume": prenume,
                "varsta": f"{ani} ani si {luni} luni",
                "email": email,
                "tip_mesaj": tip_mesaj,
                "subiect": subiect,
                "zile_asteptare": zile_asteptare,
                "mesaj": mesaj,
            }

            with open(cale_fisier, 'w') as f:
                json.dump(mesaj_json, f)
            
            return render(request, 'mesaj_trimis.html', {'nume': nume})
        
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})

def adauga_recenzie(request):
    if not request.user.has_perm('app_name.add_recenzie'):
        return HttpResponseForbidden(render(request, '403.html', {
            'titlu': 'Eroare adaugare recenzie',
            'mesaj_personalizat': f'Nu ai voie să adaugi recenzii',
        }))
    
    if request.method == 'POST':
        form = RecenzieForm(request.POST)
        if form.is_valid():
            recenzie = form.save(commit=False)
            recenzie.save()
            return redirect('recenzii_lista')
    else:
        form = RecenzieForm()
        
    return render(request, 'adauga_recenzie.html', {'form': form})

def lista_recenzii(request):
    recenzii = Recenzie.objects.all().order_by('-data_recenzie')
    return render(request, 'lista_recenzii.html', {'recenzii': recenzii})

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save()
            send_confirmation_email(user)
            return redirect('confirmare_email')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(86400) 
            else:
                request.session.set_expiry(0)  
            
            if user.email_confirmat:
                login(request, user)
                return redirect('profil') 
            else:
                messages.error(request, 'Confirma email-ul.')
                send_confirmation_email(user)
                return redirect('login')  
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def profil(request):
    user_data = {
        'username': request.user.username,
        'email': request.user.email,
        'numar_telefon': request.user.numar_telefon,
        'adresa': request.user.adresa,
        'data_nasterii': request.user.data_nasterii,
        'poza_profil': request.user.poza_profil.url if request.user.poza_profil else None,
        'newsletter': request.user.newsletter,
    }
    return render(request, 'profil.html', {'user_data': user_data})

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user) # mentine sesiunea dupa ce este schimbata parola
            messages.success(request, 'Parola a fost actualizata')
            return redirect('profil')
        else:
            messages.error(request, 'Exista erori.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'schimba_parola.html', {'form': form})

def confirm_email(request, cod):
    user = get_object_or_404(CustomUser, cod=cod)
    if not user.email_confirmat:
        user.email_confirmat = True
        user.save()
        return HttpResponse('Email-ul a fost confirmat cu succes')
    else:
        return HttpResponse('Email-ul a fost deja confirmat')

def send_confirmation_email(user):
    context = {
        'username': user.username,
        'confirm_url': f'http://127.0.0.1:8000/confirma_mail/{user.cod}/',
        'logo_url': f'http://127.0.0.1:8000/static/images/logo.jpg'
    }
    subject = 'Confirmare email'
    html_content = render_to_string('emailtemplate.html', context)
    
    email = EmailMessage(
        subject,
        html_content,
        'craciundenis96@gmail.com',
        [user.email]
    )
    email.content_subtype = 'html'
    email.send()
    
def confirmare_email(request):
    return render(request, 'confirmare_email.html')

def update_vizualizari(user, produs):
    Vizualizari.objects.crate(utilizator=user, produs=produs)
    while Vizualizari.objects.filter(utilizator=user).count() > 5:
        Vizualizari.objects.filter(utilizator=user).earliest('data_vizualizare').delete()
        
def incaltaminte_view(request, id):
    incaltaminte = get_object_or_404(Incaltaminte, id=id)
    if request.user.is_authenticated:
        update_vizualizari(request.user, incaltaminte)
    else:
        messages.error(request, 'Eroare produs')
    return render(request, 'incaltaminte.html', {'incaltaminte', incaltaminte})

def send_sus_login_alert(username, ip_adress):
    subject = 'Alerta logari suspecte'
    html_message = render_to_string('sus_login.html', {'username': username, 'ip':ip_adress})
    plain_message = strip_tags(html_message)
    mail_admins(subject, plain_message, html_message)
    
@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username','')
    attempts = cache.get(username,0)
    cache.set(username, attempts + 1, timeout = 120)
    
    if cache.get(username) >= 3:
        ip_address = 1234
        send_sus_login_alert(username, ip_address)
        cache.delete(username)
        logger.critical(f'userul: {username} a incercat sa se logheze de mai multe ori')
        
def detalii_produs(request, produs_id):
    produs = get_object_or_404(Incaltaminte, id=produs_id)
    return render(request, 'incaltaminte.html', {'produs': produs})

def custom_403_view(request, exception):
    return render(request, '403.html', {
        'titlu': 'Acces Restrictionat',
        'mesaj_personalizat': 'Ne pare rau, dar nu aveti permisiunea de a accesa aceasta pagina.',
    }, status=403)
