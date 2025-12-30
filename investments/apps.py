from django.apps import AppConfig
import sys

class InvestmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'investments'

    def ready(self):
        # Evitamos la ejecución durante comandos de migración o ayuda
        if 'runserver' not in sys.argv:
            return

        # Importación diferida para evitar errores de carga circular
        from .models.models import Portfolio
        from .services.etl import data_ingestion_service
        import os

        # Verificamos si ya existen portfolios
        if not Portfolio.objects.exists():
            print("--- Base de datos vacía. Iniciando ETL automático... ---")
            excel_path = os.path.join(os.path.dirname(__file__), 'assets', 'datos.xlsx')
            
            if os.path.exists(excel_path):
                try:
                    data_ingestion_service(excel_path)
                    print("--- ETL finalizado exitosamente. ---")
                except Exception as e:
                    print(f"--- Error en ETL: {e} ---")
            else:
                print(f"--- Error: No se encontró el archivo en {excel_path} ---")