# investments/apis.py
from rest_framework.views import APIView
from rest_framework.response import Response
from investments.selectors.calculus import portfolio_history_selector

class PortfolioHistoryAPI(APIView):
    def get(self, request, pk):
        start = request.query_params.get('fecha_inicio')
        end = request.query_params.get('fecha_fin')
        data = portfolio_history_selector(pk, start, end)
        return Response(data)