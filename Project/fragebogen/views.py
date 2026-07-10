from django.utils import timezone

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import io
import base64
import numpy as np

from django.template.loader import render_to_string
from weasyprint import HTML

from .models import (
    Einladung,
    FragebogenFall,
    FragebogenAntwort,
    FragebogenAbschnitt,
    AbschnittAntwort,
    FrageAntwort,
)

from .forms import AbschnittForm



def fragebogen_start(request, code):

    einladung = get_object_or_404(
        Einladung,
        code=code
    )

    return render(
        request,
        "fragebogen_start.html",
        {
            "fragebogen": einladung.fall.fragebogen,
            "einladung": einladung,
        }
    )



def abschnitt_ausfuellen(request, code, abschnitt_nr):

    einladung = get_object_or_404(
        Einladung,
        code=code
    )

    fragebogen = einladung.fall.fragebogen

    abschnitte = list(
        fragebogen.abschnitte.all()
        .order_by("reihenfolge")
    )


    abschnitt = get_object_or_404(
        FragebogenAbschnitt,
        fragebogen=fragebogen,
        reihenfolge=abschnitt_nr,
    )


    antwort, created = FragebogenAntwort.objects.get_or_create(
        einladung=einladung
    )


    abschnitt_antwort = (
        AbschnittAntwort.objects
        .filter(
            fragebogen_antwort=antwort,
            fragebogen_abschnitt=abschnitt,
        )
        .first()
    )


    if request.method == "POST":

        form = AbschnittForm(
            request.POST,
            fragebogen_abschnitt=abschnitt,
            abschnitt_antwort=abschnitt_antwort,
        )


        if form.is_valid():

            abschnitt_antwort, created = (
                AbschnittAntwort.objects.update_or_create(
                    fragebogen_antwort=antwort,
                    fragebogen_abschnitt=abschnitt,
                    defaults={
                        "kommentar":
                            form.cleaned_data["kommentar"]
                    }
                )
            )


            for frage in form.fragen:

                FrageAntwort.objects.update_or_create(
                    abschnitt_antwort=abschnitt_antwort,
                    frage=frage,
                    defaults={
                        "antwort_wert":
                            form.cleaned_data[
                                f"frage_{frage.id}"
                            ]
                    }
                )


            action = request.POST.get("action")


            if action == "back":

                return redirect(
                    "abschnitt_ausfuellen",
                    code=code,
                    abschnitt_nr=abschnitt_nr - 1,
                )


            if action == "next":

                next_section = abschnitt_nr + 1


                if next_section <= len(abschnitte):

                    return redirect(
                        "abschnitt_ausfuellen",
                        code=code,
                        abschnitt_nr=next_section,
                    )


                antwort.end_time = timezone.now()
                antwort.save()


                einladung.benutzt = True
                einladung.save()


                return redirect(
                    "success"
                )


    else:

        form = AbschnittForm(
            fragebogen_abschnitt=abschnitt,
            abschnitt_antwort=abschnitt_antwort,
        )


    return render(
        request,
        "fragebogen.html",
        {
            "form": form,
            "fragebogen": fragebogen,
            "einladung": einladung,
            "abschnitt": abschnitt,
            "abschnitt_nr": abschnitt_nr,
            "gesamt_abschnitte": len(abschnitte),
        }
    )



def success(request):

    return render(
        request,
        "success.html"
    )

def export_fragebogen_pdf(request, fall_id):

    fall = get_object_or_404(
        FragebogenFall,
        id=fall_id
    )


    antworten = (
        FragebogenAntwort.objects
        .filter(
            einladung__fall=fall
        )
        .prefetch_related(
            "abschnitt_antworten__fragebogen_abschnitt",
            "abschnitt_antworten__antworten__frage__frage_vorlage",
        )
        .order_by("-start_time")
    )


    selbsteinschaetzung = (
        antworten
        .filter(
            einladung__bezugsperson__isnull=True
        )
        .first()
    )


    fremdeinschaetzung = (
        antworten
        .filter(
            einladung__bezugsperson__isnull=False
        )
        .first()
    )


    abschnitte = (
        fall.fragebogen.abschnitte
        .all()
        .order_by("reihenfolge")
    )


    vergleich = []


    for abschnitt in abschnitte:

        fragen = abschnitt.fragen.all().order_by(
            "reihenfolge"
        )


        for frage in fragen:

            selbst_wert = None
            fremd_wert = None


            if selbsteinschaetzung:

                antwort = (
                    FrageAntwort.objects
                    .filter(
                        abschnitt_antwort__fragebogen_antwort=selbsteinschaetzung,
                        frage=frage
                    )
                    .first()
                )

                if antwort:
                    selbst_wert = antwort.antwort_wert



            if fremdeinschaetzung:

                antwort = (
                    FrageAntwort.objects
                    .filter(
                        abschnitt_antwort__fragebogen_antwort=fremdeinschaetzung,
                        frage=frage
                    )
                    .first()
                )

                if antwort:
                    fremd_wert = antwort.antwort_wert



            vergleich.append(
                {
                    "abschnitt": abschnitt.titel,
                    "frage": frage.frage_vorlage.text,
                    "selbst": selbst_wert,
                    "fremd": fremd_wert,
                }
            )



    categories = []
    selbst_values = []
    fremd_values = []


    for abschnitt in abschnitte:

        categories.append(
            abschnitt.titel
        )


        selbst_scores = []
        fremd_scores = []


        for eintrag in vergleich:

            if eintrag["abschnitt"] == abschnitt.titel:

                if eintrag["selbst"] is not None:
                    selbst_scores.append(
                        eintrag["selbst"]
                    )

                if eintrag["fremd"] is not None:
                    fremd_scores.append(
                        eintrag["fremd"]
                    )


        selbst_values.append(
            sum(selbst_scores) / len(selbst_scores)
            if selbst_scores
            else 0
        )


        fremd_values.append(
            sum(fremd_scores) / len(fremd_scores)
            if fremd_scores
            else 0
        )



    buffer = io.BytesIO()


    fig = plt.figure(
        figsize=(8,8)
    )


    if categories:

        count = len(categories)


        angles = [
            n / count * 2 * np.pi
            for n in range(count)
        ]

        angles += angles[:1]


        ax = plt.subplot(
            111,
            polar=True
        )


        ax.set_theta_offset(
            np.pi / 2
        )

        ax.set_theta_direction(
            -1
        )


        plt.xticks(
            angles[:-1],
            categories,
            size=10
        )


        plt.ylim(
            0,
            7
        )


        if any(selbst_values):

            ax.plot(
                angles,
                selbst_values + selbst_values[:1],
                label="Selbsteinschätzung",
                color="#3498db"
            )


        if any(fremd_values):

            ax.plot(
                angles,
                fremd_values + fremd_values[:1],
                label="Fremdeinschätzung",
                color="#e74c3c"
            )


        plt.legend()



    plt.savefig(
        buffer,
        format="png",
        bbox_inches="tight"
    )


    plt.close(fig)


    buffer.seek(0)


    chart_image = base64.b64encode(
        buffer.read()
    ).decode("utf-8")



    context = {

        "fall": fall,

        "selbsteinschaetzung":
            selbsteinschaetzung,

        "fremdeinschaetzung":
            fremdeinschaetzung,

        "vergleich":
            vergleich,

        "chart_image":
            chart_image,

    }



    html = render_to_string(
        "auswertung_pdf.html",
        context
    )


    pdf = HTML(
        string=html
    ).write_pdf()



    response = HttpResponse(
        pdf,
        content_type="application/pdf"
    )


    response["Content-Disposition"] = (
        'inline; filename="fragebogen_auswertung.pdf"'
    )


    return response