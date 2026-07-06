from django.db import migrations

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


def crear_categorias_default(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Categoria = apps.get_model("core", "Categoria")
    for usuario in User.objects.all():
        for nombre in CATEGORIAS_INGRESO:
            Categoria.objects.get_or_create(
                usuario=usuario, nombre=nombre, tipo="INGRESO"
            )
        for nombre in CATEGORIAS_GASTO:
            Categoria.objects.get_or_create(
                usuario=usuario, nombre=nombre, tipo="GASTO"
            )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_categorias_default),
    ]
