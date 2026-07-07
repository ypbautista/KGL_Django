from django.shortcuts import render, get_object_or_404, redirect

from .models import (
    Fragebogen,
    FragebogenAntwort,
    FragebogenAbschnitt,
    AbschnittAntwort,
    FrageAntwort,
)

from .forms import AbschnittForm


def abschnitt_ausfuellen(request, fragebogen_id, person_id, abschnitt_nr):

    fragebogen = get_object_or_404(
        Fragebogen,
        id=fragebogen_id
    )

    abschnitte = list(
        fragebogen.abschnitte.all().order_by("reihenfolge")
    )

    fragebogen_abschnitt = get_object_or_404(
        FragebogenAbschnitt,
        fragebogen=fragebogen,
        reihenfolge=abschnitt_nr,
    )

    antwort, created = FragebogenAntwort.objects.get_or_create(
        jugendliche_person_id=person_id,
        fragebogen=fragebogen,
        bewertet_von="JugendlichePerson",
    )

    abschnitt_antwort = AbschnittAntwort.objects.filter(
        fragebogen_antwort=antwort,
        fragebogen_abschnitt=fragebogen_abschnitt,
    ).first()

    if request.method == "POST":

        form = AbschnittForm(
            request.POST,
            fragebogen_abschnitt=fragebogen_abschnitt,
            abschnitt_antwort=abschnitt_antwort,
        )

        if form.is_valid():

            abschnitt_antwort, created = AbschnittAntwort.objects.update_or_create(
                fragebogen_antwort=antwort,
                fragebogen_abschnitt=fragebogen_abschnitt,
                defaults={
                    "kommentar": form.cleaned_data["kommentar"]
                }
            )

            for abschnitt_frage in form.fragen:

                FrageAntwort.objects.update_or_create(
                    abschnitt_antwort=abschnitt_antwort,
                    frage=abschnitt_frage,
                    defaults={
                        "antwort_wert": form.cleaned_data[
                            f"frage_{abschnitt_frage.id}"
                        ]
                    }
                )

            action = request.POST.get("action")


            if action == "back":

                vorheriger_abschnitt = abschnitt_nr - 1

                return redirect(
                    "abschnitt_ausfuellen",
                    fragebogen_id=fragebogen.id,
                    person_id=person_id,
                    abschnitt_nr=vorheriger_abschnitt,
                )


            if action == "next":

                naechster_abschnitt = abschnitt_nr + 1

                if naechster_abschnitt <= len(abschnitte):

                    return redirect(
                        "abschnitt_ausfuellen",
                        fragebogen_id=fragebogen.id,
                        person_id=person_id,
                        abschnitt_nr=naechster_abschnitt,
                    )

                return redirect("success")


    else:

        form = AbschnittForm(
            fragebogen_abschnitt=fragebogen_abschnitt,
            abschnitt_antwort=abschnitt_antwort,
        )


    return render(
        request,
        "fragebogen.html",
        {
            "form": form,
            "fragebogen": fragebogen,
            "abschnitt": fragebogen_abschnitt,
            "abschnitt_nr": abschnitt_nr,
            "gesamt_abschnitte": len(abschnitte),
            "person_id": person_id,
        }
    )


def success(request):
    return render(
        request,
        "success.html"
    )