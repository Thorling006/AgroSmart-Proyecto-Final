from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# =========================
# USER MANAGER
# =========================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


# =========================
# CUSTOM USER
# =========================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    username = models.CharField("Usuario", max_length=80, blank=True, default="")
    display_name = models.CharField("Nombre visible", max_length=120, blank=True, default="")
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    bio = models.TextField(blank=True, default="")

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# =========================
# EMAIL VERIFICATION
# =========================
class EmailVerification(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_expired() and self.attempts < 5

    def __str__(self):
        return f"{self.email} - {self.code}"


# =========================
# CROP
# =========================
class Crop(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="crops"
    )
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, default="")
    country_code = models.CharField(max_length=2, default="SV")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    sowing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =========================
# ABONO APPLICATION
# =========================
class AbonoApplication(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aplicado", "Aplicado"),
        ("no_aplicado", "No Aplicado"),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="abono_applications")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="abono_applications"
    )
    date_applied = models.DateTimeField(null=True, blank=True)
    scheduled_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    notes = models.TextField(blank=True, default="")
    tip = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.crop.name} - {self.status}"


# =========================
# WEATHER RECORD
# =========================
class WeatherRecord(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="records")
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    rain_mm = models.FloatField(null=True, blank=True)
    wind_ms = models.FloatField(null=True, blank=True)
    recommendation = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.crop.name} @ {self.timestamp}"


# =========================
# ALERTS
# =========================
class CropAlert(models.Model):
    ALERT_TYPES = [
        ("irrigation", "Riego"),
        ("fertilizer", "Fertilizante"),
        ("pest", "Plaga"),
        ("general", "General"),
    ]

    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=32, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alert_type} - {self.crop.name}"


# =========================
# CHAT
# =========================
class ChatMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.recipient}"
