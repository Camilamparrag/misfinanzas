from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Categoria

CATEGORIAS_INGRESO = [
    "Sueldo",
    "Honorarios",
    "Horas Extras",
    "Bonificaciones",
    "Ventas",
    "Comisiones",
    "Inversiones",
    "Dividendos",
    "Intereses",
    "Arriendos Recibidos",
    "Reembolsos",
    "Regalos",
    "Otros Ingresos",
]

CATEGORIAS_GASTO = [
    "Alimentación",
    "Supermercado",
    "Transporte",
    "Combustible",
    "Arriendo",
    "Dividendo Hipotecario",
    "Servicios Básicos",
    "Internet",
    "Telefonía",
    "Salud",
    "Farmacia",
    "Educación",
    "Mascotas",
    "Ropa",
    "Entretenimiento",
    "Viajes",
    "Restaurantes",
    "Suscripciones",
    "Seguros",
    "Impuestos",
    "Ahorro",
    "Inversiones",
    "Tarjeta de Crédito",
    "Otros Gastos",
]


def crear_categorias_default(usuario):
    """Crea las categorías predeterminadas para un usuario."""
    for nombre in CATEGORIAS_INGRESO:
        Categoria.objects.get_or_create(
            usuario=usuario, nombre=nombre, tipo="INGRESO"
        )
    for nombre in CATEGORIAS_GASTO:
        Categoria.objects.get_or_create(
            usuario=usuario, nombre=nombre, tipo="GASTO"
        )


@receiver(post_save, sender=User)
def crear_categorias_al_registrar(sender, instance, created, **kwargs):
    if created:
        crear_categorias_default(instance)
