from django.contrib import admin
from .models import Fisher


@admin.register(Fisher)
class FisherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "dni", "phone", "organization", "category")
    list_filter = ("category", "organization")
    search_fields = ("full_name", "dni", "phone")