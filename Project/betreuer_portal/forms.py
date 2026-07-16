from django import forms
from fragebogen.models import JugendlichePerson, Fragebogen

class GenerateLinkForm(forms.Form):
    jugendliche_person = forms.ModelChoiceField(
        queryset=JugendlichePerson.objects.all(),
        label="Jugendliche Person",
        empty_label="--- Bitte auswählen ---"
    )
    fragebogen = forms.ModelChoiceField(
        queryset=Fragebogen.objects.all(),
        label="Fragebogen Vorlage",
        empty_label="--- Bitte auswählen ---"
    )