from django.utils import timezone

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from django.template.loader import render_to_string
from weasyprint import HTML
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

# #http://127.0.0.1:8000/export/fragebogennummer/ falls nochmals gebraucht
# def export_fragebogen_excel(request, code):
#     durchlaeufe = (
#       FragebogenAntwort.objects
#       .filter(einladung__code=code)
#       .select_related(
#         "jugendliche_person",
#         "bezugsperson",
#         "einladung",
#         "fragebogen",
#     )
#     .prefetch_related(
#         "abschnitt_antworten__fragebogen_abschnitt",
#         "abschnitt_antworten__antworten__frage__frage_vorlage",
#     )
# )
#     
#     excel_data = []
#     
#     for durchlauf in durchlaeufe:
#         row = {
#             'Startzeit': durchlauf.start_time.strftime('%Y-%m-%d %H:%M') if durchlauf.start_time else '',
#             'Fertigstellung': durchlauf.end_time.strftime('%Y-%m-%d %H:%M') if durchlauf.end_time else 'Noch offen',
#             'Vorname JP': durchlauf.jugendliche_person.vorname,
#             'Nachname JP': durchlauf.jugendliche_person.nachname,
#             'Ausgefüllt von': durchlauf.bewertet_von,
#             'Kürzel Betreuer': durchlauf.bezugsperson.kuerzel if durchlauf.bezugsperson and durchlauf.bezugsperson.kuerzel else '',
#             'Name Betreuer': f"{durchlauf.bezugsperson.vorname} {durchlauf.bezugsperson.nachname}" if durchlauf.bezugsperson else '',
#         }
#         
#         for abschnitt_ant in durchlauf.abschnitt_antworten.all():
#             for ant in abschnitt_ant.antworten.all():
#                 prefix = f"{ant.frage.reihenfolge} - {ant.frage.frage_vorlage.text[:30]}"
#                 row[f"{prefix} (Wertung)"] = ant.antwort_wert
#             
#             row[f"Kommentar ({abschnitt_ant.fragebogen_abschnitt.titel})"] = abschnitt_ant.kommentar
#             
#         excel_data.append(row)
#         
#     df = pd.DataFrame(excel_data)
#     
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = 'attachment; filename="verlauf_auswertung.xlsx"'
#     
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, sheet_name='Verlauf', index=False)
#         
#         workbook = writer.book
#         worksheet = writer.sheets['Verlauf']
#         
#         header_format = workbook.add_format({
#             'bold': True,
#             'text_wrap': True,
#             'valign': 'top',
#             'bg_color': '#4F81BD',
#             'font_color': 'white',
#             'border': 1
#         })
#         
#         for col_num, value in enumerate(df.columns.values):
#             worksheet.write(0, col_num, value, header_format)
#             
#         worksheet.set_column('A:B', 16)
#         worksheet.set_column('C:G', 15)
#         
#         if len(df.columns) > 7:
#             worksheet.set_column(7, len(df.columns) - 1, 20)
#             
#     return response

def export_fragebogen_pdf(request, code):
    einladung = get_object_or_404(Einladung, code=code)
    
    durchlaeufe = (
        FragebogenAntwort.objects
        .filter(einladung=einladung)
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
        .order_by('-start_time') 
    )
    
    pdf_data = []
    
    for durchlauf in durchlaeufe:
        row = {
            'start_time': durchlauf.start_time,
            'end_time': durchlauf.end_time,
            'bewertet_von': durchlauf.bewertet_von,
            'jp_name': f"{durchlauf.jugendliche_person.vorname} {durchlauf.jugendliche_person.nachname}",
            'betreuer_name': f"{durchlauf.bezugsperson.vorname} {durchlauf.bezugsperson.nachname}" if durchlauf.bezugsperson else '',
            'abschnitte': durchlauf.abschnitt_antworten.all()
        }
        pdf_data.append(row)


    latest_jp = durchlaeufe.filter(bewertet_von='JugendlichePerson').first()
    latest_bp = durchlaeufe.filter(bewertet_von='Bezugsperson').first()
    
    abschnitte = einladung.fragebogen.abschnitte.all().order_by('reihenfolge')
    categories = [a.titel for a in abschnitte]
    
    jp_values = []
    bp_values = []
    
    for abschnitt in abschnitte:
        if latest_jp:
            jp_ant = latest_jp.abschnitt_antworten.filter(fragebogen_abschnitt=abschnitt).first()
            if jp_ant and jp_ant.antworten.exists():
                avg = sum(a.antwort_wert for a in jp_ant.antworten.all()) / jp_ant.antworten.count()
                jp_values.append(avg)
            else:
                jp_values.append(0)
                

        if latest_bp:
            bp_ant = latest_bp.abschnitt_antworten.filter(fragebogen_abschnitt=abschnitt).first()
            if bp_ant and bp_ant.antworten.exists():
                avg = sum(a.antwort_wert for a in bp_ant.antworten.all()) / bp_ant.antworten.count()
                bp_values.append(avg)
            else:
                bp_values.append(0)

    fig = plt.figure(figsize=(8, 8))
    
    if categories and (jp_values or bp_values):
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1] 
        
        ax = plt.subplot(111, polar=True)
        

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        

        plt.xticks(angles[:-1], categories, size=10)
        

        ax.set_rlabel_position(0)
        plt.yticks([1, 2, 3, 4, 5, 6, 7], ["1","2","3","4","5","6","7"], color="grey", size=8)
        plt.ylim(0, 7)
        

        if jp_values:
            jp_v = jp_values + jp_values[:1]
            ax.plot(angles, jp_v, linewidth=2, linestyle='solid', label='Jugendliche Person (aktuell)', color='#3498db') # Blau
            ax.fill(angles, jp_v, '#3498db', alpha=0.15)
            
        if bp_values:
            bp_v = bp_values + bp_values[:1]
            ax.plot(angles, bp_v, linewidth=2, linestyle='solid', label='Betreuer/in (aktuell)', color='#e74c3c') # Rot
            ax.fill(angles, bp_v, '#e74c3c', alpha=0.15)
            
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=True)
        plt.title('Einschätzung der Kompetenzen', size=16, weight='bold', pad=30)
    else:
        ax = plt.subplot(111)
        ax.text(0.5, 0.5, 'Noch nicht genügend Daten für ein Diagramm', ha='center', va='center')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    context = {
        'pdf_data': pdf_data,
        'chart_image': chart_base64,
        'code': code
    }
    html_string = render_to_string('auswertung_pdf.html', context)

    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="auswertung.pdf"'
    
    return response