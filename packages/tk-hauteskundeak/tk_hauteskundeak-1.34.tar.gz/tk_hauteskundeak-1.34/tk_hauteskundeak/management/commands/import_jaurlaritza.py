# -*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand, CommandError
from tk_hauteskundeak.models import *
from tk_hauteskundeak.views import sortu_eskualdeko_datuak
from django.template.defaultfilters import slugify
from photologue.models import Photo
from datetime import datetime
import requests 
import xmltodict


# http://www.euskadi.eus/informazioa/hauteskundeetako-emaitzen-fitxategien-deskargak/web01-a2haukon/eu/
# http://www.infoelectoral.mir.es/infoelectoral/min/areaDescarga.html?method=inicio
#Mun dakenak hartu behar dira
import glob, os

URLA = 'https://komunikabideak.euskalhauteskundeak.eus/files/Resultados.xml'
#URLA='http://localhost:8000/static/Resultados.xml'


#Identifikatzailea: u098@euskalhauteskundeak.net
#Gakoa: !Ae!Pk71
#Telefono zk.: 900 840 071 (uuztailak 6tik 11ra 8etatik 20:00etara)
#cau-elecciones

"""
from requests.auth import HTTPBasicAuth
requests.get(URLA, auth=HTTPBasicAuth('u098@euskalhauteskundeak.net', '!Ae!Pk71'))
"""
from django.conf import settings




def get_alderdia(izena):
    try:
        return Alderdia.objects.get(import_kodea=izena)
    except:
        return None
    print izena
    ald = Alderdia.objects.filter(izena__icontains=izena.lower())
    if ald:
        return ald.first()
    ald, created = Alderdia.objects.get_or_create(izena=izena.lower())
    return ald
    

def get_xml_data():
    
    if getattr(settings, 'HAUTESKUDEAK_TEST', False):
        XML_URLA='https://uztarria.eus/static/HH17-45.xml'
    else:    
        XML_URLA = 'https://bots-medios.euskadielecciones.eus/files/Resultados.xml'
    
    return requests.get(XML_URLA, auth=('u098@euskalhauteskundeak.net', '!Ae!Pk71'))

def int_please(data):
    if '-' in str(data):
        return 0
    elif ',' in str(data):
        return data.replace(',','.')
    try:
        return int(data)
    except:
        return 0

def import_xml():
    hauteskundeaq = Hauteskundea.objects.filter(auto_import=True).order_by('-id')
    if hauteskundeaq:
        hauteskundea=hauteskundeaq.first()
        xmla = get_xml_data().content
        di = xmltodict.parse(xmla, process_namespaces=True)
        datuak_dict = di['SalidaDatos']['SalidaXML']        
        
        for lekua in datuak_dict:
            ambito = lekua['AMBITO']
            print ambito
            lurralde_kodea = int(ambito[0:2])
            herri_kodea = int(ambito[2:])
            tokia = Tokia.objects.filter(lurralde_kodea = lurralde_kodea, herri_kodea=herri_kodea)
            print tokia
            if tokia:
                tokia=tokia.first()
                hauteskundea_tokian, created = HauteskundeaTokian.objects.get_or_create(tokia=tokia, hauteskundea=hauteskundea)
                
                hauteskundea_tokian.errolda = int_please(lekua['CENSO'])
                hauteskundea_tokian.eskrutinioa = int_please(lekua['PESCRU'])
                hauteskundea_tokian.baliogabeak = int_please(lekua['NNULOS'])
                hauteskundea_tokian.boto_emaileak = int_please(lekua['NVOTOS'])
                hauteskundea_tokian.zuriak = int_please(lekua['NBLANCOS'])
                hauteskundea_tokian.save()

                for alderdia in lekua['PARTIDO']:
                    tk_alderdia = get_alderdia(alderdia['SIGLAS'])
                    if tk_alderdia:
                        emaitza_tokian, created = HauteskundeEmaitzakTokian.objects.get_or_create(hauteskundeatokian=hauteskundea_tokian,
                                                                                        alderdia=tk_alderdia)
                        emaitza_tokian.botoak=int_please(alderdia['VOTOS'])
                        #emaitza_tokian.botoak=int_please(alderdia[u'ESCA\xd1OS'])
                        emaitza_tokian.save()
                        
                hauteskundea_tokian.save()
                for em in HauteskundeEmaitzakTokian.objects.filter(hauteskundeatokian=hauteskundea_tokian):
                    #EHUNEKOAK GORDETZEKO
                    em.save()
                hauteskundea_tokian.save()    
                    
                        
        sortu_eskualdeko_datuak(hauteskundea)

class Command(BaseCommand):
    args = 'Irekiako datuak import'
    help = 'Irekiako csvak irakurtzeko'


    def handle(self, *args, **options):
        import_xml()
