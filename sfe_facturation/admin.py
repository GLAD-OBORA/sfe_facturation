from django.contrib import admin
from .models import Entreprise, Compte, CompteEntreprise, Abonnement, Operateur, Acteur, CompteClient, Taux, TaxeSpecifique, Categorie, Article, Stock, Facture, ItemFacture, Paiement, Action, Notification, GroupeTaxation, Commentaire, TypeActeur, TypeFacture, DataDgi, Devis, StyleFacture, ItemDevis, PointVente

# Register your models here.
@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
	pass


@admin.register(PointVente)
class PointVenteAdmin(admin.ModelAdmin):
	pass


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
	pass


@admin.register(CompteEntreprise)
class Compte_EntrepriseAdmin(admin.ModelAdmin):
	pass


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
	pass


@admin.register(Operateur)
class Operateurdmin(admin.ModelAdmin):
	pass


@admin.register(Acteur)
class ActeurAdmin(admin.ModelAdmin):
	pass


@admin.register(CompteClient)
class Compte_ClientAdmin(admin.ModelAdmin):
	pass


@admin.register(Taux)
class TauxAdmin(admin.ModelAdmin):
	pass


@admin.register(TaxeSpecifique)
class Taxe_specifiqueAdmin(admin.ModelAdmin):
	pass


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
	pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	pass


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
	pass


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
	pass


@admin.register(ItemFacture)
class ItemFactureAdmin(admin.ModelAdmin):
	pass


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
	pass


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
	pass


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	pass


@admin.register(GroupeTaxation)
class GroupeAdmin(admin.ModelAdmin):
	pass


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
	pass


@admin.register(TypeActeur)
class TypeActeurAdmin(admin.ModelAdmin):
	pass


@admin.register(TypeFacture)
class TypeFactureAdmin(admin.ModelAdmin):
	pass


@admin.register(DataDgi)
class DataDgiAdmin(admin.ModelAdmin):
	pass


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
	pass


@admin.register(ItemDevis)
class ItemDevisAdmin(admin.ModelAdmin):
	pass


@admin.register(StyleFacture)
class StyleFactureAdmin(admin.ModelAdmin):
	pass


