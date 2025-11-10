from django.db import models
import uuid

# # Create your models here.


# class Entreprise(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date= models.DateField(auto_now_add=True)
#     Nif = models.CharField(max_length=20)
#     Rccm = models.CharField(max_length=30, null=True)
#     Designation = models.CharField(max_length=100)
#     Devise = models.CharField(max_length=5)
#     Activité = models.CharField(max_length=100)
#     Adresse = models.CharField(max_length=100)
#     Telephone = models.CharField(max_length=20)
#     Email = models.EmailField(null=True)
#     Site = models.CharField(max_length=100, null=True)
#     Logo = models.ImageField()
#     def __str__(self):
#         return self.Designation


# class PointVente(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date= models.DateField(auto_now_add=True)
#     Designation = models.CharField(max_length=100)
#     Key = models.CharField()
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)


# class StyleFacture(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Primary_color=models.CharField(max_length=50)
#     Filigrane=models.ImageField(null=True)
#     Police=models.CharField(max_length=50)
#     Border_color=models.CharField(max_length=50)
#     Premiere_ligne=models.CharField(max_length=50)
#     Deuxieme_ligne=models.CharField(max_length=50)
#     CompteClient=models.BooleanField(default=True)
#     CompteEntreprise=models.BooleanField(default=True)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)


# class Compte(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Type = models.CharField(max_length=50)
#     Operateur = models.CharField(max_length=50)
#     Nom = models.CharField(max_length=50)
#     Numero = models.CharField(max_length=50)
#     Obs = models.TextField(null=True)
#     def __str__(self):
#         nom=self.Type+'['+str(self.Numero)+']'
#         return nom


# class CompteEntreprise(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     Date= models.DateField(auto_now_add=True)


# class Abonnement(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Compte = models.ForeignKey(CompteEntreprise, on_delete=models.CASCADE)
#     Montant = models.IntegerField()
#     Date = models.DateField(auto_now_add=True)
#     DateFin= models.DateField(null=True)
#     Obs = models.CharField(max_length=100, null=True)
#     pass


# class Operateur(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Email = models.EmailField()
#     Password = models.CharField(max_length=50)
#     Username = models.CharField(max_length=50)
#     Profil = models.ImageField()
#     SuperAdmin = models.BooleanField(default=False)
#     Date= models.DateField(auto_now_add=True)
#     PointVente = models.ForeignKey(PointVente, on_delete=models.CASCADE)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     def __str__(self):
#         return self.Username


# class TypeActeur(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Code = models.CharField(max_length=5)
#     Libelle = models.CharField(max_length=50)
#     pass


# class Acteur(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date= models.DateField(auto_now_add=True)
#     Model = models.CharField(max_length=5)
#     Type = models.ForeignKey(TypeActeur, on_delete=models.CASCADE)
#     Nif = models.CharField(max_length=20, null=True)
#     Designation = models.CharField(max_length=100)
#     Adresse = models.CharField(max_length=100, null=True)
#     Telephone = models.CharField(max_length=20, null=True)
#     Email = models.EmailField(null=True)
#     Refdoc = models.CharField(max_length=100, null=True)
#     Profil = models.ImageField()
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class CompteClient(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
#     Client = models.ForeignKey(Acteur, on_delete=models.CASCADE)
#     Date= models.DateField(auto_now_add=True)
#     def __str__(self):
#         return str(self.Compte)



# class Taux(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Libelle = models.IntegerField()
#     Date= models.DateField(auto_now_add=True)
#     pass


# class TaxeSpecifique(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Designation = models.CharField(max_length=100)
#     Taux = models.IntegerField()
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class Categorie(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Libelle = models.CharField(max_length=30)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class GroupeTaxation(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Code = models.CharField(max_length=5)
#     Designation = models.CharField(max_length=30)
#     Taux = models.IntegerField(null=True)
#     pass


# class Article(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date = models.DateField(auto_now_add=True)
#     Type = models.CharField(max_length=5)
#     Designation = models.CharField(max_length=50)
#     Prix = models.IntegerField()
#     Devise = models.CharField(max_length=5)
#     Mesure = models.CharField(max_length=30, null=True)
#     Categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, null=True)
#     Photo = models.ImageField()
#     Groupe = models.ForeignKey(GroupeTaxation, on_delete=models.CASCADE)
#     Taxe_specifique = models.ForeignKey(TaxeSpecifique, on_delete=models.CASCADE, null=True)
#     Mode = models.CharField(max_length=5)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class Stock(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Article = models.ForeignKey(Article, on_delete=models.CASCADE)
#     Fournisseur = models.ForeignKey(Acteur, on_delete=models.CASCADE, null=True)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     PrixUnitaire = models.IntegerField()
#     Devise = models.CharField(max_length=5)
#     Taux = models.IntegerField(null=True)
#     Quantite = models.IntegerField()
#     Montant = models.IntegerField()
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class TypeFacture(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Code = models.CharField(max_length=5)
#     Libelle = models.CharField(max_length=50)
#     pass


# class Facture(models.Model):
#     Uuid = models.CharField(primary_key=True, max_length=100)
#     RN = models.CharField(max_length=30, null=True)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     Type = models.ForeignKey(TypeFacture, on_delete=models.CASCADE)
#     Montant = models.IntegerField()
#     Devise = models.CharField(max_length=5)
#     ModeFacture = models.CharField(max_length=5)
#     ModePaiement = models.CharField(max_length=30)
#     Client = models.ForeignKey(Acteur, on_delete=models.CASCADE)
#     Compte = models.ForeignKey(CompteClient, on_delete=models.CASCADE, null=True)
#     NatureAvoir = models.CharField(max_length=30, null=True)
#     ReferenceAvoir = models.CharField(max_length=30, null=True)
#     Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class DataDgi(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
#     codeDEFDGI = models.CharField(max_length=100)
#     nim = models.CharField(max_length=100)
#     counters = models.CharField(max_length=100)
#     dateTime = models.CharField(max_length=100)
#     qrcode = models.CharField(max_length=100)
#     pass


# class ItemFacture(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
#     Article = models.ForeignKey(Article, on_delete=models.CASCADE)
#     Quantite = models.IntegerField()
#     Montant = models.IntegerField()
#     pass


# class Commentaire(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
#     Texte = models.TextField()
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     pass


# class Paiement(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Code = models.CharField(max_length=30)
#     Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     Mode = models.CharField(max_length=30)
#     Devise = models.CharField(max_length=5)
#     Taux = models.IntegerField(null=True)
#     Montant = models.IntegerField()
#     Compte = models.ForeignKey(CompteClient, on_delete=models.CASCADE, null=True)
#     Statut = models.CharField(max_length=30)
#     Solde = models.CharField(max_length=30)
#     Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
#     pass


# class Devis(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Code = models.CharField(max_length=30)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     Type = models.CharField(max_length=50)
#     Devise = models.CharField(max_length=5)
#     Montant = models.IntegerField()
#     Client = models.ForeignKey(Acteur, on_delete=models.CASCADE, null=True)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
#     pass


# class ItemDevis(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Devis = models.ForeignKey(Devis, on_delete=models.CASCADE)
#     Article = models.ForeignKey(Article, on_delete=models.CASCADE)
#     Quantite = models.IntegerField()
#     Montant = models.IntegerField()
#     pass


# class Notification(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     Titre = models.CharField(max_length=100)
#     Texte = models.TextField()
#     Photo = models.ImageField()
#     Lecture = models.BooleanField(default=False)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True)


# class Action(models.Model):
#     Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     Date = models.DateField(auto_now_add=True)
#     Heure = models.TimeField(auto_now_add=True)
#     Type = models.CharField(max_length=30)
#     Element = models.CharField(max_length=30)
#     Table = models.CharField(max_length=30)
#     Obs = models.CharField(max_length=100, null=True)
#     Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
#     Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)

# Create your models here.


class Entreprise(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date= models.DateField(auto_now_add=True)
    Nif = models.CharField(max_length=20)
    Rccm = models.CharField(max_length=30, null=True)
    Designation = models.CharField(max_length=100)
    Devise = models.CharField(max_length=5)
    Activité = models.CharField(max_length=100)
    Adresse = models.CharField(max_length=100)
    Telephone = models.CharField(max_length=20)
    Email = models.EmailField(null=True)
    Site = models.CharField(max_length=100, null=True)
    Logo = models.ImageField()
    def __str__(self):
        return self.Designation


class PointVente(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date= models.DateField(auto_now_add=True)
    Designation = models.CharField(max_length=100)
    Key = models.CharField()
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)


class StyleFacture(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Primary_color=models.CharField(max_length=50)
    Filigrane=models.ImageField(null=True)
    Police=models.CharField(max_length=50)
    Border_color=models.CharField(max_length=50)
    Premiere_ligne=models.CharField(max_length=50)
    Deuxieme_ligne=models.CharField(max_length=50)
    CompteClient=models.BooleanField(default=True)
    CompteEntreprise=models.BooleanField(default=True)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)


class Compte(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Type = models.CharField(max_length=50)
    Operateur = models.CharField(max_length=50)
    Nom = models.CharField(max_length=50)
    Numero = models.CharField(max_length=50)
    Obs = models.TextField(null=True)
    def __str__(self):
        nom=self.Type+'['+str(self.Numero)+']'
        return nom


class CompteEntreprise(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    Date= models.DateField(auto_now_add=True)


class Abonnement(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Compte = models.ForeignKey(CompteEntreprise, on_delete=models.CASCADE)
    Montant = models.IntegerField()
    Date = models.DateField(auto_now_add=True)
    DateFin= models.DateField(null=True)
    Obs = models.CharField(max_length=100, null=True)
    pass


class Operateur(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Email = models.EmailField()
    Password = models.CharField(max_length=50)
    Username = models.CharField(max_length=50)
    Profil = models.ImageField()
    SuperAdmin = models.BooleanField(default=False)
    Date= models.DateField(auto_now_add=True)
    PointVente = models.ForeignKey(PointVente, on_delete=models.CASCADE)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    def __str__(self):
        return self.Username


class TypeActeur(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(max_length=5)
    Libelle = models.CharField(max_length=50)
    pass


class Acteur(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date= models.DateField(auto_now_add=True)
    Model = models.CharField(max_length=5)
    Type = models.ForeignKey(TypeActeur, on_delete=models.CASCADE)
    Nif = models.CharField(max_length=20, null=True)
    Designation = models.CharField(max_length=100)
    Adresse = models.CharField(max_length=100, null=True)
    Telephone = models.CharField(max_length=20, null=True)
    Email = models.EmailField(null=True)
    Refdoc = models.CharField(max_length=100, null=True)
    Profil = models.ImageField()
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class CompteClient(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    Client = models.ForeignKey(Acteur, on_delete=models.CASCADE)
    Date= models.DateField(auto_now_add=True)
    def __str__(self):
        return str(self.Compte)



class Taux(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Libelle = models.IntegerField()
    Date= models.DateField(auto_now_add=True)
    pass


class TaxeSpecifique(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Designation = models.CharField(max_length=100)
    Taux = models.IntegerField()
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class Categorie(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Libelle = models.CharField(max_length=30)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class GroupeTaxation(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(max_length=5)
    Designation = models.CharField(max_length=30)
    Taux = models.IntegerField(null=True)
    pass


class Article(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date = models.DateField(auto_now_add=True)
    Type = models.CharField(max_length=5)
    Designation = models.CharField(max_length=50)
    Prix = models.IntegerField()
    Devise = models.CharField(max_length=5)
    Mesure = models.CharField(max_length=30, null=True)
    Categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, null=True)
    Photo = models.ImageField()
    Groupe = models.ForeignKey(GroupeTaxation, on_delete=models.CASCADE)
    Taxe_specifique = models.ForeignKey(TaxeSpecifique, on_delete=models.CASCADE, null=True)
    Mode = models.CharField(max_length=5)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class Stock(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Article = models.ForeignKey(Article, on_delete=models.CASCADE)
    Fournisseur = models.ForeignKey(Acteur, on_delete=models.CASCADE, null=True)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    PrixUnitaire = models.IntegerField()
    Devise = models.CharField(max_length=5)
    Taux = models.IntegerField(null=True)
    Quantite = models.IntegerField()
    Montant = models.IntegerField()
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class TypeFacture(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(max_length=5)
    Libelle = models.CharField(max_length=50)
    pass


class Facture(models.Model):
    Uuid = models.CharField(primary_key=True, max_length=100)
    RN = models.CharField(max_length=30, null=True)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    Type = models.ForeignKey(TypeFacture, on_delete=models.CASCADE)
    Montant = models.IntegerField()
    Devise = models.CharField(max_length=5)
    ModeFacture = models.CharField(max_length=5)
    ModePaiement = models.CharField(max_length=30)
    Client = models.ForeignKey(Acteur, on_delete=models.CASCADE)
    Compte = models.ForeignKey(CompteClient, on_delete=models.CASCADE, null=True)
    NatureAvoir = models.CharField(max_length=30, null=True)
    ReferenceAvoir = models.CharField(max_length=30, null=True)
    Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class DataDgi(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    codeDEFDGI = models.CharField(max_length=100)
    nim = models.CharField(max_length=100)
    counters = models.CharField(max_length=100)
    dateTime = models.CharField(max_length=100)
    qrcode = models.CharField(max_length=100)
    pass


class ItemFacture(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    Article = models.ForeignKey(Article, on_delete=models.CASCADE)
    Quantite = models.IntegerField()
    Montant = models.IntegerField()
    pass


class Commentaire(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    Texte = models.TextField()
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    pass


class Paiement(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(max_length=30)
    Facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    Mode = models.CharField(max_length=30)
    Devise = models.CharField(max_length=5)
    Taux = models.IntegerField(null=True)
    Montant = models.IntegerField()
    Compte = models.ForeignKey(CompteClient, on_delete=models.CASCADE, null=True)
    Statut = models.CharField(max_length=30)
    Solde = models.CharField(max_length=30)
    Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
    pass


class Devis(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(max_length=30)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    Type = models.CharField(max_length=50)
    Devise = models.CharField(max_length=5)
    Montant = models.IntegerField()
    Client = models.ForeignKey(Acteur, on_delete=models.CASCADE, null=True)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    pass


class ItemDevis(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Devis = models.ForeignKey(Devis, on_delete=models.CASCADE)
    Article = models.ForeignKey(Article, on_delete=models.CASCADE)
    Quantite = models.IntegerField()
    Montant = models.IntegerField()
    pass


class Notification(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    Titre = models.CharField(max_length=100)
    Texte = models.TextField()
    Photo = models.ImageField()
    Lecture = models.BooleanField(default=False)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True)


class Action(models.Model):
    Uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Date = models.DateField(auto_now_add=True)
    Heure = models.TimeField(auto_now_add=True)
    Type = models.CharField(max_length=30)
    Element = models.CharField(max_length=30)
    Table = models.CharField(max_length=30)
    Obs = models.CharField(max_length=100, null=True)
    Operateur = models.ForeignKey(Operateur, on_delete=models.CASCADE)
    Entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE)