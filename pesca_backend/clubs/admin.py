from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "city", "province")
    search_fields = ("name", "city", "province")
    list_filter = ("type", "province")