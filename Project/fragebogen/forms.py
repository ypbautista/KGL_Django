from django import forms
from .models import AbschnittFrage, FrageAntwort


class AbschnittForm(forms.Form):

    kommentar = forms.CharField(
        required=False,
        label="Kommentar",
        widget=forms.Textarea(attrs={"rows": 4})
    )

    def __init__(
        self,
        *args,
        fragebogen_abschnitt=None,
        abschnitt_antwort=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if abschnitt_antwort:
            self.fields["kommentar"].initial = abschnitt_antwort.kommentar

        self.fragen = AbschnittFrage.objects.filter(
            fragebogen_abschnitt=fragebogen_abschnitt
        ).order_by("reihenfolge")

        for abschnitt_frage in self.fragen:
            field_name = f"frage_{abschnitt_frage.id}"

            initial = None

            if abschnitt_antwort:
                response = FrageAntwort.objects.filter(
                    abschnitt_antwort=abschnitt_antwort,
                    frage=abschnitt_frage
                ).first()

                if response:
                    initial = response.antwort_wert

            self.fields[field_name] = forms.IntegerField(
                label=abschnitt_frage.frage_vorlage.text,
                min_value=1,
                max_value=5,
                initial=initial,
                widget=forms.NumberInput(
                    attrs={
                        "type": "range",
                        "min": 1,
                        "max": 5,
                        "step": 1,
                    }
                )
            )