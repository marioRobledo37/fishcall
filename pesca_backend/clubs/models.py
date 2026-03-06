from django.db import models


class Organization(models.Model):
    TYPE_CHOICES = [
        ("CLUB", "Club"),
        ("PENA", "Peña"),
        ("FED", "Federación"),
        ("MUNI", "Municipalidad"),
        ("OTRO", "Otro"),
    ]

    name = models.CharField("Nombre", max_length=120)
    type = models.CharField("Tipo", max_length=10, choices=TYPE_CHOICES, default="CLUB")
    city = models.CharField("Ciudad", max_length=120, blank=True)
    province = models.CharField("Provincia", max_length=120, blank=True)
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.type})"
    
    logo = models.ImageField(
        "Logo",
        upload_to="organizations/",
        null=True,
        blank=True
    )