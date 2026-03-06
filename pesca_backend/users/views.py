from django.http import JsonResponse
from .models import Fisher


def find_fisher_by_dni(request):
    dni = request.GET.get("dni")

    try:
        fisher = Fisher.objects.get(dni=dni)

        data = {
            "exists": True,
            "id": fisher.id,
            "first_name": fisher.first_name,
            "last_name": fisher.last_name,
            "phone": fisher.phone,
            "category": fisher.category,
            "organization": fisher.organization.name if fisher.organization else None,
        }

    except Fisher.DoesNotExist:
        data = {"exists": False}

    return JsonResponse(data)