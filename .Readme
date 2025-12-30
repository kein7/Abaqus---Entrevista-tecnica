# Readme - Prueba tecnica Abaqus

## Dependencias

- Django
- djangorestframework
- pandas
- openpyxl

## Ejecutar servidor

`python manage.py runserver`

## Inicializacion del proyecto

Para cumplir con las practicas de https://github.com/HackSoftware/Django-Styleguide

**Crear el proyecto base**
`django-admin startproject core .`

**Crear la aplicación para la lógica de negocios**
`python manage.py startapp investments`

## Models

Para los modelos se tomo en cuenta estas consideraciones.

- **DecimalField**: No se recomienda `FloatField` para aplicaciones financieras. Los errores de redondeo binario pueden arruinar los cálculos de $V_t$.
- **UniqueTogether**: Se garantiza integridad referencial; no puede haber dos precios para el mismo activo el mismo día.
- **PortfolioAsset**: Esta seria la tabla de hechos. Tener esta tabla permite actualizar las cantidades si hay compras o ventas.

### Migraciones

Para la creación de la base de datos se utilizo la funcionalidad de migraciones del ORM de DJango para generar las tablas a partir del modelo de base de datos definido.

Se utilizo los siguientes comandos del ORM de Django para generar la migracion.

```
python manage.py makemigrations investments
python manage.py migrate
```

## Etl

Para ejecutar de manera manual el etl hay que acceder al ORM de DJango

`python manage.py shell`

Y luego ejecutar el siguiente script

```
from investments.services.etl import data_ingestion_service
data_ingestion_service('assets/datos.xlsx')
```

**De todas maneras se realizo una automatizacion en el apps.py para que se ejecute en la primera run del servidor asegurando que no se ejecute durante migraciones o si la base de datos esta con datos**

## Selectors

Este selector calcula el historial de precios del total del valor de un portafolio

## Ejecucion del trade

```
python manage.py run_trade
```
