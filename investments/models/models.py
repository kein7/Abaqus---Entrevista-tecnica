from django.db import models

class Asset(models.Model):
    """Representa un instrumento financiero (EEUU, Europa, etc.)"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    """Representa el precio P_{i,t} de un activo en una fecha dada"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    price = models.DecimalField(max_digits=20, decimal_places=6)

    class Meta:
        unique_together = ('asset', 'date')
        ordering = ['date']

class Portfolio(models.Model):
    """Representa un portafolio de inversión (Portafolio 1, 2)"""
    name = models.CharField(max_length=100)
    initial_value = models.DecimalField(max_digits=20, decimal_places=2, default=1000000000.00)

    def __str__(self):
        return self.name

class PortfolioAsset(models.Model):
    """
    Tabla intermedia que define la cantidad C_{i,t} de un activo en un portafolio.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=25, decimal_places=10)
    initial_weight = models.DecimalField(max_digits=10, decimal_places=6, default=0,help_text="w_{i,0}")
    effective_date = models.DateField()

    class Meta:
        unique_together = ('portfolio', 'asset', 'effective_date')
