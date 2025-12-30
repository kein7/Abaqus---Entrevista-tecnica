from django.urls import path
from investments.apis.portfolio_history import PortfolioHistoryAPI
from investments.views import portfolio_dashboard

urlpatterns = [
    # Ruta para el Dashboard (Punto 5 - Bonus)
    path('dashboard/<int:pk>/', portfolio_dashboard, name='portfolio-dashboard'),
    
    # Ruta para la API REST (Punto 4)
    # Ejemplo: /api/portfolio/1/history/?fecha_inicio=2022-02-15&fecha_fin=2023-02-16
    path('api/portfolio/<int:pk>/history/', PortfolioHistoryAPI.as_view(), name='portfolio-history-api'),
]