from django.shortcuts import render, get_object_or_404
from .models import Capture, Contest, PushSubscription, Registration
from .forms import CaptureForm
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from .models import Registration, Contest, Capture
from django.views.decorators.csrf import csrf_exempt
import json


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
                length_cm=int(length)
            )

            return JsonResponse({"status": "ok"})

        except Registration.DoesNotExist:

            return JsonResponse({"error": "competitor not found"}, status=404)

    return JsonResponse({"error": "invalid method"}, status=400)


def director_panel(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    ranking = contest.ranking()

    biggest = contest.biggest_capture()

    total_cm = contest.total_centimeters()

    last_captures = Capture.objects.filter(
        contest=contest,
        approved=True
    ).order_by("-created_at")[:10]

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



def live_board(request, contest_id):

    contest = get_object_or_404(Contest, id=contest_id)

    captures = contest.captures.filter(
        approved=True
    ).select_related("fisher").order_by("-created_at")[:20]

    return render(
        request,
        "live_board.html",
        {
            "contest": contest,
            "captures": captures
        }
    )
    

def fiscal_capture(request, contest_id):

    contest = Contest.objects.get(id=contest_id)

    if request.method == "POST":

        form = CaptureForm(request.POST, request.FILES)

        if form.is_valid():

            capture = form.save(commit=False)

            capture.contest = contest
            capture.approved = True

            capture.save()

            return redirect(request.path)

    else:

        form = CaptureForm()

    return render(
        request,
        "fiscal_capture.html",
        {
            "form": form,
            "contest": contest
        }
    )
    



def fisher_lookup(request, contest_id):

    number = request.GET.get("number")

    try:

        reg = Registration.objects.select_related(
            "fisher",
            "fisher__organization"
        ).get(
            contest_id=contest_id,
            competitor_number=number
        )

        fisher = reg.fisher

        data = {
            "name": fisher.get_full_name(),
            "club": fisher.organization.name if fisher.organization else "",
            "photo": fisher.photo.url if fisher.photo else "",
            "number": reg.competitor_number
        }

        return JsonResponse(data)

    except Registration.DoesNotExist:

        return JsonResponse({"error": "not_found"})
    


def save_subscription(request):

    data = json.loads(request.body)

    PushSubscription.objects.create(
        subscription=data
    )

    return JsonResponse({"status":"ok"})
    
    