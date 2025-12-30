from django.db import transaction
from investments.models.models import PortfolioAsset, Price
from decimal import Decimal
from django.core.exceptions import ValidationError

def process_trade_service(portfolio, date, asset_sell_obj, asset_buy_obj, amount_usd):
    """
    Procesa la permuta de activos usando Foreign Keys.
    Vende un monto en USD de un activo y compra el equivalente en otro.
    """
    amount_usd = Decimal(str(amount_usd))

    with transaction.atomic():
        # 1. Obtener precios al día de la operación (P_{i,t})
        try:
            p_sell = Price.objects.get(asset=asset_sell_obj, date=date).price
            p_buy = Price.objects.get(asset=asset_buy_obj, date=date).price
        except Price.DoesNotExist:
            raise ValidationError(f"No hay precios registrados para la fecha {date}")

        # 2. Obtener los activos en el portafolio (C_{i,t})
        pa_sell = PortfolioAsset.objects.get(portfolio=portfolio, asset=asset_sell_obj)
        # Usamos get_or_create por si el portafolio aún no tiene el activo que se desea comprar
        pa_buy, created = PortfolioAsset.objects.get_or_create(
            portfolio=portfolio, 
            asset=asset_buy_obj,
            defaults={'quantity': Decimal('0'), 'initial_weight': Decimal('0')}
        )

        # 3. Calcular variación de cantidades (Delta C)
        qty_to_reduce = amount_usd / p_sell
        qty_to_add = amount_usd / p_buy

        # 4. Validación: ¿Tiene suficiente cantidad para vender?
        if pa_sell.quantity < qty_to_reduce:
            raise ValidationError(
                f"Fondos insuficientes en {asset_sell_obj.name}. "
                f"Intenta vender {qty_to_reduce} pero solo tiene {pa_sell.quantity}"
            )

        # 5. Actualizar cantidades
        pa_sell.quantity -= qty_to_reduce
        pa_buy.quantity += qty_to_add

        pa_sell.save()
        pa_buy.save()

    return f"Trade exitoso: -{qty_to_reduce} {asset_sell_obj.name}, +{qty_to_add} {asset_buy_obj.name}"