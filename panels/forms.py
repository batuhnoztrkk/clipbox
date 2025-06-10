from django import forms
from .models import Panel

class PanelForm(forms.ModelForm):
    class Meta:
        model = Panel
        fields = '__all__'  # veya düzenlemek istediğiniz alanlar
