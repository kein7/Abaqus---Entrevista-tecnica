from django.db.models import Sum, F
from ..models.models import Portfolio, Price, PortfolioAsset
from datetime import date
from decimal import Decimal

def portfolio_history_selector(portfolio_id: int, start_date: date, end_date: date):
    """
    Calcula la evolución de Vt y wi,t para un portafolio.
    """
    portfolio = Portfolio.objects.get(id=portfolio_id)
    assets_in_portfolio = PortfolioAsset.objects.filter(portfolio=portfolio)
    
    # Obtenemos todas las fechas únicas de precios en el rango
    dates = Price.objects.filter(
        date__range=(start_date, end_date)
    ).values_list('date', flat=True).distinct().order_by('date')

    history = []

    for d in dates:
        v_t = Decimal('0.0')
        assets_data = []
        
        # 1. Calcular x_{i,t} y V_t
        for pa in assets_in_portfolio:
            try:
                price_obj = Price.objects.get(asset=pa.asset, date=d)
                x_it = price_obj.price * pa.quantity
                v_t += x_it
                assets_data.append({
                    'asset_name': pa.asset.name,
                    'x_it': x_it,
                    'price': price_obj.price
                })
            except Price.DoesNotExist:
                continue # O manejar falta de precio

        # 2. Calcular w_{i,t} una vez que tenemos V_t
        weights = []
        for item in assets_data:
            w_it = (item['x_it'] / v_t) if v_t > 0 else 0
            weights.append({
                'asset': item['asset_name'],
                'weight': float(w_it), # Convertir a float para JSON/Gráficos
                'value': float(item['x_it'])
            })

        history.append({
            'date': d.strftime('%Y-%m-%d'),
            'total_value': float(v_t),
            'weights': weights
        })

    return history