from collections import defaultdict
from decimal import Decimal
from datetime import date
from investments.models.models import Portfolio, Price, PortfolioAsset, Asset

def portfolio_history_selector(portfolio_id, start_date: date, end_date: date):
    # 1. Consulta para el portafolio
    portfolio = Portfolio.objects.get(id=portfolio_id)
    
    # 2. Traer todos los activos y crear un mapa de nombres
    # Usamos un diccionario de mapeo
    assets_map = {a.id: a.name for a in Asset.objects.all()}

    # 3. Traer todos los precios necesarios de una sola vez
    prices_query = Price.objects.filter(
        date__range=(start_date, end_date)
    ).order_by('date')

    # Agrupamos precios por fecha en un diccionario: 
    prices_by_date = defaultdict(list)
    for p in prices_query:
        prices_by_date[p.date].append(p)

    # 4. Traer todas las posiciones históricas de este portafolio
    posiciones_queryset = PortfolioAsset.objects.filter(
        portfolio=portfolio,
        effective_date__lte=end_date
    ).order_by('asset_id', 'effective_date')

    pos_history_map = defaultdict(list)
    for pa in posiciones_queryset:
        pos_history_map[pa.asset_id].append((pa.effective_date, pa.quantity))

    history = []

    # 5. Iteramos cronológicamente
    for d in sorted(prices_by_date.keys()):
        v_t = Decimal('0.0')
        daily_assets_calc = []
        
        for price_obj in prices_by_date[d]:
            asset_pos_history = pos_history_map.get(price_obj.asset_id, [])
            qty = Decimal('0.0')
            
            for effective_date, quantity in asset_pos_history:
                if effective_date <= d:
                    qty = quantity
                else:
                    break
            
            x_it = price_obj.price * qty
            v_t += x_it
            
            daily_assets_calc.append({
                'asset_id': price_obj.asset_id,
                'x_it': x_it
            })

        # 6. Cálculo de pesos w_it
        weights_list = []
        for item in daily_assets_calc:
            # w_it = x_it / V_t
            w_it = (item['x_it'] / v_t) if v_t > 0 else Decimal('0')
            
            weights_list.append({
                'asset': assets_map.get(item['asset_id'], "Unknown"),
                'weight': float(w_it), # Para el JSON de la API
                'value': float(item['x_it'])
            })

        history.append({
            'date': d.strftime('%Y-%m-%d'),
            'total_value': float(v_t),
            'weights': weights_list
        })

    return history