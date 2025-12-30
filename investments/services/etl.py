import pandas as pd
from django.db import transaction
from investments.models.models import Asset, Price, Portfolio, PortfolioAsset
from decimal import Decimal

def data_ingestion_service(file_path: str):
    """
    Función ETL para cargar pesos y precios desde el archivo datos.xlsx.
    Implementa los puntos 2 y 3 de la prueba.
    """
    # 1. Cargar Hojas
    weights_df = pd.read_excel(file_path, sheet_name='weights')
    prices_df = pd.read_excel(file_path, sheet_name='Precios')

    with transaction.atomic():
        # 2. Crear Portafolios (Punto 3: V0 = 1,000,000,000)
        v0 = Decimal('1000000000.00')
        p1, _ = Portfolio.objects.get_or_create(name="portafolio 1", initial_value=v0)
        p2, _ = Portfolio.objects.get_or_create(name="portafolio 2", initial_value=v0)

        # 3. Procesar Activos y Pesos iniciales
        for _, row in weights_df.iterrows():
            asset_name = row['activos']
            asset, _ = Asset.objects.get_or_create(name=asset_name)

            w1 = Decimal(str(row['portafolio 1']))
            w2 = Decimal(str(row['portafolio 2']))

            # Carga de Precios para este activo (para obtener P_{i,0})
            p_i0_val = Decimal(str(prices_df.iloc[0][asset_name]))
            
            # Calcular Cantidades iniciales C_{i,0} = (w_{i,0} * V_0) / P_{i,0}
            c_i0_p1 = (w1 * v0) / p_i0_val
            c_i0_p2 = (w2 * v0) / p_i0_val

            # Guardar en PortfolioAsset
            PortfolioAsset.objects.update_or_create(
                portfolio=p1, asset=asset,
                defaults={'quantity': c_i0_p1, 'initial_weight': w1}
            )
            PortfolioAsset.objects.update_or_create(
                portfolio=p2, asset=asset,
                defaults={'quantity': c_i0_p2, 'initial_weight': w2}
            )

        # 4. Cargar Historial de Precios P_{i,t}
        # Iterar por filas (fechas) y columnas (activos)
        for _, row in prices_df.iterrows():
            date = row['Dates'] 
            for asset_name in weights_df['activos']:
                asset = Asset.objects.get(name=asset_name)
                Price.objects.update_or_create(
                    asset=asset,
                    date=date,
                    defaults={'price': Decimal(str(row[asset_name]))}
                )

    return "Carga completada con éxito"