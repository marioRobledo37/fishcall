from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

import json

from users.models import Fisher
from .models import Capture, Contest, PushSubscription, Registration, Sponsor
from .forms import CaptureForm
from .payments import create_payment_preference


# ============================
# LINK MAGICO DE INSCRIPCION
# ============================

def join_contest(request, code):

    contest = get_object_or_404(Contest, join_code=code)

    return render(
        request,
        "join_contest.html",
        {
            "contest": contest
        }
    )


# ============================
# API CAPTURA (APP / CELULAR)
# ============================

@csrf_exempt
def capture_sync(request):

    if request.method == "POST":

        print("POST:", request.POST)
        print("FILES:", request.FILES)

        contest_id = request.POST.get("contest_id")
        number = request.POST.get("number")
        species = request.POST.get("species")
        length = request.POST.get("length_cm")

        photo = request.FILES.get("photo")

        print("FOTO RECIBIDA:", photo)
# ============================
# LIVE BOARD
# ============================

def live_board(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    captures = Capture.objects.filter(
    contest=contest,
    status="approved"
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
# CAPTURAS PENDIENTES
# ============================

@staff_member_required
def pending_captures(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    captures = Capture.objects.filter(
        contest=contest,
        approved=False
    ).order_by("-created_at")

    return render(
        request,
        "pending_captures.html",
        {
            "contest": contest,
            "captures": captures
        }
    )


# ============================
# APROBAR CAPTURA
# ============================

@staff_member_required
def approve_capture(request, capture_id):

    capture = get_object_or_404(Capture, id=capture_id)

    capture.approved = True
    capture.approved_by = request.user.username
    capture.save()

    return redirect(request.META.get("HTTP_REFERER"))


# ============================
# RECHAZAR CAPTURA
# ============================

@staff_member_required
def reject_capture(request, capture_id):

    capture = get_object_or_404(Capture, id=capture_id)

    capture.delete()

    return redirect(request.META.get("HTTP_REFERER"))


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

    return render(
        request,
        "ranking_board.html",
        {
            "contest": contest,
            "captures": captures
        }
    )


# ============================
# PAGO DE INSCRIPCION
# ============================

def pay_registration(request, contest_id, fisher_id):

    contest = get_object_or_404(Contest, id=contest_id)
    fisher = get_object_or_404(Fisher, id=fisher_id)

    payment_url = create_payment_preference(contest, fisher)

    return redirect(payment_url)

# ============================
# sista de inscripcion
# ============================

def register_contest(request, code):

    contest = get_object_or_404(Contest, join_code=code)

    if request.method == "POST":

        name = request.POST.get("name")
        dni = request.POST.get("dni")
        phone = request.POST.get("phone")

        fisher, created = Fisher.objects.get_or_create(
            dni=dni,
            defaults={
                "full_name": name,
                "phone": phone
            }
        )

        # crear inscripción
        registration, created = Registration.objects.get_or_create(
            fisher=fisher,
            contest=contest
        )

        # asignar numero de pescador
        if not registration.competitor_number:

            last = (
                Registration.objects
                .filter(contest=contest)
                .order_by("-competitor_number")
                .first()
            )

            if last and last.competitor_number:
                registration.competitor_number = last.competitor_number + 1
            else:
                registration.competitor_number = 1

            registration.save()

        # si el torneo tiene costo
        if contest.entry_fee > 0 and contest.mode == "SELF":

            return redirect(
                f"/contest/{contest.id}/pay/{fisher.id}/"
            )

        return render(
            request,
            "registration_success.html",
            {
                "contest": contest,
                "registration": registration
            }
        )

    return render(
        request,
        "contest_register.html",
        {
            "contest": contest
        }
    )
    
def fisher_lookup_dni(request):
    dni = request.GET.get("dni")

    if not dni:
        return JsonResponse({"error": "DNI requerido"}, status=400)

    try:
        fisher = Fisher.objects.get(dni=dni)

        data = {
            "id": fisher.id,
            "name": fisher.name,
            "dni": fisher.dni,
        }

        return JsonResponse(data)

    except Fisher.DoesNotExist:
        return JsonResponse({"found": False})
    
    
def fishers_api(request, contest_id):

    regs = Registration.objects.filter(contest_id=contest_id)

    data = []

    for r in regs:
        data.append({
            "number": r.competitor_number,
            "name": r.fisher.full_name
        })

    return JsonResponse(data, safe=False)