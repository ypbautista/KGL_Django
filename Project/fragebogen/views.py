from django.utils import timezone

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import (
    Einladung,
    Fragebogen,
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
            "fragebogen": einladung.fragebogen,
            "einladung": einladung,
        }
    )

def abschnitt_ausfuellen(request, code, abschnitt_nr):

    einladung = get_object_or_404(
        Einladung,
        code=code,
    )

    fragebogen = einladung.fragebogen
    jugendliche_person = einladung.jugendliche_person

    abschnitte = list(
        fragebogen.abschnitte.all().order_by("reihenfolge")
    )

    fragebogen_abschnitt = get_object_or_404(
        FragebogenAbschnitt,
        fragebogen=fragebogen,
        reihenfolge=abschnitt_nr,
    )

    antwort, created = FragebogenAntwort.objects.get_or_create(
        einladung=einladung,
        defaults={
            "jugendliche_person": jugendliche_person,
            "fragebogen": fragebogen,
            "bewertet_von": "JugendlichePerson",
        }
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
                    code=code,
                    abschnitt_nr=vorheriger_abschnitt,
                )

            if action == "next":

                naechster_abschnitt = abschnitt_nr + 1

                if naechster_abschnitt <= len(abschnitte):

                    return redirect(
                        "abschnitt_ausfuellen",
                        code=code,
                        abschnitt_nr=naechster_abschnitt,
                    )
                antwort.end_time = timezone.now()
                antwort.save()

                einladung.benutzt = True
                einladung.save()

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
        }
    )


def success(request):
    return render(
        request,
        "success.html"
    )

#http://127.0.0.1:8000/export/fragebogennummer/
def export_fragebogen_excel(request, code):
    durchlaeufe = (
      FragebogenAntwort.objects
      .filter(einladung__code=code)
      .select_related(
        "jugendliche_person",
        "bezugsperson",
        "einladung",
        "fragebogen",
    )
    .prefetch_related(
        "abschnitt_antworten__fragebogen_abschnitt",
        "abschnitt_antworten__antworten__frage__frage_vorlage",
    )
)
    
    excel_data = []
    
    for durchlauf in durchlaeufe:
        row = {
            'Startzeit': durchlauf.start_time.strftime('%Y-%m-%d %H:%M') if durchlauf.start_time else '',
            'Fertigstellung': durchlauf.end_time.strftime('%Y-%m-%d %H:%M') if durchlauf.end_time else 'Noch offen',
            'Vorname JP': durchlauf.jugendliche_person.vorname,
            'Nachname JP': durchlauf.jugendliche_person.nachname,
            'Ausgefüllt von': durchlauf.bewertet_von,
            'Kürzel Betreuer': durchlauf.bezugsperson.kuerzel if durchlauf.bezugsperson and durchlauf.bezugsperson.kuerzel else '',
            'Name Betreuer': f"{durchlauf.bezugsperson.vorname} {durchlauf.bezugsperson.nachname}" if durchlauf.bezugsperson else '',
        }
        
        for abschnitt_ant in durchlauf.abschnitt_antworten.all():
            for ant in abschnitt_ant.antworten.all():
                prefix = f"{ant.frage.reihenfolge} - {ant.frage.frage_vorlage.text[:30]}"
                row[f"{prefix} (Wertung)"] = ant.antwort_wert
            
            row[f"Kommentar ({abschnitt_ant.fragebogen_abschnitt.titel})"] = abschnitt_ant.kommentar
            
        excel_data.append(row)
        
    df = pd.DataFrame(excel_data)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="verlauf_auswertung.xlsx"'
    
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Verlauf', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Verlauf']
        
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#4F81BD',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        worksheet.set_column('A:B', 16)
        worksheet.set_column('C:G', 15)
        
        if len(df.columns) > 7:
            worksheet.set_column(7, len(df.columns) - 1, 20)
            
    return response