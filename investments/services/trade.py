from django.db import transaction
from investments.models.models import PortfolioAsset, Price
from decimal import Decimal
from django.core.exceptions import ValidationError

def process_trade_service(portfolio, date, asset_sell_obj, asset_buy_obj, amount_usd):
    amount_usd = Decimal(str(amount_usd))

    with transaction.atomic():
        # 1. Obtener precios (P_{i,t})
        p_sell = Price.objects.get(asset=asset_sell_obj, date=date).price
        p_buy = Price.objects.get(asset=asset_buy_obj, date=date).price

        # 2. Función para obtener la cantidad JUSTO ANTES de este día
        # Buscamos la fecha efectiva estrictamente menor a la actual
        def get_previous_qty(asset):
            pos = PortfolioAsset.objects.filter(
                portfolio=portfolio, 
                asset=asset, 
                effective_date__lt=date # < estrictamente menor
            ).order_by('-effective_date').first()
            return pos.quantity if pos else Decimal('0')

        # 3. Calcular Deltas
        qty_to_reduce = amount_usd / p_sell
        qty_to_add = amount_usd / p_buy

        # 4. Handler de la venta 
        current_pos_sell = PortfolioAsset.objects.filter(
            portfolio=portfolio, asset=asset_sell_obj, effective_date=date
        ).first()

        if current_pos_sell:
            new_qty_sell = current_pos_sell.quantity - qty_to_reduce
        else:
            new_qty_sell = get_previous_qty(asset_sell_obj) - qty_to_reduce

        if new_qty_sell < 0:
            raise ValidationError(f"Venta excede saldo disponible en {asset_sell_obj.name}")

        # Guardar/Actualizar registro de hoy
        PortfolioAsset.objects.update_or_create(
            portfolio=portfolio, asset=asset_sell_obj, effective_date=date,
            defaults={'quantity': new_qty_sell}
        )

        # 5. Manejo de la COMPRA (Asset Buy)
        current_pos_buy = PortfolioAsset.objects.filter(
            portfolio=portfolio, asset=asset_buy_obj, effective_date=date
        ).first()

        if current_pos_buy:
            new_qty_buy = current_pos_buy.quantity + qty_to_add
        else:
            new_qty_buy = get_previous_qty(asset_buy_obj) + qty_to_add

        PortfolioAsset.objects.update_or_create(
            portfolio=portfolio, asset=asset_buy_obj, effective_date=date,
            defaults={'quantity': new_qty_buy}
        )

    return f"Operación procesada para el {date}"