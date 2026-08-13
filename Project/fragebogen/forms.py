from django import forms

from .models import (
    AbschnittFrage,
    FrageAntwort,
)

CHOICES_FRAGEN = [
    (1, "überragend"),
    (2, "immer"),
    (3, "meistens"),
    (4, "oft"),
    (5, "manchmal"),
    (6, "selten"),
    (7, "nie"),
]

CHOICES_MOTIVATION = [
    (1, "extrem hoch"),
    (2, "hoch"),
    (3, "eher hoch"),
    (4, "mittel"),
    (5, "eher niedrig"),
    (6, "niedrig"),
    (7, "null Bock"),
]

class AbschnittForm(forms.Form):

    kommentar = forms.CharField(
        required=False,
        label="Kommentar",
        widget=forms.Textarea(
            attrs={
                "rows": 4
            }
        )
    )

    def __init__(
        self,
        *args,
        fragebogen_abschnitt=None,
        abschnitt_antwort=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        if abschnitt_antwort:
            self.fields["kommentar"].initial = (
                abschnitt_antwort.kommentar
            )

        self.fragen = (
            AbschnittFrage.objects
            .filter(
                fragebogen_abschnitt=fragebogen_abschnitt
            )
            .select_related(
                "frage_vorlage"
            )
            .order_by(
                "reihenfolge"
            )
        )

        for index, frage in enumerate(self.fragen):

            initial = None

            if abschnitt_antwort:

                antwort = (
                    FrageAntwort.objects
                    .filter(
                        abschnitt_antwort=abschnitt_antwort,
                        frage=frage,
                    )
                    .first()
                )

                if antwort:
                    initial = antwort.antwort_wert
            choices = CHOICES_MOTIVATION if index == 1 else CHOICES_FRAGEN

            self.fields[f"frage_{frage.id}"] = forms.TypedChoiceField(
                label=frage.frage_vorlage.text,
                coerce=int,
                choices=choices,
                initial=initial,
                widget=forms.RadioSelect(
                    attrs={
                        "class": "likert-radio-group"
                    }
                )
            )



        kommentar_field = self.fields.pop("kommentar", None)

        first_frage_key = f"frage_{self.fragen[0].id}" if self.fragen.exists() else None

        new_fields = {}
        for key, value in self.fields.items():
            new_fields[key] = value
            if key == first_frage_key and kommentar_field:
                new_fields["kommentar"] = kommentar_field
                kommentar_field = None

        if kommentar_field:
            new_fields["kommentar"] = kommentar_field

        self.fields = new_fields