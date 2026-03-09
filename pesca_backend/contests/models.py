from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
from django.core.files import File
from users.models import Fisher
from .fish_ai import detect_species
from .fish_measure import measure_fish
from .fish_overlay import draw_measurement
from django.core.files.base import ContentFile
import cv2


# ===============================
# PUSH NOTIFICATIONS
# ===============================

class PushSubscription(models.Model):

    subscription = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)


# ===============================
# CONCURSO
# ===============================

class Contest(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Borrador"),
        ("OPEN", "Inscripción Abierta"),
        ("RUNNING", "En Curso"),
        ("CLOSED", "Finalizado"),
    ]

    name = models.CharField("Nombre del Concurso", max_length=150)

    organizer = models.ForeignKey(
        "clubs.Organization",
        on_delete=models.CASCADE,
        related_name="organized_contests",
        verbose_name="Organizador"
    )

    start_date = models.DateTimeField("Fecha inicio")
    end_date = models.DateTimeField("Fecha fin")

    status = models.CharField(
        "Estado",
        max_length=10,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    created_at = models.DateTimeField("Creado", auto_now_add=True)

    def total_centimeters(self):
        return (
            self.captures
            .filter(approved=True)
            .aggregate(total=Sum("length_cm"))["total"] or 0
        )

    def biggest_capture(self):
        return (
            self.captures
            .filter(approved=True)
            .order_by("-length_cm")
            .first()
        )

    def ranking(self):

        return (
            Fisher.objects
            .filter(registrations__contest=self)
            .annotate(
                total_points=Sum(
                    "capture__length_cm",
                    filter=Q(
                        capture__contest=self,
                        capture__approved=True
                    )
                ),
                total_captures=Count(
                    "capture",
                    filter=Q(
                        capture__contest=self,
                        capture__approved=True
                    )
                )
            )
            .filter(total_points__isnull=False)
            .order_by("-total_points")
        )

    class Meta:
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date.date()})"


# ===============================
# SPONSORS
# ===============================

class Sponsor(models.Model):

    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="sponsors"
    )

    name = models.CharField(max_length=200)

    logo = models.ImageField(upload_to="sponsors/")

    is_main = models.BooleanField(
        "Sponsor principal",
        default=False
    )

    active = models.BooleanField(
        "Activo",
        default=True
    )

    order = models.IntegerField(
        "Orden",
        default=0
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.contest.name})"


# ===============================
# INSCRIPCIÓN
# ===============================

class Registration(models.Model):

    PAYMENT_STATUS = [
        ("PENDING", "Pendiente"),
        ("PAID", "Pagado"),
        ("CANCELLED", "Cancelado"),
    ]

    fisher = models.ForeignKey(
        "users.Fisher",
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    competitor_number = models.IntegerField(
        "Número de pescador",
        null=True,
        blank=True
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default="PENDING"
    )

    qr_code = models.ImageField(
        upload_to="qrcodes/",
        blank=True,
        null=True
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("fisher", "contest")

    def __str__(self):
        return f"{self.fisher} - {self.contest}"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.qr_code and self.competitor_number:

            qr_data = f"C{self.contest.id}-P{self.competitor_number}"

            qr = qrcode.make(qr_data)

            buffer = BytesIO()
            qr.save(buffer, format="PNG")

            file_name = f"qr_{self.contest.id}_{self.competitor_number}.png"

            self.qr_code.save(file_name, File(buffer), save=False)

            super().save(update_fields=["qr_code"])


# ===============================
# CAPTURA
# ===============================

class Capture(models.Model):

    fisher = models.ForeignKey(Fisher, on_delete=models.CASCADE)
    
    overlay = models.ImageField(
        upload_to="measurements/",
        null=True,
        blank=True
    )

    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="captures"
    )

    species = models.CharField(
        max_length=50,
        blank=True
    )

    length_cm = models.FloatField(
        "Longitud (cm)",
        null=True,
        blank=True
    )

    photo = models.ImageField(
        upload_to="captures/",
        null=True,
        blank=True
    )

    approved = models.BooleanField(
        "Aprobada",
        default=False
    )

    approved_by = models.CharField(
        "Fiscal",
        max_length=120,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        "Fecha y hora",
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Captura"
        verbose_name_plural = "Capturas"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if self.photo and self.length_cm and not self.overlay:

            img = draw_measurement(self.photo.url, self.length_cm)

            _, buffer = cv2.imencode(".jpg", img)

            self.overlay.save(
                f"measure_{self.id}.jpg",
                ContentFile(buffer.tobytes()),
                save=False
            )

            super().save(update_fields=["overlay"])

    def points(self):

        if self.approved:
            return self.length_cm

        return 0

    def __str__(self):
        return f"{self.fisher.full_name} - {self.length_cm} cm"