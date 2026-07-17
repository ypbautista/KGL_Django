from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404

from fragebogen.models import (
    JugendlichePerson, 
    FragebogenFall,
    Einladung,
    FragebogenAntwort
)
from .forms import GenerateLinkForm

@login_required
def dashboard(request):
    betreuer = request.user.bezugsperson
    
    faelle_des_betreuers = FragebogenFall.objects.filter(
        einladungen__bezugsperson=betreuer
    ).prefetch_related('einladungen').distinct()

    fall_ids = list(faelle_des_betreuers.values_list('id', flat=True))

    alle_antworten = FragebogenAntwort.objects.filter(
        einladung__fall_id__in=fall_ids
    ).select_related(
        'einladung__fall__jugendliche_person'
    ).order_by("-start_time")

    letzte_antworten = []
    seen_falls = set()

    for antwort in alle_antworten:
        fall_id = antwort.einladung.fall_id
        if fall_id not in seen_falls:
            letzte_antworten.append(antwort)
            seen_falls.add(fall_id)
        
        if len(letzte_antworten) >= 3:
            break

    return render(request, "betreuer_portal/dashboard.html", {
        "betreuer": betreuer,
        "letzte_antworten": letzte_antworten,
        "aktive_faelle": faelle_des_betreuers,
    })

@login_required
def jugendliche_list(request):
    betreuer = request.user.bezugsperson
    suchbegriff = request.GET.get('q', '')

    jugendliche = JugendlichePerson.objects.filter(
        faelle__einladungen__bezugsperson=betreuer
    ).distinct()

    if suchbegriff:
        jugendliche = jugendliche.filter(
            Q(vorname__icontains=suchbegriff) | Q(nachname__icontains=suchbegriff)
        )

    return render(request, "betreuer_portal/jugendliche_list.html", {
        "jugendliche": jugendliche,
        "suchbegriff": suchbegriff,
        "betreuer": betreuer,
    })


@login_required
def jugendliche_detail(request, jp_id):  
    betreuer = request.user.bezugsperson
    
    jugendliche_person = get_object_or_404(JugendlichePerson, pk=jp_id)

    faelle = FragebogenFall.objects.filter(
        jugendliche_person=jugendliche_person,
        einladungen__bezugsperson=betreuer
    ).distinct()

    return render(request, "betreuer_portal/jugendliche_detail.html", {
        "jugendliche_person": jugendliche_person,
        "faelle": faelle, 
    })

@login_required
def generate_link(request):
    betreuer = request.user.bezugsperson
    jugendliche_link = None
    betreuer_link = None
    selected_jp = None

    if request.method == "POST":
        form = GenerateLinkForm(request.POST)
        if form.is_valid():
            jp = form.cleaned_data["jugendliche_person"]
            fb = form.cleaned_data["fragebogen"]
            selected_jp = jp

            fall = FragebogenFall.objects.create(
                jugendliche_person=jp,
                fragebogen=fb
            )

            selbst_einladung = Einladung.objects.create(
                fall=fall, 
                bezugsperson=None
            )
            
            fremd_einladung = Einladung.objects.create(
                fall=fall, 
                bezugsperson=betreuer
            )

            selbst_path = reverse("fragebogen_start", kwargs={"code": selbst_einladung.code})
            jugendliche_link = request.build_absolute_uri(selbst_path)

            fremd_path = reverse("fragebogen_start", kwargs={"code": fremd_einladung.code})
            betreuer_link = request.build_absolute_uri(fremd_path)
            
    else:
        form = GenerateLinkForm()

    return render(request, "betreuer_portal/generate_link.html", {
        "form": form,
        "jugendliche_link": jugendliche_link,
        "betreuer_link": betreuer_link,
        "selected_jp": selected_jp,
        "betreuer": betreuer,
    })