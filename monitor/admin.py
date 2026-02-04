from django.contrib import admin
from .models import Crop, WeatherRecord, AbonoApplication, ChatMessage

@admin.register(AbonoApplication)
class AbonoApplicationAdmin(admin.ModelAdmin):
    list_display = ("crop", "user", "date_applied", "notes")
    list_filter = ("crop", "user")
    search_fields = ("notes",)

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "country_code", "sowing_date", "created_at")
    search_fields = ("name", "description")

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("crop", "timestamp", "temperature", "humidity", "rain_mm", "wind_ms")
    list_filter = ("crop",)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "created_at", "is_read")
    list_filter = ("created_at", "is_read", "sender", "recipient")
    search_fields = ("message", "sender__email", "recipient__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
