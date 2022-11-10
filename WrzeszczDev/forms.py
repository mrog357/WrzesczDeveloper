from django import forms
from .models import Csvs

class HexaProperties(forms.Form):
    horizontal = forms.IntegerField(label='Wysokość')
    vertical = forms.IntegerField(label='Szerokosć')

class NewPlotName(forms.Form):
    new_name = forms.CharField(label='Nazwa')

class CsvModelForm(forms.ModelForm):

    class Meta:
        model = Csvs
        fields = ('file_name',)