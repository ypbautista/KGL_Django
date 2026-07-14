from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404

from fragebogen.models import (
    JugendlichePerson, 
    FragebogenFall,
    FragebogenAntwort
)

@login_required
def dashboard(request):
    betreuer = request.user.bezugsperson
    
    faelle_des_betreuers = FragebogenFall.objects.filter(
        einladungen__bezugsperson=betreuer
    ).distinct()

    letzte_antworten = FragebogenAntwort.objects.filter(
        einladung__fall__in=faelle_des_betreuers
    ).select_related(
        'einladung__fall__jugendliche_person'
    ).order_by("-start_time")[:3]

    return render(request, "betreuer_portal/dashboard.html", {
        "betreuer": betreuer,
        "letzte_antworten": letzte_antworten,
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
    return redirect("betreuer_portal:dashboard")