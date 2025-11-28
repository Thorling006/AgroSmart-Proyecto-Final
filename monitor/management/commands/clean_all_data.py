from django.core.management.base import BaseCommand
from monitor.models import CustomUser, Crop, AbonoApplication, EmailVerification, WeatherRecord, CropAlert

class Command(BaseCommand):
    help = 'Elimina todos los usuarios, cultivos y datos relacionados (excepto root si existe)'

    def handle(self, *args, **options):
        # Eliminar cultivos y datos relacionados
        CropAlert.objects.all().delete()
        WeatherRecord.objects.all().delete()
        AbonoApplication.objects.all().delete()
        Crop.objects.all().delete()
        EmailVerification.objects.all().delete()
        # Eliminar usuarios excepto root
        CustomUser.objects.exclude(email='root@gmail.com').delete()
        self.stdout.write(self.style.SUCCESS('Todos los datos y usuarios (excepto root) han sido eliminados.'))
