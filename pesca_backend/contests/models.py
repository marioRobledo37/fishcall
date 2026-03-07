from django.db import models
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import qrcode
from io import BytesIO
from django.core.files import File

from users.models import Fisher

# ===============================
# CONCURSO
# ===============================


class PushSubscription(models.Model):

    subscription = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    

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

    # ===============================
    # MÉTRICAS DEL CONCURSO
    # ===============================

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

    def ranking_by_organization(self):
        from django.db.models import Sum

        return (
            self.captures
            .filter(approved=True)
            .values("fisher__organization__name")
            .annotate(
                total_points=Sum("length_cm")
            )
            .order_by("-total_points")
    )
        
    
        
    def is_ranking_public(self):
        if self.status != "CLOSED":
            return False

        return timezone.now() >= self.end_date + timedelta(hours=1)
    
    def public_ranking(self, user=None):
        if self.is_ranking_public():
            return self.ranking()

        # Si no es público, solo admin puede verlo
        if user and user.is_staff:
            return self.ranking()

        return None

    class Meta:
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date.date()})"


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
        "contests.Contest",
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

    # 👇 AQUÍ VA LA FUNCIÓN
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
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name="captures"
    )

    species = models.CharField(max_length=50)
    length_cm = models.IntegerField()

    photo = models.ImageField(upload_to="captures/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    approved = models.BooleanField("Aprobada", default=False)

    approved_by = models.CharField(
        "Fiscal",
        max_length=120,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField("Fecha y hora", auto_now_add=True)

    class Meta:
        verbose_name = "Captura"
        verbose_name_plural = "Capturas"
        ordering = ["-created_at"]

    def points(self):
        if self.approved:
            return self.length_cm
        return 0

    def __str__(self):
        return f"{self.fisher.full_name} - {self.length_cm} cm"
    


