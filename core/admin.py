from django.contrib import admin
from .models import Categoria, Ingreso, Gasto, Presupuesto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "usuario")
    list_filter = ("tipo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "monto", "fecha", "categoria", "usuario")
    list_filter = ("fecha", "categoria")
    search_fields = ("descripcion",)
    ordering = ("-fecha",)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ("descripcion", "monto", "fecha", "categoria", "medio_pago", "usuario")
    list_filter = ("fecha", "categoria", "medio_pago")
    search_fields = ("descripcion",)
    ordering = ("-fecha",)


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "mes", "año", "monto")
    list_filter = ("año", "mes")
    ordering = ("-año", "-mes")
