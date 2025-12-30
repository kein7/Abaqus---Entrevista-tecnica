from django.db.models import Sum, F
from investments.models.models import Portfolio, Price, PortfolioAsset
from datetime import date
from decimal import Decimal

def portfolio_history_selector(portfolio_id: int, start_date: date, end_date: date):
    """
    Calcula Vt y wi,t usando la relación Asset -> ForeignKey.
    """
    portfolio = Portfolio.objects.get(id=portfolio_id)
    # Traemos los activos del portafolio y sus nombres de una vez
    assets_in_portfolio = PortfolioAsset.objects.filter(
        portfolio=portfolio
    ).select_related('asset')
    
    # Mapeo de asset_id -> cantidad para búsqueda rápida en memoria
    quantities = {pa.asset_id: pa.quantity for pa in assets_in_portfolio}
    asset_names = {pa.asset_id: pa.asset.name for pa in assets_in_portfolio}

    # Obtenemos todos los precios en el rango de una sola vez
    prices_query = Price.objects.filter(
        asset_id__in=quantities.keys(),
        date__range=(start_date, end_date)
    ).order_by('date')

    # Agrupamos precios por fecha en un diccionario para procesar linealmente
    prices_by_date = {}
    for p in prices_query:
        if p.date not in prices_by_date:
            prices_by_date[p.date] = []
        prices_by_date[p.date].append(p)

    history = []

    # Iteramos sobre las fechas que tienen precios
    for d in sorted(prices_by_date.keys()):
        v_t = Decimal('0.0')
        daily_assets = []
        
        # Calculamos x_it y acumulamos V_t para esta fecha
        for price_obj in prices_by_date[d]:
            qty = quantities.get(price_obj.asset_id, Decimal('0'))
            x_it = price_obj.price * qty
            v_t += x_it
            
            daily_assets.append({
                'asset_id': price_obj.asset_id,
                'x_it': x_it
            })

        # Calculamos los pesos w_it
        weights = []
        for item in daily_assets:
            w_it = (item['x_it'] / v_t) if v_t > 0 else 0
            weights.append({
                'asset': asset_names[item['asset_id']],
                'weight': float(w_it),
                'value': float(item['x_it'])
            })

        history.append({
            'date': d.strftime('%Y-%m-%d'),
            'total_value': float(v_t),
            'weights': weights
        })

    return history