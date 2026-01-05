import pandas as pd
from django.db import transaction
from investments.models.models import Asset, Price, Portfolio, PortfolioAsset
from decimal import Decimal
from datetime import date

def data_ingestion_service(file_path: str):
    """
    Función ETL mejorada para soportar historial de cantidades (Opción 1).
    """
    # 1. Cargar Hojas
    weights_df = pd.read_excel(file_path, sheet_name='weights')
    prices_df = pd.read_excel(file_path, sheet_name='Precios')

    # Definimos la fecha de inicio según la prueba técnica (15/02/2022)
    t0_date = date(2022, 2, 15)

    with transaction.atomic():
        # 2. Crear Portafolios (V0 = 1,000,000,000)
        v0 = Decimal('1000000000.00')
        p1, _ = Portfolio.objects.get_or_create(name="portafolio 1", defaults={'initial_value': v0})
        p2, _ = Portfolio.objects.get_or_create(name="portafolio 2", defaults={'initial_value': v0})

        # 3. Procesar Activos y Pesos iniciales
        for _, row in weights_df.iterrows():
            asset_name = row['activos']
            asset, _ = Asset.objects.get_or_create(name=asset_name)

            w1 = Decimal(str(row['portafolio 1']))
            w2 = Decimal(str(row['portafolio 2']))

            # Obtenemos P_{i,0} (el precio en t=0 para este activo)
            p_i0_val = Decimal(str(prices_df.iloc[0][asset_name]))
            
            # Calcular Cantidades iniciales 
            c_i0_p1 = (w1 * v0) / p_i0_val
            c_i0_p2 = (w2 * v0) / p_i0_val

            # Guardar con effective_date
            # Usamos update_or_create incluyendo la fecha en la búsqueda
            PortfolioAsset.objects.update_or_create(
                portfolio=p1, 
                asset=asset,
                effective_date=t0_date, # La cantidad rige desde el inicio
                defaults={'quantity': c_i0_p1, 'initial_weight': w1}
            )
            PortfolioAsset.objects.update_or_create(
                portfolio=p2, 
                asset=asset,
                effective_date=t0_date,
                defaults={'quantity': c_i0_p2, 'initial_weight': w2}
            )

        # 4. Cargar Historial de Precios P_{i,t}
        for _, row in prices_df.iterrows():
            current_date = row['Dates'] 
            for asset_name in weights_df['activos']:
                asset = Asset.objects.get(name=asset_name)
                Price.objects.update_or_create(
                    asset=asset,
                    date=current_date,
                    defaults={'price': Decimal(str(row[asset_name]))}
                )

    return "Carga completada con éxito con soporte de historial"