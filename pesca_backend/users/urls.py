from django.urls import path
from .views import find_fisher_by_dni

urlpatterns = [

    path("buscar-pescador/", find_fisher_by_dni, name="buscar_pescador"),

]