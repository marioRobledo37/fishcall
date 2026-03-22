import uuid

from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
from django.core.files import File

from users.models import Fisher

# ===============================
# IMPORTS SEGUROS (NO ROMPEN EN PRODUCCIÓN)
# ===============================

try:
    from .fish_ai import detect_species
except ImportError:
    detect_species = None

try:
    from .fish_measure import measure_fish
except ImportError:
    measure_fish = None


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

    MODE_CHOICES = [
        ("SELF", "Autogestionado"),
        ("PRO", "Evento profesional"),
    ]

    name = models.CharField(max_length=150)

    organizer = models.ForeignKey(
        "clubs.Organization",
        on_delete=models.CASCADE,
        related_name="organized_contests"
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default="SELF"
    )

    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    join_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)

    def total_centimeters(self):
        return (
            self.captures
            .filter(status="approved")
            .aggregate(total=Sum("length_cm"))["total"] or 0
        )

    def biggest_capture(self):
        return (
            self.captures
            .filter(status="approved")
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
                        capture__status="approved"
                    )
                ),
                total_captures=Count(
                    "capture",
                    filter=Q(
                        capture__contest=self,
                        capture__status="approved"
                    )
                )
            )
            .filter(total_points__isnull=False)
            .order_by("-total_points")
        )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


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

    is_main = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

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

    competitor_number = models.IntegerField(null=True, blank=True)

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

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("approved", "Aprobada"),
        ("rejected", "Rechazada"),
    ]

    fisher = models.ForeignKey(Fisher, on_delete=models.CASCADE)

    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="captures"
    )

    species = models.CharField(max_length=50, blank=True)

    length_cm = models.IntegerField(null=True, blank=True)

    photo = models.ImageField(
        upload_to="captures/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    approved_by = models.CharField(
        max_length=120,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # ===============================
        # MEDICIÓN AUTOMÁTICA (SI EXISTE)
        # ===============================
        if self.photo and not self.length_cm and measure_fish:
            try:
                measured = measure_fish(self.photo.url)
                if measured:
                    self.length_cm = measured
                    super().save(update_fields=["length_cm"])
            except Exception as e:
                print("ERROR MEDICION:", e)

        # ===============================
        # DETECCIÓN DE ESPECIE (SI EXISTE)
        # ===============================
        if self.photo and not self.species and detect_species:
            try:
                species_detected = detect_species(self.photo.url)
                if species_detected and species_detected != "Desconocido":
                    self.species = species_detected
                    super().save(update_fields=["species"])
            except Exception as e:
                print("ERROR ESPECIE:", e)

    def __str__(self):
        return f"{self.fisher.full_name} - {self.length_cm} cm"