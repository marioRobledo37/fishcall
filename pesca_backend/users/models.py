from django.db import models


class Fisher(models.Model):

    CATEGORY_CHOICES = [
        ("Hombres", "Hombres"),
        ("Mujeres", "Mujeres"),
        ("Cadetes", "Cadetes"),
        ("Niños", "Niños"),
    ]

    # TEMPORAL (se eliminará luego de migrar datos)
    full_name = models.CharField("Nombre completo", max_length=120)

    first_name = models.CharField("Nombre", max_length=80, blank=True)
    last_name = models.CharField("Apellido", max_length=80, blank=True)

    dni = models.CharField("DNI", max_length=20, unique=True)

    phone = models.CharField("Teléfono", max_length=20)

    birth_date = models.DateField(
        "Fecha de nacimiento",
        null=True,
        blank=True
    )

    photo = models.ImageField(
        "Foto de perfil",
        upload_to="fishers/",
        null=True,
        blank=True
    )

    organization = models.ForeignKey(
        "clubs.Organization",
        verbose_name="Club / Peña",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    
    CATEGORY_CHOICES = [
        ("MEN","Hombres"),
        ("WOMEN","Mujeres"),
        ("CADET","Cadetes"),
        ("SENIOR","Señor"),
        ("CHILDREN","Niños"),
    ]

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES
    )

    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        verbose_name = "Pescador"
        verbose_name_plural = "Pescadores"
        ordering = ["last_name", "first_name"]

    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.full_name

    def __str__(self):
        return self.get_full_name()