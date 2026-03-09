from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, get_object_or_404
from .models import Contest, Registration, Capture, Sponsor


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):

    list_display = ("name", "status", "start_date", "end_date", "ranking_button")

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:contest_id>/ranking/",
                self.admin_site.admin_view(self.ranking_view),
                name="contest-ranking",
            ),
        ]

        return custom_urls + urls

    def ranking_view(self, request, contest_id):

        contest = get_object_or_404(Contest, id=contest_id)

        ranking = list(contest.ranking())
        biggest = contest.biggest_capture()
        total_cm = contest.total_centimeters()

        # ==========================================
        # RANKING POR CATEGORÍA
        # ==========================================

        ranking_by_category = {}

        for fisher in ranking:
            category = fisher.category

            if category not in ranking_by_category:
                ranking_by_category[category] = []

            ranking_by_category[category].append(fisher)

        # ==========================================
        # AGRUPAR POR ORGANIZACIÓN
        # ==========================================

        ranking_by_org = {}

        for fisher in ranking:

            org = (
                fisher.organization.name
                if fisher.organization
                else "Sin organización"
            )

            if org not in ranking_by_org:
                ranking_by_org[org] = []

            ranking_by_org[org].append(fisher)

        # ==========================================
        # CALCULAR PUNTOS POR ORGANIZACIÓN
        # ==========================================

        ranking_org = []

        for org, fishers in ranking_by_org.items():

            total_points = sum(f.total_points for f in fishers)

            ranking_org.append({
                "name": org,
                "points": total_points,
                "members": len(fishers)
            })

        ranking_org = sorted(
            ranking_org,
            key=lambda x: x["points"],
            reverse=True
        )

        ranking_by_org = dict(
            sorted(
                ranking_by_org.items(),
                key=lambda item: len(item[1]),
                reverse=True
            )
        )

        context = dict(
            self.admin_site.each_context(request),
            contest=contest,
            ranking=ranking,
            ranking_org=ranking_org,
            ranking_by_org=ranking_by_org,
            ranking_by_category=ranking_by_category,
            biggest=biggest,
            total_cm=total_cm,
        )

        return render(request, "admin/contest_ranking.html", context)

    def ranking_button(self, obj):

        url = reverse("admin:contest-ranking", args=[obj.id])

        return format_html(
            '<a class="button" href="{}">🏆 Ver ranking</a>',
            url
        )

    ranking_button.short_description = "Ranking"


# ==========================================
# INSCRIPCIONES
# ==========================================

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "competitor_number",
        "fisher",
        "contest",
        "payment_status",
        "registered_at"
    )

    list_filter = ("contest", "payment_status")

    search_fields = (
        "fisher__full_name",
        "fisher__dni",
    )


# ==========================================
# CAPTURAS
# ==========================================

@admin.register(Capture)
class CaptureAdmin(admin.ModelAdmin):

    list_display = ("fisher", "contest", "length_cm", "approved", "created_at")
    list_filter = ("contest", "approved")
    search_fields = ("fisher__full_name",)
    
    
# ==========================================
# sponsors
# ==========================================


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):

    list_display = ("name","contest","is_main","active","order")
    list_filter = ("contest","is_main","active")
    ordering = ("order",)