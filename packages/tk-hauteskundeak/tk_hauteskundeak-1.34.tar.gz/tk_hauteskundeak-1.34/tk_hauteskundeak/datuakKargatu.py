import csv
from django.core.management.base import BaseCommand, CommandError
from tk_hauteskundeak.models import *
from django.template.defaultfilters import slugify
from .models import *
from photologue.models import Photo
import datetime
import xlrd
import glob, os
from os import walk

def datuak_jaso(url):
    izena = url[:-4]
    mota = izena[:-4]
    urtea = izena[-4:]
    urteBerezia = izena[-6:]

    if mota == "aldundiak":
        slug = "batzar-nagusietako-hauteskundeak-{}".format(urtea)
        titulua = "Batzar nagusietako hauteskundeak {}".format(urtea)
        mota = HauteskundeMota.objects.get(slug="batzar-nagusietarako-hauteskundeak")
    elif mota == "udalak":
        slug = "udal-hauteskundeak-{}".format(urtea)
        titulua = "Udal hauteskundeak {}".format(urtea)
        mota = HauteskundeMota.objects.get(slug="udal-hauteskundeak")
    elif mota == "legebiltzarra":
        slug = "eusko-legebiltzarrerako-hauteskundeak-{}".format(urtea)
        titulua = "Eusko Legebiltzarrerako hauteskundeak {}".format(urtea)
        mota = HauteskundeMota.objects.get(slug="eusko-legebiltzarrerako-hauteskundeak")
    elif mota == "europa":
        slug = "europako-parlamentuko-hauteskundeak-{}".format(urtea)
        titulua = "Europako Parlamentuko hauteskundeak {}".format(urtea)
        mota = HauteskundeMota.objects.get(slug="europako-parlamentuko-hauteskundeak")
    elif url=="espainia-012019.csv" or url=="espainia-022019.csv":
        slug = "espainiako-kongresuko-hauteskundeak-{}".format(urteBerezia)
        titulua = "Espainiako kongresuko hauteskundeak {}".format(urteBerezia)
        mota = HauteskundeMota.objects.get(slug="espainiako-kongresuko-hauteskundeak")
    else:
        slug = "espainiako-kongresuko-hauteskundeak-{}".format(urtea)
        titulua = "Espainiako kongresuko hauteskundeak {}".format(urtea)
        mota = HauteskundeMota.objects.get(slug="espainiako-kongresuko-hauteskundeak")
    
    datuak = {"slug":slug, "titulua":titulua, "mota":mota, "urtea":urtea}
    return datuak

def datuak_inportatu(filenames=None):
    if not filenames:
        filenames = next(walk("src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/"), (None, None, []))[2]
    
    for haut in filenames:
        herriak_gorde(haut)
        alderdiak_gorde(haut)
        hauteskundeak_sortu(haut)
        hauteskundea_tokian_sortu(haut)
        hauteskundeak_emaitza_tokian_sortu(haut)


def herriak_gorde(url):
    with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url)) as f:
        
        DictReader_obj = csv.DictReader(f)
        for item in DictReader_obj:
            if not Tokia.objects.filter(slug=slugify(item['Ámbito'])).exists():
                herria, created = Tokia.objects.get_or_create(slug=slugify(item['Ámbito']), izena=item['Ámbito'])
    
                if created:
                    herria.is_public = True
                    if item['Cod Municipio'] != "":
                        herria.herri_kodea = item['Cod Municipio']
                    herria.lurralde_kodea = item['Cod Comarca']
                    herria.save()
        print("Herriak gordeta")


def alderdiak_gorde(url):
    with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url),'r') as f:
        DictReader_obj = csv.DictReader(f)
        headers = DictReader_obj.fieldnames[12:]
        for item in headers:
            if not Alderdia.objects.filter(izena=item).exists():
                alderdia, created = Alderdia.objects.get_or_create(slug=slugify(item), izena=item, akronimoa = item[:29])
        print("Alderdiak gordeta")
            

def hauteskundeak_sortu(url):
    datuak = datuak_jaso(url)
    d = datetime.date(int(datuak.get("urtea")), 1, 1)
    if not Hauteskundea.objects.filter(slug=datuak.get("slug")).exists():
        hauteskundea, created = Hauteskundea.objects.get_or_create(slug=datuak.get("slug"), eguna = d,mota = datuak.get("mota"))
        if created:
            hauteskundea.izena = datuak.get("titulua")
            hauteskundea.get_urtea()
            hauteskundea.is_public = True
            hauteskundea.save()
    print("Hauteskundea sortuta")


def hauteskundea_tokian_sortu(url):
    with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url),'r') as f:
        DictReader_obj = csv.DictReader(f)
        datuak = datuak_jaso(url)
        for item in DictReader_obj:
            h_tokian, created = HauteskundeaTokian.objects.get_or_create(hauteskundea = Hauteskundea.objects.filter(slug=datuak.get("slug")).first(), tokia = Tokia.objects.filter(slug=slugify(item['Ámbito'])).first())
            if created:
                if item["Censo"] != "":
                    h_tokian.errolda = item["Censo"]
                if item["Votantes"] != "":
                    h_tokian.boto_emaileak = item["Votantes"]
                if item["Nulos"] != "":
                    h_tokian.baliogabeak = item["Nulos"]
                if item["Blancos"] != "":
                    h_tokian.zuriak = item["Blancos"]
                if item["Votos Candidatura"] != "":
                    h_tokian.alderdien_botoak = item["Votos Candidatura"]
                h_tokian.save()

def hauteskundeak_emaitza_tokian_sortu(url):
     with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url),'r') as f:
        DictReader_obj = csv.DictReader(f)
        headers = DictReader_obj.fieldnames[12:]
        datuak = datuak_jaso(url)
        for item in DictReader_obj:
            for alderdi in headers:
                print(Hauteskundea.objects.get(slug=datuak.get("slug")).slug, item['Ámbito'], item[alderdi], alderdi)
                if item[alderdi] and item[alderdi] != 0 and item[alderdi] != "0":
                    hauteskundeatokian = HauteskundeaTokian.objects.get(hauteskundea=Hauteskundea.objects.get(slug=datuak.get("slug")), tokia=Tokia.objects.filter(slug=slugify(item['Ámbito'])).first())
                    hetokian, created = HauteskundeEmaitzakTokian.objects.get_or_create(hauteskundeatokian=hauteskundeatokian, alderdia=Alderdia.objects.filter(izena=alderdi).first())
                    if created:
                        hetokian.botoak = item[alderdi] 
                        hetokian.save()



def hauteskundea_tokian_sortu_herria(url, ambito):
    with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url),'r') as f:
        DictReader_obj = csv.DictReader(f)
        datuak = datuak_jaso(url)
        for item in DictReader_obj:
            if item['Ámbito'] == ambito:
                h_tokian, created = HauteskundeaTokian.objects.get_or_create(hauteskundea = Hauteskundea.objects.filter(slug=datuak.get("slug")).first(), tokia = Tokia.objects.filter(slug=slugify(item['Ámbito'])).first())
                if created:
                    if item["Censo"] != "":
                        h_tokian.errolda = item["Censo"]
                    if item["Votantes"] != "":
                        h_tokian.boto_emaileak = item["Votantes"]
                    if item["Nulos"] != "":
                        h_tokian.baliogabeak = item["Nulos"]
                    if item["Blancos"] != "":
                        h_tokian.zuriak = item["Blancos"]
                    if item["Votos Candidatura"] != "":
                        h_tokian.alderdien_botoak = item["Votos Candidatura"]
                    h_tokian.save()



def hauteskundeak_emaitza_tokian_sortu_herria(url, ambito):
     with open('src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/{}'.format(url),'r') as f:
        DictReader_obj = csv.DictReader(f)
        headers = DictReader_obj.fieldnames[12:]
        datuak = datuak_jaso(url)
        for item in DictReader_obj:
            if ambito == item['Ámbito']:
                for alderdi in headers:
                    print(Hauteskundea.objects.get(slug=datuak.get("slug")).slug, item['Ámbito'], item[alderdi], alderdi)
                    if item[alderdi] and item[alderdi] != 0 and item[alderdi] != "0":
                        hauteskundeatokian = HauteskundeaTokian.objects.get(hauteskundea=Hauteskundea.objects.get(slug=datuak.get("slug")), tokia=Tokia.objects.filter(slug=slugify(item['Ámbito'])).first())
                        hetokian, created = HauteskundeEmaitzakTokian.objects.get_or_create(hauteskundeatokian=hauteskundeatokian, alderdia=Alderdia.objects.filter(izena=alderdi).first())
                        if created:
                            hetokian.botoak = item[alderdi] 
                            hetokian.save()


def datuak_inportatu_herria(herria):
    filenames = next(walk("src/tk_hauteskundeak/tk_hauteskundeak/hauteskunde-emaitzak/"), (None, None, []))[2]
    
    for haut in filenames:
        hauteskundeak_sortu(haut)
        alderdiak_gorde(haut)
        hauteskundea_tokian_sortu_herria(haut, herria)
        hauteskundeak_emaitza_tokian_sortu_herria(haut, herria)



# Denak inportatzeko
# from tk_hauteskundeak.datuakKargatu import *; datuak_inportatu()
# Aukeratuak -inportatzeko
# from tk_hauteskundeak.datuakKargatu import *; datuak_inportatu(["udalak2019.csv"])

#Herri jakin bateko denak ekartzeko
# from tk_hauteskundeak.datuakKargatu import *; datuak_inportatu_herria("AYALA/AIARA")