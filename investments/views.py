import json
from django.shortcuts import render
from investments.selectors.calculus import portfolio_history_selector
from investments.models.models import Portfolio

def portfolio_dashboard(request, pk):
    portfolio = Portfolio.objects.get(pk=pk)
    
    # Obtenemos el historial (Punto 4)
    # En un caso real, start_date y end_date vendrían de request.GET
    history_data = portfolio_history_selector(pk, '2022-02-15', '2023-02-16')
    
    context = {
        'portfolio': portfolio,
        'history_json': json.dumps(history_data), # Lo pasamos como string JSON
    }
    return render(request, 'dashboard.html', context)