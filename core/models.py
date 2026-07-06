from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    TIPOS = [
        ("INGRESO", "Ingreso"),
        ("GASTO", "Gasto"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["tipo", "nombre"]
        unique_together = ("usuario", "nombre", "tipo")

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Ingreso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, limit_choices_to={"tipo": "INGRESO"}
    )

    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.descripcion} - ${self.monto}"


class Gasto(models.Model):
    MEDIOS_PAGO = [
        ("EFECTIVO", "Efectivo"),
        ("DEBITO", "Débito"),
        ("CREDITO", "Crédito"),
        ("TRANSFERENCIA", "Transferencia"),
        ("OTRO", "Otro"),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, limit_choices_to={"tipo": "GASTO"}
    )
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_PAGO, default="EFECTIVO")

    class Meta:
        verbose_name = "Gasto"
        verbose_name_plural = "Gastos"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.descripcion} - ${self.monto}"


class Presupuesto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mes = models.IntegerField()
    año = models.IntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Presupuesto"
        verbose_name_plural = "Presupuestos"
        ordering = ["-año", "-mes"]
        unique_together = ("usuario", "mes", "año")

    def __str__(self):
        return f"{self.get_mes_display()} {self.año} - ${self.monto}"

    def get_mes_display(self):
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
        ]
        return meses[self.mes - 1] if 1 <= self.mes <= 12 else "Mes inválido"
