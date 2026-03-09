from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Capture, Contest, PushSubscription, Registration, Sponsor
from .forms import CaptureForm

import json


# ============================
# API CAPTURA (APP / CELULAR)
# ============================

@csrf_exempt
def capture_sync(request):

    if request.method == "POST":

        number = request.POST.get("number")
        species = request.POST.get("species")
        length = request.POST.get("length_cm")

        try:

            reg = Registration.objects.get(
                contest_id=1,
                competitor_number=number
            )

            Capture.objects.create(
                fisher=reg.fisher,
                contest=reg.contest,
                species=species,
                length_cm=int(length),
                approved=True
            )

            return JsonResponse({"status": "ok"})

        except Registration.DoesNotExist:

            return JsonResponse(
                {"error": "competitor not found"},
                status=404
            )

    return JsonResponse({"error": "invalid method"}, status=400)


# ============================
# LIVE BOARD
# ============================

def live_board(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    captures = (
        Capture.objects
        .filter(contest=contest, approved=True)
        .select_related("fisher", "fisher__organization")
        .order_by("-id")[:30]
    )

    sponsors = (
        Sponsor.objects
        .filter(contest=contest, active=True)
        .order_by("order")
    )

    main_sponsor = sponsors.filter(is_main=True).first()

    return render(
        request,
        "live_board.html",
        {
            "contest": contest,
            "captures": captures,
            "sponsors": sponsors,
            "main_sponsor": main_sponsor
        }
    )


# ============================
# BROADCAST PRO
# ============================

def broadcast_view(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    capture = (
        Capture.objects
        .filter(contest=contest, approved=True)
        .select_related("fisher")
        .order_by("-id")
        .first()
    )

    ranking = contest.ranking()[:10]

    sponsors = (
        Sponsor.objects
        .filter(contest=contest, active=True)
        .order_by("order")
    )

    return render(
        request,
        "broadcast_pro.html",
        {
            "contest": contest,
            "capture": capture,
            "ranking": ranking,
            "sponsors": sponsors
        }
    )


# ============================
# API DETECTAR NUEVA CAPTURA
# ============================

def captures_json(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    capture = (
        Capture.objects
        .filter(contest=contest, approved=True)
        .select_related("fisher")
        .order_by("-id")
        .first()
    )

    if not capture:
        return JsonResponse({"id": None})

    return JsonResponse({

        "id": capture.id,
        "fisher": capture.fisher.get_full_name(),
        "species": capture.species,
        "length": capture.length_cm,
        "photo": capture.photo.url if capture.photo else None,
        "time": capture.created_at.strftime("%H:%M")

    })


# ============================
# PANEL DIRECTOR
# ============================

def director_panel(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    ranking = contest.ranking()

    biggest = contest.biggest_capture()

    total_cm = contest.total_centimeters()

    last_captures = Capture.objects.filter(
        contest=contest,
        approved=True
    ).order_by("-id")[:10]

    context = {
        "contest": contest,
        "ranking": ranking,
        "biggest": biggest,
        "total_cm": total_cm,
        "last_captures": last_captures,
    }

    return render(
        request,
        "director_panel.html",
        context
    )


# ============================
# CARGA FISCAL
# ============================

def fiscal_capture(request):

    if request.method == "POST":

        form = CaptureForm(request.POST, request.FILES)

        if form.is_valid():

            capture = form.save(commit=False)

            capture.approved = True

            capture.save()

            return redirect(request.path)

    else:

        form = CaptureForm()

    return render(
        request,
        "fiscal_capture.html",
        {
            "form": form
        }
    )


# ============================
# PUSH NOTIFICATIONS
# ============================

def save_subscription(request):

    data = json.loads(request.body)

    PushSubscription.objects.create(
        subscription=data
    )

    return JsonResponse({"status": "ok"})


# ============================
# RANKING BOARD
# ============================

def ranking_board(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    captures = (
        Capture.objects
        .filter(contest=contest, approved=True)
        .order_by("-length_cm")[:20]
    )

    return render(request, "ranking_board.html", {
        "contest": contest,
        "captures": captures
    })