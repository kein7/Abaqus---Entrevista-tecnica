from django.db.models import OuterRef, Subquery
from investments.models.models import Portfolio, Price, PortfolioAsset, Asset
from datetime import date
from decimal import Decimal

def portfolio_history_selector(portfolio_id: int, start_date: date, end_date: date):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    
    # 1. Obtenemos los IDs de los activos que han pasado por este portafolio
    # Usamos values_list y distinct() sin parámetros (que sí es compatible con SQLite)
    asset_ids = PortfolioAsset.objects.filter(
        portfolio=portfolio
    ).values_list('asset_id', flat=True).distinct()
    
    # 2. Obtenemos los nombres de esos activos para el mapeo del JSON
    # Esto es mucho más eficiente y compatible
    assets = Asset.objects.filter(id__in=asset_ids)
    asset_names = {a.id: a.name for a in assets}
    
    # El resto del código sigue igual...
    prices_query = Price.objects.filter(
        asset_id__in=asset_ids,
        date__range=(start_date, end_date)
    ).order_by('date')

    # Agrupamos precios por fecha
    prices_by_date = {}
    for p in prices_query:
        if p.date not in prices_by_date:
            prices_by_date[p.date] = []
        prices_by_date[p.date].append(p)

    history = []

    # 3. Iteramos cronológicamente
    for d in sorted(prices_by_date.keys()):
        v_t = Decimal('0.0')
        daily_assets = []
        
        for price_obj in prices_by_date[d]:
            # --- CAMBIO CLAVE PARA BONUS 2 ---
            # Buscamos la cantidad que estaba vigente en la fecha 'd'
            # Es decir: la cantidad con la fecha efectiva más reciente pero que no supere a 'd'
            posicion_vigente = PortfolioAsset.objects.filter(
                portfolio=portfolio,
                asset_id=price_obj.asset_id,
                effective_date__lte=d
            ).order_by('-effective_date').first()

            qty = posicion_vigente.quantity if posicion_vigente else Decimal('0')
            # ---------------------------------

            x_it = price_obj.price * qty
            v_t += x_it
            
            daily_assets.append({
                'asset_id': price_obj.asset_id,
                'x_it': x_it
            })

        # Calculamos los pesos w_it (mismo procedimiento anterior)
        weights = []
        for item in daily_assets:
            w_it = (item['x_it'] / v_t) if v_t > 0 else Decimal('0')
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