from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import random, string
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Furnizor(models.Model):
    nume = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    numar_telefon = models.CharField(max_length=12)
    def __str__(self):
        return self.nume

class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    data_inceput = models.DateField()
    data_sfarsit = models.DateField()
    procentaj = models.DecimalField(max_digits=4, decimal_places=2)
    def __str__(self):
        return self.nume

class Marca(models.Model):
    nume = models.CharField(max_length=100, unique=True)
    descriere = models.TextField(blank=True)
    def __str__(self):
        return self.nume

class Incaltaminte(models.Model):
    id_marca = models.ForeignKey(Marca, on_delete=models.CASCADE)
    id_furnizor = models.ForeignKey(Furnizor, on_delete=models.CASCADE)
    id_promotie = models.ForeignKey(Promotie, null=True, blank=True, on_delete=models.SET_NULL)
    nume = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=7, decimal_places=2)
    culoare = models.CharField(max_length=15)
    descriere = models.TextField(blank=True)
    tip_categorie = [('sport','Sport'),('casual','Casual'),('ghete','Ghete')]
    categorie = models.CharField(max_length=15, choices=tip_categorie)
    def __str__(self):
        return self.nume

class Material(models.Model):
    nume = models.CharField(max_length=100)
    id_incaltaminte = models.ManyToManyField(Incaltaminte)
    tip_componenta = [('exterior','Exterior'),('interior','Interior'),('talpa','Talpa')]
    componenta = models.CharField(max_length=20, choices=tip_componenta, default='')
    def __str__(self):
        return f"{self.nume} ({self.componenta})"

class Imagine(models.Model):
    id_incaltaminte = models.ForeignKey(Incaltaminte, on_delete=models.CASCADE)
    imagine = models.ImageField(upload_to='imagini/')

class Marime(models.Model):
    id_incaltaminte = models.ForeignKey(Incaltaminte, on_delete=models.CASCADE)
    tip_marime = [(36,'36'),(37,'37'),(38,'38'),(39,'39'),(40,'40'),(41,'41'),(42,'42'),(43,'43'),(44,'44'),(45,'45'),(46,'46')]
    marime = models.IntegerField(choices=tip_marime)
    numar_bucati = models.IntegerField(null=True, default=0)

class Recenzie(models.Model):
    id_incaltaminte = models.ForeignKey(Incaltaminte, on_delete=models.CASCADE)
    nr_stele = [(1,'O stea'), (2,'2 stele'), (3,'3 stele'), (4,'4 stele'), (5,'5 stele')]
    stele = models.IntegerField(choices=nr_stele)
    comentariu = models.TextField(blank=True)
    data_recenzie = models.DateField(auto_now_add=True)

class CustomUser(AbstractUser):
    numar_telefon = models.CharField(max_length=15, blank=True, null=True)
    adresa = models.TextField(blank=True, null=True)
    data_nasterii = models.DateField(blank=True, null=True)
    poza_profil = models.ImageField(upload_to='poze_profil/', blank=True, null=True)
    newsletter = models.BooleanField(default=False)
    cod = models.CharField(max_length=100, null=True)
    email_confirmat = models.BooleanField(default=False)
    blocat = models.BooleanField(default=False) 

    def generate_cod(self):
        self.cod = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        self.save()

    def __str__(self):
        return self.username

class Vizualizari(models.Model):
    utilizator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    produs = models.ForeignKey(Incaltaminte, on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_vizualizare']
        get_latest_by = 'data_vizualizare'


@receiver(post_migrate)
def create_custom_permissions(sender, **kwargs):
    content_type = ContentType.objects.get(app_label='app_name', model='CustomUser')
    Permission.objects.get_or_create(
        codename='vizualizeaza_oferta',
        name='Poate vizualiza oferta',
        content_type=content_type,
    )