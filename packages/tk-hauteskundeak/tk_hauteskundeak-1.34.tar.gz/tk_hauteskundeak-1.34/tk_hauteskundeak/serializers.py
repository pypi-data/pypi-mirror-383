from rest_framework import serializers
from .models import Hauteskundea, HauteskundeaTokian, HauteskundeEserlekuakTokian, Alderdia, Tokia, HauteskundeEmaitzakTokian
from photologue.models import Photo
     
        

                

class PhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Photo
        fields = ["title", "slug", "image"]



class AlderdiaSerializer(serializers.ModelSerializer):
    logoa = PhotoSerializer()
    class Meta:
        model = Alderdia  
        fields = ["slug","akronimoa", "izena", "kolorea","logoa"]

        
class HauteskundeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hauteskundea
        fields = ['slug','izen_motza','izena','eguna']


class TokiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tokia  
        fields = ["slug","izena", "boundary_svg"]
                    

        
class HauteskundeaTokianSerializer(serializers.ModelSerializer):
    tokia = TokiaSerializer()
    hauteskundea = HauteskundeaSerializer()
    class Meta:
        model = HauteskundeaTokian        
        fields = ['jarlekuen_kopurua','errolda','boto_emaileak','eskrutinioa','baliogabeak','zuriak','hauteskundea','tokia']        
  
class HauteskundeaTokianSerializer2(serializers.ModelSerializer):
    #hauteskundea = HauteskundeaSerializer()
    tokia = TokiaSerializer()
    
    class Meta:
        model = HauteskundeaTokian        
        fields = ['jarlekuen_kopurua','errolda','boto_emaileak','eskrutinioa','baliogabeak','zuriak','tokia']        
  


class HauteskundeEmaitzaSerializer(serializers.ModelSerializer):
    alderdia = AlderdiaSerializer()
    hauteskundeatokian = HauteskundeaTokianSerializer()
    class Meta:
        model = HauteskundeEmaitzakTokian
        fields = ['alderdia','hauteskundeatokian', 'botoak','jarlekuak', 'ehunekoa', 'get_jarlekuak_aurrekoan']
    
  
class HauteskundeEserlekuakTokianSerializer(serializers.ModelSerializer):
    argazkia = PhotoSerializer()
    alderdia = AlderdiaSerializer()
    
    class Meta:
        model = HauteskundeEserlekuakTokian  
        fields = '__all__'
        



        