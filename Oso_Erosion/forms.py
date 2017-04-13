from django import forms
from Oso_Erosion.models import Rastermodel

class Rasterform(forms.ModelForm):
    class Meta:
        model = Rastermodel
        fields = ('project', 'rasterpath',)
