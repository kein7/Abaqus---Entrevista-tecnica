from django.core.management.base import BaseCommand
from datetime import date
from investments.models.models import Portfolio, Asset
from investments.services.trade import process_trade_service

class Command(BaseCommand):
    help = 'Ejecuta la operación de compra/venta del 15/05/2022 (Punto 6)'

    def handle(self, *args, **options):
        try:
            p1 = Portfolio.objects.get(name__iexact="portafolio 1")
            eeuu = Asset.objects.get(name__iexact="EEUU")
            europa = Asset.objects.get(name__iexact="Europa")

            msg = process_trade_service(
                portfolio=p1,
                date=date(2022, 5, 15),
                asset_sell_obj=eeuu,
                asset_buy_obj=europa,
                amount_usd=200000000
            )
            self.stdout.write(self.style.SUCCESS(msg))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al ejecutar trade: {e}"))