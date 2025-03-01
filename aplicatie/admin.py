from django.contrib import admin

from .models import CustomUser, Furnizor, Marime, Recenzie, Incaltaminte, Promotie, Marca, Material, Imagine
from django.contrib.auth.admin import UserAdmin

admin.site.site_header = "Panou de Administrare SneakerShop"
admin.site.site_title = "+++"
admin.site.index_title = "Panou Admin"


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nume','descriere']
    search_fields = ['nume']
    list_filter = ['nume']
    fieldsets = (
        ('Nume marca', {
            'fields' : ['nume']
        }),
        ('Descriere marca', {
            'fields' : ['descriere'],
        }),
    )

@admin.register(Furnizor)
class FurnizorAdmin(admin.ModelAdmin):
    list_display = ['nume','email','numar_telefon']
    search_fields = ['nume']
    list_filter = ['nume']
    fieldsets = (
        ('Nume furnizor', {'fields' : ['nume']}),
        ('Date contact', {'fields' : ['email','numar_telefon']}),
    )

@admin.register(Promotie)
class PromotieAdmin(admin.ModelAdmin):
    list_display = ['nume','data_inceput','data_sfarsit','procentaj']
    search_fields = ['nume']
    list_filter = ['nume','data_inceput']
    fieldsets = (
        ('Nume promotie', {'fields' : ['nume']}),
        ('Perioada', {'fields' : ['data_inceput','data_sfarsit']}),
        ('Procentaj de reducere', {'fields' : ['procentaj']}),
    )

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['nume','componenta']
    search_fields = ['nume']
    list_filter = ['componenta']

class ImagineAdmin(admin.TabularInline):
    model = Imagine
    extra = 0

class MaterialIncAdmin(admin.TabularInline):
    model = Material.id_incaltaminte.through # pentru many-to-many
    extra = 0

class Marime2Admin(admin.TabularInline):
    model = Marime
    extra = 0

@admin.register(Incaltaminte)
class IncaltaminteAdmin(admin.ModelAdmin):
    inlines = [ImagineAdmin,MaterialIncAdmin,Marime2Admin]
    exclude = ['id_incaltaminte'] # pentru many-to-many
    list_display = ['nume','pret']
    search_fields = ['nume']
    list_filter = ['id_marca']
    fieldsets = (
        ('Nume', {'fields' : ['nume']}),
        ('Marca', {'fields' : ['id_marca']}),
        ('Promotie', {'fields' : ['id_promotie']}),
        ('Furnizor', {'fields' : ['id_furnizor']}),
        ('Pret', {'fields' : ['pret']}),
        ('Culoare', {'fields' : ['culoare']}),
        ('Categorie', {'fields' : ['categorie']}),
        ('Descriere', {'classes' : ['collapse'], 'fields' : ['descriere']}),
    )

@admin.register(Imagine)
class Imagine2Admin(admin.ModelAdmin):
    list_display = ['id_incaltaminte','imagine']
    search_fields = ['id_incaltaminte__nume']
    list_filter = ['id_incaltaminte__nume']

@admin.register(Recenzie)
class RecenzieAdmin(admin.ModelAdmin):
    list_display = ['id_incaltaminte','stele','data_recenzie','comentariu']
    search_fields = ['id_incaltaminte__nume']
    list_filter = ['id_incaltaminte__nume','stele']

@admin.register(Marime)
class MarimeAdmin(admin.ModelAdmin):
    list_display = ['id_incaltaminte','marime','numar_bucati']
    search_fields = ['id_incaltaminte__nume']
    list_filter = ['id_incaltaminte__nume','marime']
    

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Informatii suplimentare', {
                'fields': (
                    'numar_telefon',
                    'adresa',
                    'data_nasterii',
                    'poza_profil',
                    'newsletter',
                    'email_confirmat',
                ),
            }
        ),
    )
    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        (
            'Informatii suplimentare', {
                'classes': ('wide',),
                'fields': (
                    'numar_telefon',
                    'adresa',
                    'data_nasterii',
                    'poza_profil',
                    'newsletter',
                ),
            }
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)