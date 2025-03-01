from django.urls import path
from . import views
from django.conf.urls import handler403

handler403 = 'app_name.views.custom_403_view'
from django.contrib.sitemaps import Sitemap
from aplicatie.models import Incaltaminte, Marca, Furnizor, Promotie

urlpatterns = [
	path("", views.index, name="index"),
	path("produse/", views.produse, name="produse"),
	path("produse2/", views.produse2, name="produse2"),
	path("contact/", views.contact, name="contact"),
	path('recenzii/', views.lista_recenzii, name='recenzii_lista'),
    path('recenzii/adauga/', views.adauga_recenzie, name='adauga_recenzie'),
	path('register/', views.register, name='register'),
	path('profil/', views.profil, name='profil'),
	path('login/', views.login_view, name='login'),
	path('schimba_parola/', views.change_password_view, name='schimba_parola'),
	path('logout/', views.logout_view, name='logout'),
	path('confirma_mail/<str:cod>/', views.confirm_email, name='confirm_email'),
	path('confirmare_email/', views.confirmare_email, name='confirmare_email'),
	path('incaltaminte/<int:produs_id>/', views.detalii_produs, name='detalii_produs'),
	path('oferta/', views.oferta, name='oferta'),
]

class IncaltaminteSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Incaltaminte.objects.all()

    def location(self, obj):
        return f'/incaltaminte/{obj.id}'

class MarcaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Marca.objects.all()

    def location(self, obj):
        return f'/marca/{obj.id}'

class FurnizorSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Furnizor.objects.all()

    def location(self, obj):
        return f'/furnizor/{obj.id}'

class PaginiStaticeSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.4

    def items(self):
        return ['index', 'contact']

    def location(self, item):
        return f'/{item}'

sitemaps = {
    'incaltaminte': IncaltaminteSitemap,
    'marca': MarcaSitemap,
    'furnizor': FurnizorSitemap,
    'pagini_statice': PaginiStaticeSitemap,
}
