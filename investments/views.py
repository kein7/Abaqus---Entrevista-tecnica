import json
from django.shortcuts import render
from investments.selectors.calculus import portfolio_history_selector
from investments.models.models import Portfolio

def portfolio_dashboard(request, pk):
    portfolio = Portfolio.objects.get(pk=pk)
    # Ya no llamamos al selector aquí. Solo pasamos el ID.
    context = {
        'portfolio': portfolio,
        'portfolio_id': pk,
    }
    return render(request, 'dashboard.html', context)