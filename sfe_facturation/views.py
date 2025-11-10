import json
from django.http import JsonResponse
import requests
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse
from .models import Entreprise, PointVente, Compte, CompteEntreprise, Abonnement, Operateur, Acteur, CompteClient, Taux, TaxeSpecifique, Categorie, Article, Stock, Facture, ItemFacture, Paiement, Action, Notification, GroupeTaxation, Commentaire, TypeActeur, TypeFacture, DataDgi, Devis, ItemDevis, StyleFacture
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from PIL import Image
import os
from django.conf import settings
import string
from random import choice, choices
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from reportlab.platypus import Table, TableStyle, Paragraph
from PyPDF2 import PdfReader, PdfWriter

# ==========================================================
# CONFIGURATION DE BASE
# ==========================================================
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 20 * mm
MARGIN_Y = 20 * mm


#https://web.facebook.com/share/r/1BWrS2YGjt/


# Create your views here.
def login(request):
    return render(request, 'page-login.html', {'message': ''})

def forgot_password(request):
    return render(request, 'page-forgot-password.html')


def authentification(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        email=request.POST['email']
        password=request.POST['password']
        query=Operateur.objects.filter(Email=email, Password=password)[:1]
        if query.exists():
            user=query[0]
            entreprise=Entreprise.objects.filter(operateur=user)[:1][0]
            profil_com = 'media/'+str(entreprise.Logo)
            profil_user = 'media/'+str(user.Profil)
            super_admin = str(user.SuperAdmin)
            return render(request, 'index.html', {'usr': user.Uuid, 'com': entreprise.Uuid, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise})
        else:
            message = 'Les informations saisies sont incorrectes'
            return render(request, 'page-login.html', {'message': message})
            pass


def home(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                return render(request, 'index.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise})


def data_article(entreprise):
    articles=Article.objects.filter(Entreprise=entreprise)
    liste_articles=[]
    num=1
    for x in articles:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        dictionnaire['photo']='media/'+str(x.Photo)
        dictionnaire['nom']=x.Designation
        dictionnaire['type']=x.Type
        quantite = Stock.objects.filter(Article=x, Entreprise=entreprise).order_by('-Date', '-Heure')
        nbr=0
        for i in quantite:
            nbr+=int(i.Quantite)
            pass
        if nbr==0:
            nbr='-'
            pass
        dictionnaire['quantite']=nbr
        dictionnaire['mesure']=x.Mesure
        groupe = GroupeTaxation.objects.filter(article__Groupe=x.Groupe)[:1][0]
        dictionnaire['code_groupe']=groupe.Code
        dictionnaire['groupe']=groupe.Designation
        dictionnaire['taux_groupe']=groupe.Taux
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            prix=x.Prix
            devise=x.Devise
        else:
            taux = liste_taux.Libelle
            devise=entreprise.Devise
            if x.Devise==devise:
                prix=x.Prix
            else:
                if devise=="USD":
                    prix=round(x.Prix/taux, 2)
                else:
                    prix=round(x.Prix*taux, 2) 
                    pass
            pass
        dictionnaire['devise']=devise
        dictionnaire['prixht']=prix
        prixtaux = (groupe.Taux*prix)/100
        dictionnaire['prixttc']=round(prix+prixtaux, 2)
        if len(quantite) > 0:
            derniere_entree = quantite[0]
            dictionnaire['derniere_date'] = derniere_entree.Date
            dictionnaire['derniere_quantite'] = derniere_entree.Quantite
        else:
            dictionnaire['derniere_date'] = ""
            dictionnaire['derniere_quantite'] = ""
            pass
        taxe_specifique = TaxeSpecifique.objects.filter(article=x)[:1]
        if taxe_specifique.exists():
            taxe=taxe_specifique[0]
            prixtaux = (taxe.Taux*prix)/100
            dictionnaire['prix_taxe']=prixtaux
            dictionnaire['taux_taxe']=taxe.Taux
        else:
            dictionnaire['prix_taxe']=""
            dictionnaire['taux_taxe']=""
            pass
        cat = Categorie.objects.filter(article=x)[:1]
        if cat.exists():
            categorie=cat[0]
            dictionnaire['categorie']=categorie.Libelle
        else:
            dictionnaire['categorie']=""
            pass
        liste_articles.append(dictionnaire)
        num+=1
        pass
    return liste_articles



def liste_articles(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Article.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                categorie = Categorie.objects.filter(Entreprise=entreprise)
                groupe = GroupeTaxation.objects.all()
                articles=data_article(entreprise)
                return render(request, 'liste-article.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'categorie': categorie, 'groupe': groupe, 'articles': articles, 'maj': date_maj})


def nouvelle_categorie(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                lib=request.POST['lib']
                Categorie.objects.create(Libelle=lib, Entreprise=entreprise)
                element=Categorie.objects.filter(Libelle=lib, Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Libelle, Table="Categorie", Type="Ajout", Operateur=user, Entreprise=entreprise)
                return redirect("/articles/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def nouvel_article(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['nom']
                mesure=request.POST['mesure']
                cat=request.POST['cat']
                typ=request.POST['type']
                gp=request.POST['groupe']
                devise=request.POST['devise']
                groupe = GroupeTaxation.objects.filter(Code=gp)[:1][0]
                mode=request.POST['mode']
                prixht=request.POST['prixht']
                specifique=request.POST['specifique']
                taux=request.POST['taux']
                if cat=="":
                    categorie=None
                else:
                    categorie = Categorie.objects.get(Uuid=cat)
                    pass
                if specifique=="" and taux=="":
                    taxe_specifique=None
                else:
                    TaxeSpecifique.objects.create(Designation=specifique, Taux=taux, Entreprise=entreprise)
                    taxe_specifique = TaxeSpecifique.objects.filter(Designation=specifique, Taux=taux, Entreprise=entreprise)[:1][0]
                    pass
                Article.objects.create(Designation=nom, Type=typ, Categorie=categorie, Groupe=groupe, Devise=devise, Prix=prixht, Mesure=mesure, Mode=mode, Photo='icon-article.png', Taxe_specifique=taxe_specifique, Entreprise=entreprise)
                element=Article.objects.filter(Designation=nom, Type=typ, Categorie=categorie, Groupe=groupe, Devise=devise, Prix=prixht, Mesure=mesure, Mode=mode, Photo='icon-article.png', Taxe_specifique=taxe_specifique, Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Article", Type="Ajout", Operateur=user, Entreprise=entreprise)
                return redirect("/articles/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def delete_article(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_article=request.POST['article_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            article=Article.objects.get(Uuid=id_article)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                Action.objects.create(Element=article.Designation, Table="Article", Type="Suppression", Operateur=user, Entreprise=entreprise)
                article.delete()
                return redirect("/articles/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def one_article(uuid, entreprise):
    article=Article.objects.filter(Uuid=uuid)[:1]
    if article.exists():
        x=article[0]
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['photo']='media/'+str(x.Photo)
        dictionnaire['nom']=x.Designation
        dictionnaire['type']=x.Type
        dictionnaire['date']=x.Date
        dictionnaire['mesure']=x.Mesure
        dictionnaire['mode']=x.Mode
        groupe = GroupeTaxation.objects.filter(article__Groupe=x.Groupe)[:1][0]
        dictionnaire['code_groupe']=groupe.Code
        dictionnaire['groupe']=groupe.Designation
        dictionnaire['taux_groupe']=groupe.Taux
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            prix=x.Prix
            devise=x.Devise
        else:
            taux = liste_taux.Libelle
            devise=entreprise.Devise
            if x.Devise==devise:
                prix=x.Prix
            else:
                if devise=="USD":
                    prix=round(x.Prix/taux, 2)
                else:
                    prix=round(x.Prix*taux, 2) 
                    pass
            pass
        dictionnaire['devise']=devise
        dictionnaire['prixht']=prix
        prixtaux = (groupe.Taux*prix)/100
        dictionnaire['prixttc']=round(prix+prixtaux, 2)
        taxe_specifique = TaxeSpecifique.objects.filter(article=x)[:1]
        if taxe_specifique.exists():
            taxe=taxe_specifique[0]
            prixtaux = (taxe.Taux*prix)/100
            dictionnaire['prix_taxe']=prixtaux
            dictionnaire['taux_taxe']=taxe.Taux
        else:
            dictionnaire['prix_taxe']=""
            dictionnaire['taux_taxe']=""
            pass
        cat = Categorie.objects.filter(article=x)[:1]
        if cat.exists():
            categorie=cat[0]
            dictionnaire['categorie']=categorie.Libelle
        else:
            dictionnaire['categorie']=""
            pass
        stock = Stock.objects.filter(Article=x, Entreprise=entreprise)
        dictionnaire['stock']=len(stock)
        facture = ItemFacture.objects.filter(Article=x)
        dictionnaire['facture']=len(facture)
        devis = ItemDevis.objects.filter(Article=x)
        dictionnaire['devis']=len(devis)
        maj=Facture.objects.filter(itemfacture__Article=x)[:1]
        if maj.exists():
            date=maj[0].Date
        else:
            date="00/00/0000"
            pass
        dictionnaire['maj']=date
        maj_stock=Stock.objects.filter(Article=x).order_by('-Date')[:1]
        if maj_stock.exists():
            last_stock=maj_stock[0].Date
        else:
            last_stock="00/00/0000"
            pass
        dictionnaire['last_stock']=last_stock
        return dictionnaire
        pass


def modif_article(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_article=request.GET['article']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            article=Article.objects.get(Uuid=id_article)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                try:
                    message=request.GET['message']
                except:
                    message=''
                    pass
                maj = Article.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                categorie = Categorie.objects.filter(Entreprise=entreprise)
                groupe = GroupeTaxation.objects.all()
                data = one_article(article.Uuid, entreprise)
                return render(request, 'modif_article.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'categorie': categorie, 'groupe': groupe, 'article': data, 'maj': date_maj, 'message': message})


def photo_article(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_article=request.POST['article_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            article=Article.objects.get(Uuid=id_article)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                photo=request.FILES['photo']
                if not photo=="":
                    try:
                        with open(os.path.join(settings.MEDIA_ROOT, photo.name), 'wb+') as destination:
                            for x in photo.chunks():
                                destination.write(x)
                            pass
                        file="sfe_facturation/static/media/"+str(photo.name)
                        image=Image.open(file)
                        image=image.resize((450, 450))
                        os.remove(file)
                        caracteres = string.ascii_letters + string.digits
                        key = ''.join(choices(caracteres, k=36))
                        name="sfe_facturation/static/media/"+key+str(photo.name)
                        image.save(name, quality=100)
                        maintenant = datetime.now()
                        date = maintenant.strftime("%Y-%m-%d")
                        article.Photo=key+str(photo.name)
                        article.Date=date
                        article.save()
                        Action.objects.create(Element=article.Designation, Table="Article", Type="Modification", Obs="Modification de la photo", Operateur=user, Entreprise=entreprise)
                        return redirect("/modifier_article/?usr={}&com={}&article={}".format(user.Uuid, entreprise.Uuid, article.Uuid))
                    except:
                        message="Le fichier importé n'est pas pris en charge"
                        return redirect("/modifier_article/?usr={}&com={}&article={}&message={}".format(user.Uuid, entreprise.Uuid, article.Uuid, message))
                        pass
                else:
                    message="Aucun fichier n'a été importé"
                    return redirect("/modifier_article/?usr={}&com={}&article={}&message={}".format(user.Uuid, entreprise.Uuid, article.Uuid, message))


def infos_article(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_article=request.POST['article_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            article=Article.objects.filter(Uuid=id_article)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['modif_nom']
                mesure=request.POST['modif_mesure']
                cat=request.POST['modif_cat']
                typ=request.POST['modif_type']
                gp=request.POST['modif_groupe']
                devise=request.POST['modif_devise']
                groupe = GroupeTaxation.objects.filter(Code=gp)[:1][0]
                mode=request.POST['modif_mode']
                prixht=request.POST['modif_prixht']
                specifique=request.POST['modif_specifique']
                taux=request.POST['modif_taux']
                if cat=="":
                    categorie=None
                else:
                    categorie = Categorie.objects.get(Uuid=cat)
                    pass
                if specifique=="" and taux=="":
                    taxe_specifique=None
                else:
                    TaxeSpecifique.objects.create(Designation=specifique, Taux=taux, Entreprise=entreprise)
                    taxe_specifique = TaxeSpecifique.objects.filter(Designation=specifique, Taux=taux, Entreprise=entreprise)[:1][0]
                    pass
                article.update(Designation=nom, Type=typ, Categorie=categorie, Groupe=groupe, Devise=devise, Prix=prixht, Mesure=mesure, Mode=mode, Taxe_specifique=taxe_specifique)
                element=Article.objects.filter(Designation=nom, Type=typ, Categorie=categorie, Groupe=groupe, Devise=devise, Prix=prixht, Mesure=mesure, Mode=mode, Taxe_specifique=taxe_specifique)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Article", Type="Modification", Obs="Modification des informations", Operateur=user, Entreprise=entreprise)
                return redirect("/articles/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def facture_article(uuid, entreprise):
    article=Article.objects.get(Uuid=uuid)
    items=ItemFacture.objects.filter(Article=article)[:10]
    liste_articles=[]
    stat_total=0
    num=1
    for i in items:
        facture=Facture.objects.filter(itemfacture=i)[:1][0]
        dictionnaire=dict()
        dictionnaire['id']=num
        dictionnaire['uuid']=facture.Uuid
        dictionnaire['rn']=facture.RN
        dictionnaire['date']=str(facture.Date)
        try:
            taux=Taux.objects.all().order_by('-Date')[:1][0]
        except:
            montant=facture.Montant
            quantite=i.Montant
        else:
            devise=entreprise.Devise
            if devise==facture.Devise:
                montant=facture.Montant
                quantite=i.Montant
            else:
                if devise=="USD":
                    montant=round(facture.Montant/taux, 2)
                    quantite=round(i.Montant/taux, 2)
                else:
                    montant=round(facture.Montant*taux, 2) 
                    quantite=round(i.Montant*taux, 2) 
                    pass
            pass
        dictionnaire['devise']=devise
        dictionnaire['quantite']=quantite
        dictionnaire['montant']=montant
        dictionnaire['nombre']=i.Quantite
        paiement=Paiement.objects.filter(Facture=facture)
        solde=0
        for x in paiement:
            solde+=x.Montant
            pass
        if solde == 0:
            dictionnaire['statut']="Null"
        elif 0<solde<facture.Montant:
            dictionnaire['statut']="Acompte"
        else:
            dictionnaire['statut']="Solde"
            pass 
        liste_articles.append(dictionnaire)
        num+=1
        stat_total+=quantite
        pass
    return liste_articles, stat_total


def article_stock(article, entreprise):
    articles=Stock.objects.filter(Article=article)
    liste_stock=[]
    num=1
    stat_total=0
    for x in articles:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        if x.Fournisseur==None:
            dictionnaire['fournisseur']=''
        else:
            fournisseur = Acteur.objects.get(stock=x)
            dictionnaire['fournisseur']=fournisseur.Designation
            pass
        try:
            taux = x.Taux        
            pass
        except:
            prix=x.PrixUnitaire
            montant=x.Montant
            devise=x.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Devise:
                prix=x.PrixUnitaire
                montant=x.Montant
            else:
                if devise=="USD":
                    prix=round(x.PrixUnitaire/taux, 2)
                    montant=round(x.Montant/taux, 2)
                else:
                    prix=round(x.PrixUnitaire*taux, 2) 
                    montant=round(x.Montant*taux, 2) 
                    pass
            pass
        dictionnaire['devise']=devise
        dictionnaire['prix']=prix
        dictionnaire['quantite']=x.Quantite
        dictionnaire['date']=x.Date
        dictionnaire['total']=montant
        liste_stock.append(dictionnaire)
        num+=1
        stat_total+=montant
        pass
    return liste_stock, stat_total


def stat_hebdo_article(article, entreprise):
    aujourd_hui = timezone.now()
    cette_semaine = aujourd_hui - timedelta(days=7)
    il_ya_deux_semaine = cette_semaine - timedelta(days=7)
    stock_cette_semaine = Stock.objects.filter(Date__gte=cette_semaine, Article=article)
    nb_stock_cette_semaine = 0
    for x in stock_cette_semaine:
        try:
            taux = x.Taux        
            pass
        except:
            montant=x.Montant
            devise=x.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Devise:
                montant=x.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2) 
                    pass
        nb_stock_cette_semaine+=montant
        pass
    stock_deux_semaine = Stock.objects.filter(Date__range=(il_ya_deux_semaine, cette_semaine), Article=article)
    nb_stock_deux_semaine = 0
    for x in stock_deux_semaine:
        try:
            taux = x.Taux       
            pass
        except:
            montant=x.Montant
            devise=x.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Devise:
                montant=x.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2) 
                    pass
        nb_stock_deux_semaine+=montant
        pass
    try:
        p_stock=((nb_stock_cette_semaine-nb_stock_deux_semaine)*100)/nb_stock_cette_semaine
    except:
        p_stock=0
        pass
    stat_stock=[nb_stock_cette_semaine, p_stock]
    facture_cette_semaine = ItemFacture.objects.filter(Facture__Date__gte=cette_semaine, Article=article)
    nb_facture_cette_semaine = 0
    nb_paiement_cette_semaine = 0
    for x in facture_cette_semaine:
        #On calcule le montant de la facture et de l'article selon la devise par defaut de l'entreprise et le taux de la facture
        try:
            taux=Taux.objects.all().order_by('-Date')[:1][0]
        except:
            montant_facture=x.Facture.Montant
            montant=x.Montant
            devise=x.Facture.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Facture.Devise:
                montant=x.Montant
                montant_facture=x.Facture.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                    montant_facture=round(x.Facture.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2)
                    montant_facture=round(x.Facture.Montant*taux, 2) 
                    pass
        nb_facture_cette_semaine+=montant
        #On calcule le % de l'article dans le montant total de la facture
        p_article=(montant*100)/montant_facture
        p_article_montant=0
        paiements=Paiement.objects.filter(Date__gte=cette_semaine, Facture=x.Facture)
        # On incrémente dans la variable p_article_montant ce % dans chaque paiement de cette facture  
        for i in paiements:
            p_montant=(p_article*i.Montant)/100
            p_article_montant+=p_montant
            pass
        nb_paiement_cette_semaine+=p_article_montant
        pass
    facture_deux_semaine = ItemFacture.objects.filter(Facture__Date__range=(il_ya_deux_semaine, cette_semaine), Article=article)
    nb_facture_deux_semaine = 0
    nb_paiement_deux_semaine = 0
    for x in facture_deux_semaine:
        #On calcule le montant de la facture et de l'article selon la devise par defaut de l'entreprise et le taux de la facture
        try:
            taux=Taux.objects.all().order_by('-Date')[:1][0]
        except:
            montant_facture=x.Facture.Montant
            montant=x.Montant
            devise=x.Facture.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Facture.Devise:
                montant=x.Montant
                montant_facture=x.Facture.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                    montant_facture=round(x.Facture.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2)
                    montant_facture=round(x.Facture.Montant*taux, 2) 
                    pass
        nb_facture_deux_semaine+=montant
        #On calcule le % de l'article dans le montant total de la facture
        p_article=(montant*100)/montant_facture
        p_article_montant=0
        paiements=Paiement.objects.filter(Date__gte=cette_semaine, Facture=x.Facture)
        # On incrémente dans la variable p_article_montant ce % dans chaque paiement de cette facture  
        for i in paiements:
            p_montant=(p_article*i.Montant)/100
            p_article_montant+=p_montant
            pass
        nb_paiement_deux_semaine+=p_article_montant
        pass
    try:
        p_facture=((nb_facture_cette_semaine-nb_facture_deux_semaine)*100)/nb_facture_cette_semaine
    except:
        p_facture=0
        pass
    stat_facture=[nb_facture_cette_semaine, p_facture]
    try:
        p_paiement=((nb_paiement_cette_semaine-nb_paiement_deux_semaine)*100)/nb_paiement_cette_semaine
    except:
        p_paiement=0
        pass
    stat_paiement=[nb_paiement_cette_semaine, p_paiement]
    return stat_stock, stat_facture, stat_paiement


def stat_gen(article, entreprise):
    facture = ItemFacture.objects.filter(Article=article)
    stat_paiement=0
    for x in facture:
        try:
            taux=Taux.objects.all().order_by('-Date')[:1][0]
        except:
            montant_facture=x.Facture.Montant
            montant=x.Montant
            devise=x.Facture.Devise
        else:
            devise=entreprise.Devise
            if devise==x.Facture.Devise:
                montant=x.Montant
                montant_facture=x.Facture.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                    montant_facture=round(x.Facture.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2)
                    montant_facture=round(x.Facture.Montant*taux, 2) 
                    pass
        p_article=(montant*100)/montant_facture
        paiements=Paiement.objects.filter(Facture=x.Facture)
        # On incrémente dans la variable p_article_montant ce % dans chaque paiement de cette facture  
        for i in paiements:
            p_montant=(p_article*i.Montant)/100
            stat_paiement+=p_montant
            pass
    devis=ItemDevis.objects.filter(Article=article)
    stat_devis=0
    for x in devis:
        try:
            taux = Taux.objects.all().order_by('-Date')[:1][0]        
            pass
        except:
            montant=x.Montant
        else:
            devise=entreprise.Devise
            if devise==x.Devis.Devise:
                montant=x.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2)
                    pass
        stat_devis+=montant
        pass
    return stat_paiement, stat_devis
    pass


def stat_mois_article(article, entreprise):
    variable1 = 5
    variable2 = 4
    liste_stat=[]
    liste_mois=[]
    while variable1 > 0:
        date_debut = date.today() - relativedelta(months=variable1)
        date_fin = date.today() - relativedelta(months=variable2)
        liste_mois.append(str(date_debut))
        labels=[]

        stock_par_mois = (
            Stock.objects
            .filter(Date__range=(date_debut, date_fin), Article=article)
            .order_by('Date')
        )
        if not stock_par_mois.exists():
            labels.append(0)
        else:
            nb_stock=0
            for x in stock_par_mois:
                try:
                    taux = x.Taux       
                    pass
                except:
                    montant=x.Montant
                    devise=x.Devise
                else:
                    devise=entreprise.Devise
                    if devise==x.Devise:
                        montant=x.Montant
                    else:
                        if devise=="USD":
                            montant=round(x.Montant/taux, 2)
                        else:
                            montant=round(x.Montant*taux, 2) 
                            pass
                nb_stock+=montant
                pass
            labels.append(nb_stock)
            pass

        facture_par_mois = (
            ItemFacture.objects
            .filter(Facture__Date__range=(date_debut, date_fin), Article=article)
            .order_by('Facture__Date')
        )
        if not facture_par_mois.exists():
            labels.extend([0, 0])
        else:
            p_article_montant=0
            nb_facture=0
            for x in facture_par_mois:
            #On calcule le montant de la facture et de l'article selon la devise par defaut de l'entreprise et le taux de la facture
                try:
                    taux=Taux.objects.all().order_by('-Date')[:1][0]
                except:
                    montant_facture=x.Facture.Montant
                    montant=x.Montant
                    devise=x.Facture.Devise
                else:
                    devise=entreprise.Devise
                    if devise==x.Facture.Devise:
                        montant=x.Montant
                        montant_facture=x.Facture.Montant
                    else:
                        if devise=="USD":
                            montant=round(x.Montant/taux, 2)
                            montant_facture=round(x.Facture.Montant/taux, 2)
                        else:
                            montant=round(x.Montant*taux, 2)
                            montant_facture=round(x.Facture.Montant*taux, 2) 
                            pass
                nb_facture+=montant
                #On calcule le % de l'article dans le montant total de la facture
                p_article=(montant*100)/montant_facture
                paiements=Paiement.objects.filter(Date__range=(date_debut, date_fin), Facture=x.Facture)
                # On incrémente dans la variable p_article_montant ce % dans chaque paiement de cette facture  
                for i in paiements:
                    p_montant=(p_article*i.Montant)/100
                    p_article_montant+=p_montant
                    pass
            labels.extend([montant, p_article_montant])
            pass
        
        liste_stat.append(labels)
        variable1-=1
        variable2-=1
        pass 
    return liste_mois, liste_stat
    pass


def details_article(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_article=request.GET['article']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            article=Article.objects.get(Uuid=id_article)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Article.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                data = one_article(article.Uuid, entreprise)
                gen_stat=stat_gen(article, entreprise)
                graph_stat=[article_stock(article, entreprise)[1], facture_article(article.Uuid, entreprise)[1], stat_gen(article, entreprise)[0], stat_gen(article, entreprise)[1]]
                article_facture  = facture_article(article.Uuid, entreprise)[0]
                stock_article  = article_stock(article, entreprise)[0]
                stat_stock = stat_hebdo_article(article, entreprise)[0]
                stat_facture = stat_hebdo_article(article, entreprise)[1]
                stat_paiement = stat_hebdo_article(article, entreprise)[2]
                mois_label = stat_mois_article(article, entreprise)[0]
                mois_data = stat_mois_article(article, entreprise)[1]
                stat_mois_stock=[]
                stat_mois_paiement=[]
                stat_mois_facture=[]
                for i in mois_data:
                    stat_mois_stock.append(i[0])
                    stat_mois_facture.append(i[1])
                    stat_mois_paiement.append(i[2])
                    pass
                return render(request, 'details_article.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'article': data, 'maj': date_maj, 'article_facture': article_facture, 'stock': stock_article, 'stat_stock': stat_stock, 'stat_facture': stat_facture, 'stat_paiement': stat_paiement, 'graph_stat': graph_stat, 'mois_label':mois_label, 'stat_mois_stock': stat_mois_stock, 'stat_mois_facture': stat_mois_facture, 'stat_mois_paiement': stat_mois_paiement})


def nouveau_fournisseur(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['nom']
                typ=request.POST['type']
                refdoc=request.POST['refdoc']
                nif=request.POST['nif']
                tel=request.POST['tel']
                email=request.POST['email']
                adresse=request.POST['adresse']
                try:
                    type_acteur=TypeActeur.objects.get(Code=typ)
                except:
                    type_acteur=None 
                    pass
                Acteur.objects.create(Designation=nom, Type=type_acteur, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Model='F', Profil='user.png', Entreprise=entreprise)
                element=Acteur.objects.filter(Designation=nom, Type=type_acteur, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Model='F', Profil='user.png', Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Fournisseur", Type="Ajout", Operateur=user, Entreprise=entreprise)
                return redirect("/fournisseurs/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def data_client(entreprise):
    articles=Acteur.objects.filter(Model__in=['C', 'CF'], Entreprise=entreprise)
    liste_clients=[]
    num=1
    for x in articles:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        dictionnaire['photo']='media/'+str(x.Profil)
        dictionnaire['nom']=x.Designation
        if x.Type==None:
            typ=''
        else:
            typ=x.Type.Libelle
            pass
        dictionnaire['type']=typ
        dictionnaire['num']=x.Telephone
        dictionnaire['email']=x.Email
        dictionnaire['adresse']=x.Adresse
        dictionnaire['nif']=x.Nif
        dictionnaire['ref']=x.Refdoc
        liste_clients.append(dictionnaire)
        num+=1
        pass
    return liste_clients


def liste_clients(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
    except:
        return render(request, 'page-login.html')
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Acteur.objects.filter(Model='C', Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                clients = data_client(entreprise)
                nbr=len(clients)
                return render(request, 'liste-user.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'clients': clients, 'maj': date_maj, 'nbr': nbr})


def nouveau_client(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['nom']
                typ=request.POST['type']
                refdoc=request.POST['refdoc']
                nif=request.POST['nif']
                tel=request.POST['tel']
                email=request.POST['email']
                adresse=request.POST['adresse']
                try:
                    typ=TypeActeur.objects.get(Code=typ)
                except:
                    typ=None 
                    pass
                Acteur.objects.create(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Model='C', Profil='user.png', Entreprise=entreprise)
                element=Acteur.objects.filter(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Model='C', Profil='user.png', Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Client", Type="Ajout", Operateur=user, Entreprise=entreprise)
                return redirect("/clients/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def data_stock(entreprise):
    articles=Stock.objects.filter(Entreprise=entreprise)
    liste_stock=[]
    num=1
    for x in articles:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        article = Article.objects.get(stock=x)
        dictionnaire['photo_article']='media/'+str(article.Photo)
        dictionnaire['id_article']=article.Uuid
        dictionnaire['article']=article.Designation
        dictionnaire['type_article']=article.Type
        if x.Fournisseur==None:
            dictionnaire['photo_fournisseur']='media/user.png'
            dictionnaire['fournisseur']=''
            dictionnaire['type_fournisseur']=''
        else:
            fournisseur = Acteur.objects.get(stock=x)
            dictionnaire['id_fournisseur']=fournisseur.Uuid
            dictionnaire['photo_fournisseur']='media/'+str(fournisseur.Profil)
            dictionnaire['fournisseur']=fournisseur.Designation
            dictionnaire['type_fournisseur']=fournisseur.Type.Libelle
            pass
        taux = x.Taux
        devise=entreprise.Devise
        if x.Devise==devise:
            prix=x.PrixUnitaire
        else:
            if devise=="USD":
                prix=round(x.PrixUnitaire/taux, 2)
            else:
                prix=round(x.PrixUnitaire*taux, 2) 
                pass
        dictionnaire['devise']=devise
        dictionnaire['prix']=prix
        dictionnaire['quantite']=x.Quantite
        dictionnaire['date']=x.Date
        dictionnaire['heure']=x.Heure
        dictionnaire['total']=round(prix*x.Quantite, 2)
        liste_stock.append(dictionnaire)
        num+=1
        pass
    return liste_stock


def liste_stock(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
    except:
        return render(request, 'page-login.html')
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Stock.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                articles = Article.objects.filter(Entreprise=entreprise)
                fournisseurs = Acteur.objects.filter(Model__in=['F', 'CF'], Entreprise=entreprise)
                stock = data_stock(entreprise)
                return render(request, 'liste-stock.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'articles': articles, 'fournisseurs': fournisseurs, 'stock': stock, 'maj': date_maj, 'entreprise': entreprise})


def nouveau_stock(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                id_article=request.POST['article']
                article=Article.objects.get(Uuid=id_article)
                id_fournisseur=request.POST['fournisseur']
                if id_fournisseur=="":
                    fournisseur=None
                else:
                    fournisseur=Acteur.objects.get(Uuid=id_fournisseur)
                    pass
                prix=int(request.POST['prix'])
                quantite=int(request.POST['quantite'])
                devise=request.POST['devise']
                try:
                    liste_taux=Taux.objects.all().order_by('-Date')[:1][0][0]
                    taux=liste_taux.Libelle
                    pass
                except:
                    taux=2263
                    pass
                total=prix*quantite
                Stock.objects.create(Article=article, Devise=devise, Taux=taux, Fournisseur=fournisseur, PrixUnitaire=prix, Quantite=quantite, Montant=total, Entreprise=entreprise)
                element=Stock.objects.filter(Article=article, Devise=devise, Taux=taux, Fournisseur=fournisseur, PrixUnitaire=prix, Quantite=quantite, Montant=total, Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Uuid, Table="Categorie", Type="Ajout", Operateur=user, Entreprise=entreprise)
                return redirect("/stock/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def delete_stock(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_stock=request.POST['stock_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            stock=Stock.objects.get(Uuid=id_stock)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                Action.objects.create(Element=stock.Uuid, Table="Stock", Type="Suppression", Obs="Date: {} | Fournisseur: {} | Article: {} | Quantite: {}".format(stock.Date, str(stock.Fournisseur), stock.Article.Designation, stock.Quantite), Operateur=user, Entreprise=entreprise)
                stock.delete()
                return redirect("/stock/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def one_stock(stock, entreprise):
    x = stock
    dictionnaire=dict()
    dictionnaire['uuid']=x.Uuid
    article = Article.objects.get(stock=x)
    dictionnaire['photo_article']='media/'+str(article.Photo)
    dictionnaire['id_article']=article.Uuid
    dictionnaire['article']=article.Designation
    dictionnaire['type_article']=article.Type
    dictionnaire['maj_article']=article.Date
    if x.Fournisseur==None:
        dictionnaire['photo_fournisseur']='media/user.png'
        dictionnaire['fournisseur']=''
        dictionnaire['type_fournisseur']=''
    else:
        fournisseur = Acteur.objects.get(stock=x)
        dictionnaire['id_fournisseur']=fournisseur.Uuid
        dictionnaire['photo_fournisseur']='media/'+str(fournisseur.Profil)
        dictionnaire['fournisseur']=fournisseur.Designation
        dictionnaire['type_fournisseur']=fournisseur.Type.Libelle
        dictionnaire['date_fournisseur']=fournisseur.Date
        pass
    taux = x.Taux
    devise=entreprise.Devise
    if x.Devise==devise:
        prix=x.PrixUnitaire
    else:
        if devise=="USD":
            prix=round(x.PrixUnitaire/taux, 2)
        else:
            prix=round(x.PrixUnitaire*taux, 2) 
            pass
    dictionnaire['devise']=devise
    dictionnaire['prix']=prix
    dictionnaire['quantite']=x.Quantite
    dictionnaire['date']=x.Date
    dictionnaire['heure']=x.Heure
    dictionnaire['total']=round(prix*x.Quantite, 2)
    return dictionnaire


def modif_stock(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_stock=request.GET['stock']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            stock=Stock.objects.get(Uuid=id_stock)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Stock.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                articles = Article.objects.filter(Entreprise=entreprise)
                fournisseurs = Acteur.objects.filter(Model__in=['F', 'CF'], Entreprise=entreprise)
                stock=one_stock(stock, entreprise)
                return render(request, 'modif_stock.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'articles': articles, 'fournisseurs': fournisseurs, 'maj': date_maj, 'stock': stock})


def modif_infos_stock(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_stock=request.POST['stock']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            stock=Stock.objects.filter(Uuid=id_stock)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                id_article=request.POST['article']
                article=Article.objects.get(Uuid=id_article)
                id_fournisseur=request.POST['fournisseur']
                if id_fournisseur=="":
                    fournisseur=None
                else:
                    fournisseur=Acteur.objects.get(Uuid=id_fournisseur)
                    pass
                prix=int(request.POST['prix'])
                quantite=int(request.POST['quantite'])
                devise=request.POST['devise']
                try:
                    liste_taux=Taux.objects.all().order_by('-Date')[:1][0][0]
                    taux=liste_taux.Libelle
                    pass
                except:
                    taux=2263
                    pass
                total=prix*quantite
                stock.update(Article=article, Devise=devise, Taux=taux, Fournisseur=fournisseur, PrixUnitaire=prix, Quantite=quantite, Montant=total, Entreprise=entreprise)
                Action.objects.create(Element=stock[0].Uuid, Table="Stock", Type="Modification", Obs="Modification des informations", Operateur=user, Entreprise=entreprise)
                return redirect("/stock/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def one_actor(acteur, entreprise):
    x=acteur
    dictionnaire=dict()
    dictionnaire['uuid']=x.Uuid
    dictionnaire['photo']='media/'+str(x.Profil)
    dictionnaire['date']=x.Date
    dictionnaire['nom']=x.Designation
    if x.Type==None:
        typ=''
        code_type=''
    else:
        typ=x.Type.Libelle
        code_type=x.Type.Code
        pass
    dictionnaire['type']=typ
    dictionnaire['code']=code_type
    dictionnaire['num']=x.Telephone
    dictionnaire['email']=x.Email
    dictionnaire['adresse']=x.Adresse
    dictionnaire['nif']=x.Nif
    dictionnaire['ref']=x.Refdoc
    stock=Stock.objects.filter(Fournisseur=x)
    dictionnaire['stock']=len(stock)
    quantite=0
    total=0
    for i in stock:
        quantite+=i.Quantite
        taux = i.Taux
        devise=entreprise.Devise
        if i.Devise==devise:
            prix=i.PrixUnitaire
        else:
            if devise=="USD":
                prix=round(i.PrixUnitaire/taux, 2)
            else:
                prix=round(i.PrixUnitaire*taux, 2) 
                pass
        total+=(prix*i.Quantite)
        pass
    dictionnaire['quantite']=quantite
    dictionnaire['total']=total
    last_stock=Stock.objects.filter(Fournisseur=x).order_by('-Date')[:1]
    if last_stock.exists():
        date=last_stock[0].Date
    else:
        date='00/00/0000'
        pass
    dictionnaire['last_stock']=date
    facture=Facture.objects.filter(Client=x)
    paiement=Paiement.objects.filter(Facture__Client=x)
    nb_facture=len(facture)
    nb_paiement=len(paiement)
    total_facture=0
    for x in facture:
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            devise=x.Facture.Devise
            montant=facture.Montant
        else:
            taux = liste_taux.Libelle
            devise=entreprise.Devise
            if x.Devise==devise:
                montant=x.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2) 
                    pass
            pass
        total_facture+=montant
        pass 
    dictionnaire['nb_facture']=nb_facture
    dictionnaire['nb_paiement']=nb_paiement
    total_paiement=0
    for x in paiement:
        taux = x.Taux
        devise=entreprise.Devise
        if x.Devise==devise:
            montant=x.Montant
        else:
            if devise=="USD":
                montant=round(facture.Montant/taux, 2)
            else:
                montant=round(facture.Montant*taux, 2) 
                pass
            pass
        total_paiement+=montant
        pass 
    statut_client = total_paiement- total_facture
    dictionnaire['statut_client']=statut_client
    return dictionnaire
    pass


def historique_fournisseur(fournisseur, entreprise):
    stock=Stock.objects.filter(Fournisseur=fournisseur)
    liste_stock=[]
    num=1
    for x in stock:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        article = Article.objects.get(stock=x)
        dictionnaire['article']=article.Designation
        taux = x.Taux
        devise=entreprise.Devise
        if x.Devise==devise:
            prix=x.PrixUnitaire
        else:
            if devise=="USD":
                prix=round(x.PrixUnitaire/taux, 2)
            else:
                prix=round(x.PrixUnitaire*taux, 2) 
                pass
        dictionnaire['devise']=devise
        dictionnaire['prix']=prix
        dictionnaire['quantite']=x.Quantite
        dictionnaire['date']=x.Date
        dictionnaire['total']=round(prix*x.Quantite, 2)
        liste_stock.append(dictionnaire)
        num+=1
        pass
    return liste_stock


def details_stock(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_stock=request.GET['stock']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            object_stock=Stock.objects.get(Uuid=id_stock)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Stock.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                articles = Article.objects.filter(Entreprise=entreprise)
                fournisseurs = Acteur.objects.filter(Model__in=['F', 'CF'], Entreprise=entreprise)
                stock=one_stock(object_stock, entreprise)
                article=one_article(object_stock.Article.Uuid, entreprise)
                if object_stock.Fournisseur==None:
                    acteur=""
                    fournisseur_historique=[]
                else:
                    data_acteur=Acteur.objects.get(Uuid=object_stock.Fournisseur.Uuid)
                    acteur=one_actor(data_acteur, entreprise)
                    fournisseur_historique=historique_fournisseur(data_acteur, entreprise)
                    pass
                object_article = Article.objects.get(Uuid=object_stock.Article.Uuid)
                stock_article  = article_stock(object_article, entreprise)[0]
                return render(request, 'details_stock.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'articles': articles, 'fournisseurs': fournisseurs, 'maj': date_maj, 'stock': stock, 'article': article, 'stock_article': stock_article, 'acteur': acteur, 'historique_fournisseur': fournisseur_historique})


def data_fournisseur(entreprise):
    articles=Acteur.objects.filter(Model__in=['F', 'CF'], Entreprise=entreprise)
    liste_fournisseurs=[]
    num=1
    for x in articles:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['id']=num
        dictionnaire['photo']='media/'+str(x.Profil)
        dictionnaire['nom']=x.Designation
        if x.Type==None:
            typ=''
        else:
            typ=x.Type.Code
            pass
        dictionnaire['type']=typ
        dictionnaire['num']=x.Telephone
        dictionnaire['email']=x.Email
        dictionnaire['adresse']=x.Adresse
        dictionnaire['nif']=x.Nif
        dictionnaire['ref']=x.Refdoc
        liste_fournisseurs.append(dictionnaire)
        num+=1
        pass
    return liste_fournisseurs


def liste_fournisseurs(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
    except:
        return render(request, 'page-login.html')
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Acteur.objects.filter(Model='F', Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                fournisseurs = data_fournisseur(entreprise)
                return render(request, 'liste-fournisseurs.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'fournisseurs': fournisseurs, 'maj': date_maj})


def client_fournisseur(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                id_acteur = request.POST['uuid']
                acteur = Acteur.objects.get(Uuid=id_acteur)
                avant = acteur.Model
                acteur.Model = 'CF'
                acteur.save()
                if avant=='C':
                    Action.objects.create(Element=acteur.Designation, Table="Fournisseur", Type="Ajout", Operateur=user, Entreprise=entreprise)
                    return redirect("/fournisseurs/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                else:
                    Action.objects.create(Element=acteur.Designation, Table="Client", Type="Ajout", Operateur=user, Entreprise=entreprise)
                    return redirect("/clients/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                    pass

def delete_fournisseur(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                Action.objects.create(Element=acteur.Designation, Table="Fournisseur", Type="Suppression", Operateur=user, Entreprise=entreprise)
                if acteur.Model=='CF':
                    acteur.Model='C'
                    stock=Stock.objects.filter(Fournisseur=acteur, Entreprise=entreprise).delete()
                    acteur.save()
                else:
                    acteur.delete()
                    pass
                return redirect("/fournisseurs/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))


def delete_client(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                Action.objects.create(Element=acteur.Designation, Table="Client", Type="Suppression", Operateur=user, Entreprise=entreprise)
                if acteur.Model=='CF':
                    acteur.Model='F'
                    acteur.save()
                    facture=Facture.objects.filter(Client=acteur, Entreprise=entreprise).delete()
                else:
                    acteur.delete()
                    pass
                return redirect("/clients/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))


def modif_fournisseur(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_acteur=request.GET['acteur']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            data_acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                try:
                    message=request.GET['message']
                except:
                    message=''
                    pass
                maj = Acteur.objects.filter(Model='F', Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                fournisseurs = data_fournisseur(entreprise)
                acteur=one_actor(data_acteur, entreprise)
                return render(request, 'modif_fournisseur.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'fournisseurs': fournisseurs, 'maj': date_maj, 'acteur': acteur, 'message': message})


def infos_fournisseur(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.filter(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['nom']
                typ=request.POST['type']
                refdoc=request.POST['refdoc']
                nif=request.POST['nif']
                tel=request.POST['tel']
                email=request.POST['email']
                adresse=request.POST['adresse']
                try:
                    typ=TypeActeur.objects.get(Code=typ)
                except:
                    typ=None 
                    pass
                acteur.update(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Entreprise=entreprise)
                element=Acteur.objects.filter(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Fournisseur", Type="Modification", Obs="Modification des informations", Operateur=user, Entreprise=entreprise)
                return redirect("/fournisseurs/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def modif_client(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_acteur=request.GET['acteur']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            data_acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                try:
                    message=request.GET['message']
                except:
                    message=''
                    pass
                maj = Acteur.objects.filter(Model='F', Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                fournisseurs = data_fournisseur(entreprise)
                acteur=one_actor(data_acteur, entreprise)
                return render(request, 'modif_client.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'fournisseurs': fournisseurs, 'maj': date_maj, 'acteur': acteur, 'message': message})


def infos_client(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.filter(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                nom=request.POST['nom']
                typ=request.POST['type']
                refdoc=request.POST['refdoc']
                nif=request.POST['nif']
                tel=request.POST['tel']
                email=request.POST['email']
                adresse=request.POST['adresse']
                try:
                    typ=TypeActeur.objects.get(Code=typ)
                except:
                    typ=None 
                    pass
                acteur.update(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Entreprise=entreprise)
                element=Acteur.objects.filter(Designation=nom, Type=typ, Refdoc=refdoc, Nif=nif, Telephone=tel, Adresse=adresse, Email=email, Entreprise=entreprise)[:1][0]
                Action.objects.create(Element=element.Designation, Table="Client", Type="Modification", Obs="Modification des informations", Operateur=user, Entreprise=entreprise)
                return redirect("/clients/?usr={}&com={}".format(user.Uuid, entreprise.Uuid))
                pass


def photo_fournisseur(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                photo=request.FILES['photo']
                if not photo=="":
                    try:
                        with open(os.path.join(settings.MEDIA_ROOT, photo.name), 'wb+') as destination:
                            for x in photo.chunks():
                                destination.write(x)
                            pass
                        file="sfe_facturation/static/media/"+str(photo.name)
                        image=Image.open(file)
                        image=image.resize((450, 450))
                        os.remove(file)
                        caracteres = string.ascii_letters + string.digits
                        key = ''.join(choices(caracteres, k=36))
                        name="sfe_facturation/static/media/"+key+str(photo.name)
                        image.save(name, quality=100)
                        maintenant = datetime.now()
                        date = maintenant.strftime("%Y-%m-%d")
                        acteur.Profil=key+str(photo.name)
                        acteur.Date=date
                        acteur.save()
                        Action.objects.create(Element=acteur.Designation, Table="Fournisseur", Type="Modification", Obs="Modification de la photo", Operateur=user, Entreprise=entreprise)
                        return redirect("/modifier_fournisseur/?usr={}&com={}&acteur={}".format(user.Uuid, entreprise.Uuid, acteur.Uuid))
                    except:
                        message="Le fichier importé n'est pas pris en charge"
                        return redirect("/modifier_fournisseur/?usr={}&com={}&acteur={}&message={}".format(user.Uuid, entreprise.Uuid, acteur.Uuid, message))
                        pass
                else:
                    message="Aucun fichier n'a été importé"
                    return redirect("/modifier_fournisseur/?usr={}&com={}&article={}&message={}".format(user.Uuid, entreprise.Uuid, article.Uuid, message))


def photo_client(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_acteur=request.POST['acteur_id']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                photo=request.FILES['photo']
                if not photo=="":
                    try:
                        with open(os.path.join(settings.MEDIA_ROOT, photo.name), 'wb+') as destination:
                            for x in photo.chunks():
                                destination.write(x)
                            pass
                        file="sfe_facturation/static/media/"+str(photo.name)
                        image=Image.open(file)
                        image=image.resize((450, 450))
                        os.remove(file)
                        caracteres = string.ascii_letters + string.digits
                        key = ''.join(choices(caracteres, k=36))
                        name="sfe_facturation/static/media/"+key+str(photo.name)
                        image.save(name, quality=100)
                        maintenant = datetime.now()
                        date = maintenant.strftime("%Y-%m-%d")
                        acteur.Profil=key+str(photo.name)
                        acteur.Date=date
                        acteur.save()
                        Action.objects.create(Element=acteur.Designation, Table="Client", Type="Modification", Obs="Modification de la photo", Operateur=user, Entreprise=entreprise)
                        return redirect("/modifier_client/?usr={}&com={}&acteur={}".format(user.Uuid, entreprise.Uuid, acteur.Uuid))
                    except:
                        message="Le fichier importé n'est pas pris en charge"
                        return redirect("/modifier_client/?usr={}&com={}&acteur={}&message={}".format(user.Uuid, entreprise.Uuid, acteur.Uuid, message))
                        pass
                else:
                    message="Aucun fichier n'a été importé"
                    return redirect("/modifier_client/?usr={}&com={}&article={}&message={}".format(user.Uuid, entreprise.Uuid, article.Uuid, message))


def details_fournisseur(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        id_acteur=request.GET['acteur']
        pass
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            data_acteur=Acteur.objects.get(Uuid=id_acteur)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Acteur.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                acteur=one_actor(data_acteur, entreprise)
                fournisseur_historique=historique_fournisseur(data_acteur, entreprise)
                return render(request, 'details_fournisseur.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'maj': date_maj, 'acteur': acteur, 'historique_fournisseur': fournisseur_historique})


def liste_commandes(entreprise):
    commandes=Facture.objects.filter(Entreprise=entreprise)
    liste=[]
    num=1
    for x in commandes:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['code']=x.RN
        dictionnaire['id']=num
        dictionnaire['profil_client']='media/'+str(x.Client.Profil)
        dictionnaire['client']=x.Client.Designation
        dictionnaire['id_client']=x.Client.Uuid
        dictionnaire['type_client']=x.Client.Type.Libelle
        dictionnaire['date']=str(x.Date)
        comments=Commentaire.objects.filter(Facture=x)
        items=ItemFacture.objects.filter(Facture=x)
        paiement=Paiement.objects.filter(Facture=x)
        paye=0
        quantite=0
        for i in items:
            quantite+=i.Quantite
            pass
        for i in paiement:
            taux = i.Taux
            devise=entreprise.Devise
            if i.Devise==devise:
                prix=i.Montant
            else:
                if devise=="USD":
                    prix=round(i.Montant/taux, 2)
                else:
                    prix=round(i.Montant*taux, 2) 
                    pass
            paye+=prix
            pass
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            montant=x.Montant
            devise=x.Devise
        else:
            taux=liste_taux
            devise=entreprise.Devise
            if x.Devise==devise:
                montant=x.Montant
            else:
                if devise=="USD":
                    montant=round(x.Montant/taux, 2)
                else:
                    montant=round(x.Montant*taux, 2) 
                    pass
        dictionnaire['nbr_paies']=len(paiement)
        dictionnaire['articles']=items
        dictionnaire['total']=montant
        dictionnaire['paye']=paye
        dictionnaire['solde']=montant-paye
        dictionnaire['devise']=devise
        dictionnaire['nbr_articles']=len(items)
        dictionnaire['quantite']=quantite
        progression=(paye*100)/x.Montant
        dictionnaire['progression']=int(progression)
        liste.append(dictionnaire)
        num+=1
        pass
    return liste
    pass


def facturation(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
    except:
        return render(request, 'page-login.html')
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                try:
                    message=request.GET['message']
                    titre=request.GET['titre']
                except:
                    message=''
                    titre=''
                    pass
                maj = Facture.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                clients = data_client(entreprise)
                articles=data_article(entreprise)
                data=liste_commandes(entreprise)
                nbr=len(data)
                return render(request, 'facturation.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'clients': clients, 'articles': articles, 'maj': date_maj, 'commandes': data, 'nbr': nbr, 'message': message, 'titre': titre})


def liste_items(items, entreprise):
    liste_articles=[]
    num=1
    for x in items:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Article.Uuid
        dictionnaire['id']=num
        dictionnaire['photo']='media/'+str(x.Article.Photo)
        dictionnaire['nom']=x.Article.Designation
        dictionnaire['type']=x.Article.Type
        dictionnaire['quantite']=x.Quantite
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            prix=x.Article.Prix
            devise=x.Facture.Devise
        else:
            taux = liste_taux.Libelle
            devise=entreprise.Devise
            if x.Facture.Devise==devise:
                prix=x.Article.Prix
            else:
                if devise=="USD":
                    prix=round(x.Article.Prix/taux, 2)
                else:
                    prix=round(x.Article.Prix*taux, 2) 
                    pass
            pass
        dictionnaire['devise']=devise
        dictionnaire['prix']=prix
        groupe = GroupeTaxation.objects.filter(article__Groupe=x.Article.Groupe)[:1][0]
        dictionnaire['groupe']=''.join(['[', groupe.Code, ']', str(groupe.Taux), '%'])
        dictionnaire['code_groupe']=groupe.Code
        prixtaux = round((groupe.Taux*prix)/100, 2)
        dictionnaire['prixtaux']=prixtaux
        dictionnaire['prixttc']=int(prix+prixtaux)
        dictionnaire['total']=(prix+prixtaux)*x.Quantite
        liste_articles.append(dictionnaire)
        num+=1
        pass
    return liste_articles


def one_facture(facture, entreprise):
    dictionnaire=dict()
    dictionnaire['uuid']=facture.Uuid
    dictionnaire['code']=facture.RN
    dictionnaire['date']=facture.Date
    dictionnaire['mode']=facture.ModeFacture
    dictionnaire['client']=facture.Client.Designation
    items=ItemFacture.objects.filter(Facture=facture)
    quantite=0
    total_ht=0
    total_tva=0
    for x in items:
        quantite+=x.Quantite
        try:
            liste_taux = Taux.objects.all().order_by('-Date')[:1][0]         
            pass
        except:
            prix=x.Article.Prix
            devise=x.Facture.Devise
            montant=facture.Montant
        else:
            taux = liste_taux.Libelle
            devise=entreprise.Devise
            if x.Facture.Devise==devise:
                prix=x.Article.Prix
                montant=facture.Montant
            else:
                if devise=="USD":
                    prix=round(x.Article.Prix/taux, 2)
                    montant=round(facture.Montant/taux, 2)
                else:
                    prix=round(x.Article.Prix*taux, 2) 
                    montant=round(facture.Montant*taux, 2) 
                    pass
            pass
        total_ht+=prix
        pass
    total_tva=round(montant-total_ht, 2)
    dictionnaire['total']=montant
    dictionnaire['items']=quantite
    dictionnaire['total_ht']=total_ht
    dictionnaire['total_tva']=total_tva
    paiement=0
    paiements=Paiement.objects.filter(Facture=facture)
    for x in paiements:
        taux = x.Taux
        devise=entreprise.Devise
        if x.Devise==devise:
            prix=x.Montant
        else:
            if devise=="USD":
                prix=round(x.Montant/taux, 2)
            else:
                prix=round(x.Montant*taux, 2) 
                pass
        paiement+=prix
        pass
    solde=paiement-montant
    reste=montant-paiement
    dictionnaire['paiement']=paiement
    dictionnaire['solde']=solde
    dictionnaire['reste']=reste
    dictionnaire['devise']=devise
    dernier_paie=Paiement.objects.all().order_by('-Date')[:1]
    if dernier_paie.exists():
        dernier_maj=dernier_paie[0].Date
    else:
        dernier_maj=facture.Date
        pass 
    dictionnaire['maj']=dernier_maj
    last_paiement=Paiement.objects.filter(Facture=facture).order_by('-Date')[:1]
    if last_paiement.exists():
        last_date=last_paiement[0].Date
    else:
        last_date='00/00/0000'
        pass
    dictionnaire['last_date']=last_date
    return dictionnaire
    pass


def liste_paiement(facture, entreprise):
    paiement=Paiement.objects.filter(Facture=facture)
    liste_paiement=[]
    num=1
    for x in paiement:
        dictionnaire=dict()
        dictionnaire['uuid']=x.Uuid
        dictionnaire['code']=x.Code
        dictionnaire['id']=num
        dictionnaire['date']=x.Date
        taux = x.Taux
        devise=entreprise.Devise
        if x.Devise==devise:
            prix=x.Montant
        else:
            if devise=="USD":
                prix=round(x.Montant/taux, 2)
            else:
                prix=round(x.Montant*taux, 2) 
                pass
        dictionnaire['montant']=prix
        dictionnaire['devise']=devise
        compte=x.Compte
        if compte==None:
            mode=x.Mode
        else:
            mode=compte.Compte.Type
            pass
        dictionnaire['mode']=mode
        dictionnaire['statut']=x.Statut
        dictionnaire['solde']=x.Solde
        dictionnaire['operateur']=x.Operateur.Username
        liste_paiement.append(dictionnaire)
        num+=1
        pass
    return liste_paiement


def detail_commande(request):
    try:
        com=request.GET['com']
        usr=request.GET['usr']
        code=request.GET['code']
    except:
        return render(request, 'page-login.html')
    else:
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            commande=Facture.objects.get(Uuid=code)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                maj = Facture.objects.filter(Entreprise=entreprise).order_by('-Date')[:1]
                if maj.exists():
                    dernier_maj=maj[0]
                    date_maj=dernier_maj.Date
                else:
                    date_maj='00/00/0000'
                    pass
                profil_com = 'media/'+str(entreprise.Logo)
                profil_user = 'media/'+str(user.Profil)
                super_admin = str(user.SuperAdmin)
                client=commande.Client
                acteur=one_actor(client, entreprise)
                compte = CompteClient.objects.filter(Client=client)
                profil_client = 'media/'+str(client.Profil)
                items=ItemFacture.objects.filter(Facture=commande)
                facture=one_facture(commande, entreprise)
                lien_facture='media/{}.pdf'.format(commande.Uuid)
                items_liste = liste_items(items, entreprise)
                comments = Commentaire.objects.filter(Facture=commande)
                paiement=liste_paiement(commande, entreprise)
                clients = data_client(entreprise)
                articles=data_article(entreprise)
                return render(request, 'details_commande.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'entreprise': entreprise, 'client': acteur, 'items': items_liste, 'profil_client': profil_client, 'comments': comments, 'code': code, 'compte': compte, 'lien_facture': lien_facture, 'montant': commande.Montant, 'facture': facture, 'maj': date_maj, 'paiement': paiement, 'clients': clients, 'articles': articles})


def envoyer_mail(request):
    if request.method=='POST':
        com=request.POST['com']
        usr=request.POST['usr']
    else:
        com=request.GET['com']
        usr=request.GET['usr']
    try:
        user=Operateur.objects.get(Uuid=usr)
        entreprise=Entreprise.objects.get(Uuid=com)
    except:
        return render(request, 'page-login.html', {'message': ''})
    else:
        entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
        if entreprise != entreprise_user:
            return render(request, 'page-login.html', {'message': ''})
        else:
            if request.method=='POST':
                file=request.POST['file']
                client=request.POST['destination']
                facture=Facture.objects.get(Uuid=file)
                client=facture.Client
                destination=client.Email
                message="""
                Mr(Mme) {}, 

                Bonjour ou bonsoir, cela dépend de l'heure à laquelle vous lirez ce mail, en espérant qu'il vous trouve bien portant.

                Ci-joint, tous les détails de la facture N°{} valable depuis le {}, émise à votre égard. Veuillez donc à cet effet, prendre connaissance de toutes les informations relatives à cette dernière.

                Cordialement, {}.""".format(client.Designation, facture.RN, facture.Date, entreprise.Designation)
            else:
                try:
                    file=request.GET['file']
                except:
                    file=''
                    pass
                try:
                    id_acteur=request.GET['destination']
                    client=Acteur.objects.get(Uuid=id_acteur)
                    destination=client.Email
                    message="""
                    Mr(Mme) {}, 

                    Bonjour ou bonsoir, cela dépend de l'heure à laquelle vous lirez ce mail, en espérant qu'il vous trouve bien portant.

                    Cordialement, {}.""".format(client.Designation, entreprise.Designation)
                except:
                    destination=''
                    message=''
                    pass
            acteurs=Acteur.objects.filter(Entreprise=entreprise)
            utilisateurs=Operateur.objects.filter(Entreprise=entreprise)
            profil_com = 'media/'+str(entreprise.Logo)
            profil_user = 'media/'+str(user.Profil)
            super_admin = str(user.SuperAdmin)
            return render(request, 'email.html', {'usr': usr, 'com': com, 'username': user.Username, 'profil_user': profil_user, 'super_admin': super_admin, 'profil_com': profil_com, 'acteurs': acteurs, 'utilisateurs': utilisateurs, 'destination': destination, 'message': message, 'file': file})


def mail_envoye(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                destination=request.POST['destination']
                message=request.POST['message']
                cc=request.POST['cc']
                liste_destinataire=[destination]
                if not cc=='':
                    liste_destinataire.append(cc)
                    pass
                try:
                   facture=request.POST['facture']
                   file='sfe_facturation/static/media/{}.pdf'.format(facture)
                except:
                    file=request.FILES['file']
                    pass 
                titre='Mail de {}'.format(entreprise.Email)
                email = EmailMessage(subject=titre, body=message, from_email=entreprise.Email, to=liste_destinataire)
                if not file=='':
                    email.attach_file(file)
                    pass 
                email.send()
                return redirect('/mails/?usr={}&com={}'.format(usr, com))
                pass


# Étape 1 : créer un PDF temporaire contenant le texte à ajouter
def create_overlay(data):
    c = canvas.Canvas("overlay.pdf", pagesize=letter)
    y_pos = PAGE_HEIGHT - 120
    c.setStrokeColor(data[0])
    c.setFillColor(colors.white) 
    c.rect(PAGE_WIDTH / 3.3, y_pos-40, 140, 50, fill=1)

    c.setFillColor('green')
    c.setFont("Courier-Bold", 8)
    c.drawCentredString(PAGE_WIDTH / 2.4, y_pos, "FACTURE {} AVEC".format(data[1]))
    c.drawCentredString(PAGE_WIDTH / 2.4, y_pos-10, "{} {} PAR {}".format(data[2], data[3], data[4]))
    c.drawCentredString(PAGE_WIDTH / 2.4, y_pos-20, "EN DATE DU {}".format(data[5]))
    c.drawCentredString(PAGE_WIDTH / 2.4, y_pos-30, "SOLDE RESTANT {} {}".format(data[6], data[3]))

    c.save()

# Étape 2 : fusionner le texte avec le PDF original
def add_text_to_pdf(input_pdf, output_pdf, data):
    create_overlay(data)

    # Ouvrir les PDF
    existing_pdf = PdfReader(open(input_pdf, "rb"))
    overlay_pdf = PdfReader(open("overlay.pdf", "rb"))
    writer = PdfWriter()

    page = existing_pdf.pages[0]  # première page
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

    # Ajouter les autres pages sans modification
    for page in existing_pdf.pages[1:]:
        writer.add_page(page)


    # Sauvegarder le résultat
    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)
    pass



def paiement(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                id_facture=request.POST['facture']
                montant=request.POST['montant']
                mode=request.POST['mode_paiement']
                devise=request.POST['devise']
                compte=request.POST['compte']
                facture=Facture.objects.get(Uuid=id_facture)
                if not compte=='':
                    liste_compte=CompteClient.objects.get(Uuid=compte)
                    compte_client=liste_compte
                else:
                    compte_client=None 
                    pass 
                try:
                    liste_taux = Taux.objects.all().order_by('-Date')[:1][0]
                except:
                    taux_facture=2263
                else:
                    taux_facture=liste_taux.Libelle
                    pass 
                caracteres = string.ascii_uppercase + string.digits
                key = ''.join(choices(caracteres, k=5))
                code_entreprise = ''.join([entreprise.Designation[0], entreprise.Designation[1], entreprise.Designation[2]])
                maintenant = datetime.now()
                date = maintenant.strftime("%d/%m/%Y")
                code = '/'.join([code_entreprise, 'REC', key, date])
                query = Paiement.objects.filter(Code=code)
                if query.exists():
                    key = ''.join(choices(caracteres, k=5))
                    code = '/'.join([code_entreprise, 'COM', key, date])
                    pass
                if devise==entreprise.Devise:
                    montant_paye=montant
                else:
                    if devise=="USD":
                        montant_paye=round(montant/taux, 2)
                    else:
                        montant_paye=round(montant*taux, 2) 
                        pass 
                paiement=Paiement.objects.filter(Facture=facture)
                accompte=0
                for x in paiement:
                    taux=x.Taux
                    devise=entreprise.Devise
                    if devise==x.Devise:
                        montant=x.Montant
                    else:
                        if devise=="USD":
                            montant=round(x.Montant/taux, 2)
                        else:
                            montant=round(x.Montant*taux, 2) 
                            pass 
                    accompte+=montant
                    pass
                paiements=int(accompte)+int(montant_paye)
                reste=facture.Montant-paiements
                if reste<=0:
                    motif="Solde"
                    statut="ACQUITTÉE"
                    color='red'
                else:
                    motif="Accompte"
                    statut="ACCOMPTÉE"
                    color='green'
                    pass
                maintenant = datetime.now()
                date = maintenant.strftime("%d/%m/%Y")
                Paiement.objects.create(Facture=facture, Code=code, Mode=mode, Devise=devise, Taux=taux_facture, Montant=montant_paye, Compte=compte_client, Statut=motif, Solde=reste, Operateur=user)
                element=Paiement.objects.filter(Facture=facture, Code=code, Mode=mode, Devise=devise, Taux=taux_facture, Montant=montant_paye, Compte=compte_client, Statut=motif, Solde=reste, Operateur=user)[:1][0]
                Action.objects.create(Element=element.Code, Table="Paiement", Type="Ajout", Operateur=user, Entreprise=entreprise)
                data=[color, statut, str(montant_paye), devise, mode, date, reste]
                add_text_to_pdf("sfe_facturation/static/media/{}.pdf".format(facture.Uuid), "sfe_facturation/static/media/{}.pdf".format(element.Uuid), data)
                return redirect('/detail/?usr={}&com={}&code={}'.format(usr, com, facture.Uuid))


def delete_paiement(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        id_paiement=request.POST['paiement']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
            paiement=Paiement.objects.get(Uuid=id_paiement)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                facture=Facture.objects.filter(paiement=paiement)[:1][0]
                Action.objects.create(Element=paiement.Uuid, Table="Paiement", Type="Suppression", Obs="Facture N°{} / Montant : {} / Date : {}".format(facture.RN, paiement.Montant, paiement.Date), Operateur=user, Entreprise=entreprise)
                paiement.delete()
                return redirect('/detail/?usr={}&com={}&code={}'.format(usr, com, facture.Uuid))
                pass



def generate_invoice(style, facture, entreprise, client, data, taxe):
    c = canvas.Canvas("sfe_facturation/static/media/{}.pdf".format(facture[0]), pagesize=A4)
    margin = 20 * mm
    primary_color=style[0]
    filigrane=style[1]
    police=style[2]
    border=style[3]
    impaire=style[4]
    paire=style[5]
    compte_entreprise=style[6]
    compte_client=style[7]
    if not filigrane=='':
        c.drawImage("sfe_facturation/static/media/{}".format(filigrane), -5, PAGE_HEIGHT - 840, width=600, height=840)
        pass

    # En-tete
    c.setFont(police, 10)   
    c.drawImage(entreprise[0], MARGIN_X, PAGE_HEIGHT - 80, width=30, height=30)
    c.setFont("{}-Bold".format(police), 13)
    c.drawString(MARGIN_X + 40, PAGE_HEIGHT - 63, entreprise[1])
    c.setFont(police, 10)
    c.drawString(MARGIN_X + 40, PAGE_HEIGHT - 78, entreprise[2])
    c.setFont("{}-Bold".format(police), 20)
    c.setFillColor(primary_color)
    c.drawString(MARGIN_X, PAGE_HEIGHT - 93, "____")
    c.setFillColor("black")
    c.drawString(MARGIN_X+ 45, PAGE_HEIGHT - 93, "_________________________________")

    # Bloc client

    bloc_x = PAGE_WIDTH - 200
    bloc_y = PAGE_HEIGHT - 80

    c.setFillColor(primary_color)
    c.setFont("{}-Bold".format(police), 23)
    c.drawRightString(PAGE_WIDTH - 60, bloc_y + 2, "FACTURE")
    c.setFillColor("black")
    c.setFont(police, 10)
    c.drawRightString(PAGE_WIDTH - 60, bloc_y - 17, facture[1])

    c.setFont("{}-Bold".format(police), 11)
    c.drawRightString(PAGE_WIDTH - 60, bloc_y - 70, "N° : {}".format(facture[2]))
    c.setFont(police, 10)
    c.drawRightString(PAGE_WIDTH - 60, bloc_y - 90, facture[3])
    # ======================================================

    c.setFont(police, 10)
    c.drawString(MARGIN_X, PAGE_HEIGHT - 150, "Client")

    c.setFont("{}-Bold".format(police), 13)
    c.drawString(MARGIN_X, PAGE_HEIGHT - 170, client[0])

    c.setFont(police, 10)
    c.drawString(MARGIN_X, PAGE_HEIGHT - 185, client[1])
    c.drawString(MARGIN_X, PAGE_HEIGHT - 200, client[2])
    c.drawString(MARGIN_X, PAGE_HEIGHT - 215, client[3])

    # --- TABLE DES ARTICLES ---
    y_table = PAGE_HEIGHT - 245
    styles = getSampleStyleSheet()
    style_right = styles["Normal"]
    style_right.alignment = TA_RIGHT
    style_center = styles["Normal"]
    style_center.alignment = TA_CENTER

    table_data = [["Description", "Prix [HT]", "Qte", "Groupe", "Total [TTC]"]]
    for item in data:
        total =round(item['quantity'] * item['price'], 2)
        table_data.append([
            item['name'],
            str(item['originalPrice']),
            str(item['quantity']),
            item['taxGroup'],
            str(total)
        ])

    table = Table(table_data, colWidths=[PAGE_WIDTH/2.6, 70, 50, 60, 80])
    style= (TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), '{}-Bold'.format(police)),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), police),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(border)),
    ]))

    for i in range(1, len(table_data)):
        bg_color = colors.HexColor(paire) if i % 2 == 0 else colors.HexColor(impaire)
        style.add('BACKGROUND', (0, i), (-1, i), bg_color)
        pass


    table.setStyle(style)
    table.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
    table_height = len(table_data) * 20
    table.drawOn(c, margin, y_table - table_height)

    x = MARGIN_X
    y = y_table-table_height

    # ======================================================
    # TOTALS ET INFORMATIONS
    # ======================================================

    if y < 100:
        c.showPage()
        y=PAGE_HEIGHT - 30
        pass

    if not entreprise[7]=='' and compte_entreprise==True:
        c.rect(MARGIN_X, y-105, 190, 90)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN_X+10, y-25, "Facture payable en :")
        x=0
        for i in entreprise[7]:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(MARGIN_X+10, y-36, "{}. {}".format(i[0], i[1]))
            c.setFont("Helvetica", 7)
            c.drawString(MARGIN_X+10, y-45, "Opérateur : {}".format(i[2]))
            c.drawString(MARGIN_X+10, y-54, "Numero : {}".format(i[3]))
            c.drawString(MARGIN_X+10, y-63, "Nom : {}".format(i[4]))
            y-=36
            x+=1
            pass
        y -= 10*x
    else:
        y-=80
        pass

    if y < 10:
        c.showPage()
        y=PAGE_HEIGHT - 30
        pass

    c.setFont(police, 10)
    c.drawString(PAGE_WIDTH - 240, y + 45, "Total H.T.")
    c.drawRightString(PAGE_WIDTH - 60, y + 45, str(taxe[0]))
    c.drawString(PAGE_WIDTH - 240, y + 30, "Total TVA")
    c.drawRightString(PAGE_WIDTH - 60, y + 30, str(taxe[1]))

    y -= 60

    if y < 120:
        c.showPage()
        y=PAGE_HEIGHT - 30
        pass

    c.setFont("{}-Bold".format(police), 11)
    c.drawRightString(PAGE_WIDTH - 60, y-20, "Total [TTC] : {} {}".format(facture[4], round(taxe[2], 2)))
    c.setFont("{}-Bold".format(police), 15)
    c.drawRightString(PAGE_WIDTH - 60, y-30, "___________________________")

    c.setFont("{}-Bold".format(police), 11)
    c.drawRightString(PAGE_WIDTH - 60, y-50, entreprise[3])

    c.setFont(police, 10)
    c.drawRightString(PAGE_WIDTH - 60, y-65, "Opérateur")


    c.setFillColor(primary_color)
    c.rect(MARGIN_X, y-9, 190, 25, fill=True, stroke=False)

    c.setFillColor("white")
    c.setFont("{}-Bold".format(police), 10)
    c.drawString(MARGIN_X+10, y, "MODE DE PAIEMENT : {}".format(facture[5]))


    if not client[5]=='' and compte_client==True:
        c.setFillColor("black")
        c.rect(MARGIN_X, y-75, 190, 50)
        c.setFont("Helvetica", 7)
        c.drawString(MARGIN_X+10, y-40, "Opérateur : {}".format(client[4][0]))
        c.drawString(MARGIN_X+10, y-50, "Numero : {}".format(client[4][1]))
        c.drawString(MARGIN_X+10, y-60, "Nom : {}".format(client[4][1]))
        pass

    # ======================================================
    # CODE QR ET BAS DE PAGE
    # ======================================================
    y -= 120

    if y < 100:
        c.showPage()
        y=PAGE_HEIGHT - 30
        pass

    c.setFillColor("black")
    try:
        c.setFont("{}-Oblique".format(police), 9)
    except:
        c.setFont("{}-Italic".format(police), 9)
        pass
    c.drawString(MARGIN_X, y, "--- ÉLÉMENTS DE SÉCURITÉ DE LA FACTURE NORMALISÉE ---")

    qr_path = "sfe_facturation/static/media/{}.png".format(facture[0])
    try:
        c.drawImage(qr_path, MARGIN_X + 30, y - 90, width=70, height=70)
    except:
        pass

    c.rect(MARGIN_X, y - 100, 490, 90)
    c.setFont(police, 10)
    c.drawString(MARGIN_X + 250, y - 25, "Code DEF/DGI")
    c.setFont("{}-Bold".format(police), 10)
    c.drawString(MARGIN_X + 200, y - 35, facture[6])
    c.setFont(police, 10)
    c.drawString(MARGIN_X + 120, y - 50, "DEF NIM :")
    c.drawString(MARGIN_X + 120, y - 60, "DEF Compteurs")
    c.drawString(MARGIN_X + 120, y - 70, "DEF Heure :")

    c.setFont("{}-Bold".format(police), 9)
    c.drawRightString(PAGE_WIDTH - 60, y, "ISF : DGI-RDC-01")
    c.setFont("{}-Bold".format(police), 10)
    c.drawRightString(PAGE_WIDTH - 60, y - 50, facture[7])
    c.drawRightString(PAGE_WIDTH - 60, y - 60, facture[8])
    c.drawRightString(PAGE_WIDTH - 60, y - 70, facture[9])

    if y < 140:
        c.showPage()
        y=PAGE_HEIGHT - 10
        pass

    c.setFont("{}-Bold".format(police), 20)
    c.setFillColor(primary_color)
    c.drawString(MARGIN_X, y - 125, "____")
    c.drawString(MARGIN_X+445, y - 125, "____")
    c.setFillColor("black")
    c.drawString(MARGIN_X+ 45, y - 125, "_____________________________________")

    c.setFont(police, 7)
    c.drawCentredString(PAGE_WIDTH / 2, y - 140, "{} | {} | {}".format(entreprise[4], entreprise[5], entreprise[6]))

    c.showPage()
    c.save()


def nouvelle_facture(request):
    if request.method=='GET':
        return render(request, 'page-login.html')
    else:
        com=request.POST['com']
        usr=request.POST['usr']
        try:
            user=Operateur.objects.get(Uuid=usr)
            entreprise=Entreprise.objects.get(Uuid=com)
        except:
            return render(request, 'page-login.html', {'message': ''})
        else:
            entreprise_user=Entreprise.objects.filter(operateur=user)[:1][0]
            if entreprise != entreprise_user:
                return render(request, 'page-login.html', {'message': ''})
            else:
                comment = request.POST['comment']
                type_facture=request.POST['type_facture']
                mode=request.POST['mode']
                try:
                    facture_type=TypeFacture.objects.filter(Code=type_facture)[:1][0]
                except:
                    facture_type=None
                    code_type='FV'
                    lib_type='DE VENTE'
                else:
                    code_type=type_facture
                    lib_type=facture_type.Libelle
                    pass
                nature=request.POST['nature']
                reference=request.POST['reference']
                data = json.loads(request.POST.get("jsonData"))
                items=data['items']
                id_client = data['client']['uuid']
                client=Acteur.objects.get(Uuid=id_client)
                compte=CompteClient.objects.filter(Client=client).order_by('-Date')[:1]
                if compte.exists():
                    mode_paiement=compte[0].Compte.Type
                    compte_client=compte[0]
                    description=[compte_client.Compte.Operateur, compte_client.Compte.Numero, compte_client.Compte.Nom]
                else:
                    mode_paiement='ESPECES'
                    compte_client=None
                    description=''
                    pass
                caracteres = string.ascii_uppercase + string.digits
                key = ''.join(choices(caracteres, k=5))
                code_entreprise = ''.join([entreprise.Designation[0], entreprise.Designation[1], entreprise.Designation[2]])
                maintenant = datetime.now()
                date = maintenant.strftime("%d/%m/%Y")
                code_rn = '/'.join([code_entreprise, 'REF', key, date])
                query = Facture.objects.filter(RN=code_rn)
                if query.exists():
                    key = ''.join(choices(caracteres, k=5))
                    code_rn = '/'.join([code_entreprise, 'REF', key, date])
                    pass
                items_data=[]
                total_tva=0
                for i in items:
                    article=Article.objects.get(Uuid=i['article'])
                    if article.Taxe_specifique==None:
                        valeur="0%"
                        montant=0
                    else:
                        valeur=str(article.Taxe_specifique.Taux)+"%"
                        montant=article.Prix*article.Taxe_specifique.Taux/100
                        pass
                    if mode=='ht':
                        prixttc=article.Prix
                    else:
                        prixttc=article.Prix + (article.Prix*article.Groupe.Taux/100)
                        pass
                    dictionnaire=dict()
                    dictionnaire['code']=str(i['article'])
                    dictionnaire['name']=article.Designation
                    dictionnaire['type']=article.Type
                    dictionnaire['price']=prixttc
                    dictionnaire['quantity']=i['qty']
                    dictionnaire['taxGroup']=article.Groupe.Code
                    dictionnaire["taxSpecificValue"]=valeur
                    dictionnaire["taxSpecificAmount"]=montant
                    dictionnaire["originalPrice"]=article.Prix
                    dictionnaire["priceModification"]="Aucune remise"
                    items_data.append(dictionnaire)
                    tva=prixttc-article.Prix
                    total_tva+=tva
                    pass                
                url = "https://developper.dgirdc.cd/edef/api/invoice"
                headers = {
                    "Authorization": user.PointVente.Key,
                    "Accept": "text/plain",
                    "Content-Type": "application/json-patch+json",
                }
                payload = {
                "nif": entreprise.Nif,
                "rn": code_rn,
                "mode": mode,
                "isf": 'ABD-DEF-01',
                "type": code_type,
                "items": items_data,
                "client": {
                    "nif": client.Nif,
                    "type": client.Type.Code,
                    "typeDesc": client.Type.Libelle,
                    "name": client.Designation,
                    "contact": client.Telephone,
                    "address": client.Adresse,
                },
                "operator": {"id": str(user.Uuid), "name": user.Username},
                "payment": [
                    {"name": mode_paiement, "amount": data['totalTTC'], "curCode": data['devise'], "curRate": 1}
                ],
                "reference": "",
                "referenceType": "",
                "referenceDesc": "",
                "cmta": comment,
                "cmtb": "",
                "cmtc": "",
                "cmtd": "",
                "cmte": "",
                "cmtf": "",
                "cmtg": "",
                "cmth": "",
                "curCode": data['devise'],
                "curDate": str(datetime.now()),
                "curRate": 1,
                }
                try:
                    # Envoi de la requête POST
                    response = requests.post(url, headers=headers, json=payload)
                except:
                    titre="La connexion avec la DGI a échoué"
                    message="Veuillez vérifier votre connexion internet ou contactez le service client de VINX en cas de persistance."
                    return redirect("/facturation/?usr={}&com={}&message={}&titre={}".format(user.Uuid, entreprise.Uuid, message, titre))
                else:
                    # Analyse de la réponse
                    reponse_dgi = response.json()
                    print(reponse_dgi)
                    try:
                        code_uuid=reponse_dgi['uid']
                        url = "https://developper.dgirdc.cd/edef/api/invoice/{}/confirm".format(code_uuid)
                        headers = {
                            "Authorization": user.PointVente.Key,
                            "Accept": "text/plain",
                            "Content-Type": "application/json-patch+json",
                        }
                        payload = {
                            'total': reponse_dgi['curTotal'],
                            'vtotal': reponse_dgi['vtotal'],
                        }
                        total_facture=reponse_dgi['curTotal']
                        total_tva=reponse_dgi['vtotal']
                        response = requests.put(url, headers=headers, json=payload)
                        reponse_dgi = response.json()
                        try:
                            img = qrcode.make(reponse_dgi['qrCode'])
                            img.save('sfe_facturation/static/media/{}.png'.format(code_uuid))
                            Facture.objects.create(Uuid=code_uuid, RN=code_rn, Montant=total_facture, Type=facture_type, NatureAvoir=nature, ReferenceAvoir=reference, ModePaiement=mode_paiement, Devise=data['devise'], ModeFacture=mode, Compte=compte_client, Operateur=user, Entreprise=entreprise, Client=client)
                            element=Facture.objects.filter(Uuid=code_uuid, RN=code_rn, Montant=total_facture, Type=facture_type, NatureAvoir=nature, ReferenceAvoir=reference, ModePaiement=mode_paiement, Devise=data['devise'], ModeFacture=mode, Compte=compte_client, Operateur=user, Entreprise=entreprise, Client=client)[:1][0]
                            Action.objects.create(Element=code_rn, Table="Facture", Type="Ajout", Operateur=user, Entreprise=entreprise)  
                            DataDgi.objects.create(Facture=element, codeDEFDGI=reponse_dgi['codeDEFDGI'], nim=reponse_dgi['nim'], counters=reponse_dgi['counters'], dateTime=reponse_dgi['dateTime'], qrcode=reponse_dgi['qrCode'])
                            for i in data['items']:
                                article=Article.objects.get(Uuid=i['article'])
                                ItemFacture.objects.create(Facture=element, Article=article, Montant=i['lineTotalTTC'], Quantite=i['qty'])
                                Action.objects.create(Element=article.Designation, Table="Item Facture", Type="Ajout", Obs="Facture N°{}".format(code_rn), Operateur=user, Entreprise=entreprise)
                                pass
                            if not comment=="":
                                Commentaire.objects.create(Facture=element, Texte=comment)
                                Action.objects.create(Element=comment, Table="Commentaire", Type="Ajout", Operateur=user, Entreprise=entreprise)
                                pass
                            style_facture=StyleFacture.objects.filter(Entreprise=entreprise)[:1]
                            if style_facture.exists():
                                style=style_facture[0]
                                primaire=style.Primary_color
                                filigrane=style.Filigrane
                                police=style.Police
                                border=style.Border_color
                                impaire=style.Premiere_ligne
                                paire=style.Deuxieme_ligne
                                affichage_compte_client=style.CompteClient
                                affichage_compte_entreprise=style.CompteEntreprise
                            else:
                                primaire='orange'
                                filigrane=''
                                police='Helvetica'
                                border='#808080'
                                impaire='#E3F2FD'
                                paire='#F5F5F5'
                                affichage_compte_client=True
                                affichage_compte_entreprise=True
                                pass
                            facture_style=[primaire, filigrane, police, border, impaire, paire, affichage_compte_entreprise, affichage_compte_client]
                            taxe=[total_facture-total_tva, total_tva, total_facture]
                            compte_entreprise=CompteEntreprise.objects.filter(Entreprise=entreprise)[:2]
                            if compte_entreprise.exists():
                                entreprise_compte=[]
                                num=1
                                for i in compte_entreprise:
                                    liste_compte=[]
                                    mode=i.Compte.Type
                                    operateur=i.Compte.Operateur
                                    numero=i.Compte.Numero
                                    nom=i.Compte.Nom
                                    liste_compte.extend([num, mode, operateur, numero, nom])
                                    entreprise_compte.append(liste_compte)
                                    num+=1
                                    pass
                            else:
                                entreprise_compte=''
                                pass
                            data_facture=[]
                            maintenant = datetime.now()
                            data_facture.extend([code_uuid, lib_type, code_rn, str(element.Date), data['devise'], mode_paiement, reponse_dgi['codeDEFDGI'], reponse_dgi['nim'], reponse_dgi['counters'], reponse_dgi['dateTime']])
                            data_entreprise=[]
                            profil_com='sfe_facturation/static/media/'+str(entreprise.Logo)
                            data_entreprise.extend([profil_com, entreprise.Designation, entreprise.Activité, user.Username, entreprise.Email, entreprise.Telephone, entreprise.Adresse, entreprise_compte])
                            data_client=[]
                            data_client.extend([client.Designation, client.Telephone, client.Email, client.Adresse, mode_paiement, description])
                            generate_invoice(facture_style, data_facture, data_entreprise, data_client, items_data, taxe)       
                            return redirect("/detail/?usr={}&com={}&code={}".format(user.Uuid, entreprise.Uuid, code_uuid))
                        except:
                            titre="Erreur de transmission N°{}".format(str(reponse_dgi['errorCode']))
                            message="{}. Contactez le service client de VINX en cas de persistance.".format(str(reponse_dgi['errorDesc']))
                            return redirect("/facturation/?usr={}&com={}&message={}&titre={}".format(user.Uuid, entreprise.Uuid, message, titre))
                        pass
                    except:
                        titre="Erreur de transmission N°{}".format(str(reponse_dgi['errorCode']))
                        message="{}. Contactez le service client de VINX en cas de persistance.".format(str(reponse_dgi['errorDesc']))
                        return redirect("/facturation/?usr={}&com={}&message={}&titre={}".format(user.Uuid, entreprise.Uuid, message, titre))