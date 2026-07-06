from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Autenticación
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("registro/", views.RegisterView.as_view(), name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Categorías
    path("categorias/", views.CategoriaListView.as_view(), name="categoria_list"),
    path("categorias/nueva/", views.CategoriaCreateView.as_view(), name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="categoria_update"),
    path("categorias/<int:pk>/eliminar/", views.CategoriaDeleteView.as_view(), name="categoria_delete"),
    # Ingresos
    path("ingresos/", views.IngresoListView.as_view(), name="ingreso_list"),
    path("ingresos/nuevo/", views.IngresoCreateView.as_view(), name="ingreso_create"),
    path("ingresos/<int:pk>/editar/", views.IngresoUpdateView.as_view(), name="ingreso_update"),
    path("ingresos/<int:pk>/eliminar/", views.IngresoDeleteView.as_view(), name="ingreso_delete"),
    # Gastos
    path("gastos/", views.GastoListView.as_view(), name="gasto_list"),
    path("gastos/nuevo/", views.GastoCreateView.as_view(), name="gasto_create"),
    path("gastos/<int:pk>/editar/", views.GastoUpdateView.as_view(), name="gasto_update"),
    path("gastos/<int:pk>/eliminar/", views.GastoDeleteView.as_view(), name="gasto_delete"),
    # Presupuestos
    path("presupuestos/", views.PresupuestoListView.as_view(), name="presupuesto_list"),
    path("presupuestos/nuevo/", views.PresupuestoCreateView.as_view(), name="presupuesto_create"),
    path("presupuestos/<int:pk>/editar/", views.PresupuestoUpdateView.as_view(), name="presupuesto_update"),
    path("presupuestos/<int:pk>/eliminar/", views.PresupuestoDeleteView.as_view(), name="presupuesto_delete"),
    # Perfil
    path("perfil/", views.PerfilView.as_view(), name="perfil"),
    path("perfil/editar/", views.PerfilUpdateView.as_view(), name="perfil_editar"),
    path("perfil/cambiar-password/", views.CambiarPasswordView.as_view(), name="cambiar_password"),
    # Resumen
    path("resumen/", views.ResumenView.as_view(), name="resumen"),
    # Búsqueda
    path("buscar/", views.BusquedaView.as_view(), name="busqueda"),
]
