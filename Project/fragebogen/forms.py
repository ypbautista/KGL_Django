from django import forms

from .models import (
    AbschnittFrage,
    FrageAntwort,
)



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


        for frage in self.fragen:


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



            self.fields[
                f"frage_{frage.id}"
            ] = forms.IntegerField(

                label=frage.frage_vorlage.text,

                min_value=1,

                max_value=7,

                initial=initial,

                widget=forms.NumberInput(
                    attrs={
                        "type": "range",
                        "min": 1,
                        "max": 7,
                        "step": 1,
                    }
                )
            )