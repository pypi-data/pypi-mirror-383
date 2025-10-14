# -*- coding: utf-8 -*-

import csv
from django.core.management.base import BaseCommand, CommandError
from tk_hauteskundeak.models import *
from django.template.defaultfilters import slugify
from photologue.models import Photo
from datetime import datetime

# http://www.euskadi.eus/informazioa/hauteskundeetako-emaitzen-fitxategien-deskargak/web01-a2haukon/eu/
# http://www.infoelectoral.mir.es/infoelectoral/min/areaDescarga.html?method=inicio
#Mun dakenak hartu behar dira
import glob, os

hauteskunda_mota = {"02":"kongresua","03":"senatua","04":"udal hauteskundeak","07":"Europakoak","pa":"Eusko Jaurlaritza","na":"Nafarroako parlamentua","ju":"Junta orokorrak"}

lurraldeak =[48,20,1,31]
# 1 - Araba
# 20 Gipuzkoa
# 48 Bizkaia
# 31 Nafarroa

giltzak_esp={u'herria':u'Nombre de Municipio',u'censo':u'Total censo electoral',u'votantes':u'Total votantes',u'Válidos':u'Votos válidos',u'votos_candidaturas':u'Votos a candidaturas',u'blancos':u'Votos en blanco',u'nulos':u'Votos nulos'}

giltzak_ej={u'herria':u'Ámbito',u'censo':u'Censo',u'votantes':u'Votantes',u'Válidos':u'Votos válidos',u'votos_candidaturas':u'Votos Candidatura',u'blancos':u'Blancos',u'nulos':u'Nulos'}
giltzak_ej2={u'herria':u'AMBITO',u'censo':u'Censo',u'votantes':u'Votantes',u'Válidos':u'Votos válidos',u'votos_candidaturas':u'Votos Candidatura',u'blancos':u'Blancos',u'nulos':u'Nulos'}


giltzak_naf={u'herria':u'MUNICIPIO',u'censo':u'CENSO',u'votantes':u'VOTOS',u'Válidos':u'VALIDOS',u'votos_candidaturas':u'A_CANDID',u'blancos':u'BLANCOS',u'nulos':u'NULOS'}
giltzak_naf2={u'herria':u'Municipio',u'censo':u'Censo',u'votantes':u'Participación',u'Válidos':u'Válidos',u'votos_candidaturas':u'A_CANDID',u'blancos':u'Blancos',u'nulos':u'Nulos'}

giltzak_naf3={u'herria':u'Municipio',u'censo':u'Censo_total',u'votantes':u'Votos_totales',u'Válidos':u'Votos_Validos',u'votos_candidaturas':u'Votos_Candidaturas',u'blancos':u'Votos_blancos',u'nulos':u'Votos_nulos'}


ej_lurraldeak ={'Bizkaia':48, 'Araba-Alava':1,'Gipuzkoa':20}


def reencode(file):
    for line in file:
        yield line.decode('ISO-8859-1').encode('utf-8')

def csvak_irakurri():
    """
    Hauteskundea.objects.all().delete()
    HauteskundeMota.objects.all().delete()
    Alderdia.objects.all().delete()
    HauteskundeaTokian.objects.all().delete()
    Tokia.objects.all().delete()

    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/ESP")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_esp)

    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/NAFARROA")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_naf, 31, delimiter=';',encoding='iso-8859-1')

    Hauteskundea.objects.filter(id__in=[433,434]).delete()
    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/NAF2")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_naf2, 31, delimiter=';',encoding='iso-8859-1')


    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/EAE")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_ej, None, delimiter=';',encoding='iso-8859-1')


    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/JUN")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_ej2, None, delimiter=',',encoding='iso-8859-1')


    # ERROREA EMAN ZUTEN NAFARROAKO BIAK
    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/NAF3")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_naf3, 31, delimiter=';',encoding='utf-8')
    """
    os.chdir("/var/csmant/django/tokikom/maxixatzen/hauteskundeak/NAF4")
    for file in glob.glob("*.csv"):
        print file
        import_csv(file, giltzak_naf, 31, delimiter=';',encoding='utf-8')



def import_csv(file, giltzak, h_kodea=None, delimiter=',', encoding='utf-8'):
    if file:
        mota, created = HauteskundeMota.objects.get_or_create(izena=hauteskunda_mota[file[0:2]])
        if file[0:2] in ["pa","na","ju"]:
            eguna = "%s-01-01" % (file.split('.')[0][-4:])
        else:
            eguna = "%s-%s-01" % (file[3:7],file[7:9])
        izena = "%s - %s"% (eguna, hauteskunda_mota[file[0:2]])

        hauteskundea, created = Hauteskundea.objects.get_or_create(izena=izena, eguna=eguna,mota=mota)

        with open(file, 'r') as fh:
            rd = csv.DictReader(fh, delimiter=delimiter)
            for row1 in rd:
                hautesk = HauteskundeaTokian()
                print encoding
                #print '--------------------------------------------'
                try:
                    row = {unicode(k,encoding).strip():unicode(v or '',encoding).strip() or 0 for k, v in row1.iteritems()}
                except:
                    #import pdb; pdb.set_trace()
                    pass
                try:
                    eremua = row.pop(giltzak['herria'])
                except:
                    if 'MUNICIPIO' in row.keys():
                        eremua = row.pop('MUNICIPIO')
                        # nafarroako excelean aldakorrak dira maiuskulak eta minuskulak
                    else:
                        #import pdb; pdb.set_trace()
                        pass
                if h_kodea:
                    herrialde_kodea=h_kodea
                elif row.has_key('TH'):
                    herrialde_kodea = ej_lurraldeak.get(row.pop('TH',None),1)
                else:
                    herrialde_kodea = row.pop(u'Código de Provincia',None)
                if not herrialde_kodea:
                    #import pdb; pdb.set_trace()
                    pass
                tokia = None

                if int(herrialde_kodea or 0) in lurraldeak:
                    try:
                        tokia, created = Tokia.objects.get_or_create(izena=eremua)
                    except:
                        tokia, created = Tokia.objects.get_or_create(izena=slugify(eremua))

                if tokia:
                    tokia=tokia
                    #import pdb; pdb.set_trace()
                    hautesk.errolda = int(str(row.pop(giltzak['censo'],'0')).replace('.','') or 0)
                    print 'errolda: '+str(hautesk.errolda)
                    hautesk.boto_emaileak = int(str(row.pop(giltzak['votantes'],'0')).replace('.','') or 0)
                    print 'botoemaileak: '+str(hautesk.boto_emaileak)
                    hautesk.baliogabeak = int(str(row.pop(giltzak['nulos'],'0')).replace('.','') or 0)
                    print 'baliogabeak: '+str(hautesk.baliogabeak)

                    hautesk.zuriak = int(str(row.pop(giltzak['blancos'],'0')).replace('.','') or 0)
                    hautesk.tokia = tokia
                    hautesk.hauteskundea = hauteskundea
                    hautesk.save()

                    try:
                        # ZABORRA KENTZEKO
                        komunitatea = row.pop(u'Nombre de Comunidad',None)
                        herrialde_izena = row.pop(u'Nombre de Provincia',None)
                        herria_kodea = row.pop(u'Código de Municipio',None)
                        mahaiak = row.pop(u'Número de mesas',None)
                        baliodunak = row.pop(u'Votos válidos',None)
                        hautagaienak = row.pop(giltzak['votos_a_candidaturas'],None)
                        biztanleak =  row.pop(u'Población','').replace('.','') or 0
                        #EJ

                        hautagaienak = row.pop(u'Cod Municipio',None)
                        hautagaienak = row.pop(u'Cod Comarca',None)
                        #NAF
                        hautagaienak = row.pop(u'CODIGO',None)


                        #Codmun
                        #Certif_alta
                    except:
                        pass

                    for alderdi, boto in row.items():

                        if boto and int(boto.replace('.',''))>0:
                            emaitza = HauteskundeEmaitzakTokian()
                            alderdia, created = Alderdia.objects.get_or_create(izena=alderdi, slug=slugify(alderdi), logoa=Photo.objects.all()[0])
                            emaitza.hauteskundeatokian=hautesk
                            emaitza.alderdia = alderdia

                            emaitza.botoak = int(boto.replace('.','')) or 0

                            emaitza.save()


class Command(BaseCommand):
    args = 'Irekiako datuak import'
    help = 'Irekiako csvak irakurtzeko'


    def handle(self, *args, **options):
        csvak_irakurri()
