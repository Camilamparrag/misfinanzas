from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView, UpdateView
)
from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from datetime import date

from .models import Categoria, Ingreso, Gasto, Presupuesto
from .forms import (
    CategoriaForm, IngresoForm, GastoForm, PresupuestoForm,
    RegistroForm, PerfilForm, LoginForm,
)


# ─── Autenticación ───────────────────────────────────────────────

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    form_class = LoginForm

    def get_success_url(self):
        messages.success(self.request, f"Inicio de sesión exitoso. ¡Bienvenido {self.request.user.first_name or self.request.user.username}!")
        return reverse_lazy("dashboard")

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)


class RegisterView(FormView):
    template_name = "registration/register.html"
    form_class = RegistroForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Registro exitoso. ¡Bienvenido {user.first_name or user.username}!")
        return super().form_valid(form)


# ─── Perfil de Usuario ───────────────────────────────────────────

class PerfilView(LoginRequiredMixin, TemplateView):
    template_name = "core/perfil.html"


class PerfilUpdateView(LoginRequiredMixin, FormView):
    template_name = "core/perfil_form.html"
    form_class = PerfilForm
    success_url = reverse_lazy("perfil")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Perfil actualizado exitosamente.")
        return super().form_valid(form)


class CambiarPasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = "core/cambiar_password.html"
    success_url = reverse_lazy("perfil")

    def form_valid(self, form):
        result = super().form_valid(form)
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Contraseña cambiada exitosamente.")
        return result


# ─── Dashboard ───────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        hoy = date.today()

        ingresos = Ingreso.objects.filter(usuario=user)
        gastos = Gasto.objects.filter(usuario=user)

        total_ingresos = ingresos.aggregate(Sum("monto"))["monto__sum"] or 0
        total_gastos = gastos.aggregate(Sum("monto"))["monto__sum"] or 0
        balance = total_ingresos - total_gastos
        cantidad_movimientos = ingresos.count() + gastos.count()

        ultimos_ingresos = ingresos.order_by("-fecha")[:5]
        ultimos_gastos = gastos.order_by("-fecha")[:5]

        gastos_por_categoria = (
            gastos.values("categoria__nombre")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        presupuesto = Presupuesto.objects.filter(
            usuario=user, mes=hoy.month, año=hoy.year
        ).first()
        gasto_mes = gastos.filter(fecha__month=hoy.month, fecha__year=hoy.year).aggregate(
            Sum("monto")
        )["monto__sum"] or 0

        disponible = float(presupuesto.monto) - float(gasto_mes) if presupuesto else 0
        porcentaje = (float(gasto_mes) / float(presupuesto.monto) * 100) if presupuesto and presupuesto.monto > 0 else 0

        ctx.update({
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "balance": balance,
            "cantidad_movimientos": cantidad_movimientos,
            "ultimos_ingresos": ultimos_ingresos,
            "ultimos_gastos": ultimos_gastos,
            "gastos_por_categoria": gastos_por_categoria,
            "presupuesto": presupuesto,
            "gasto_mes": gasto_mes,
            "disponible": disponible,
            "porcentaje_presupuesto": porcentaje,
            "labels": [g["categoria__nombre"] for g in gastos_por_categoria],
            "data": [float(g["total"]) for g in gastos_por_categoria],
        })
        return ctx


# ─── Categorías CRUD ─────────────────────────────────────────────

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "core/categoria_list.html"
    context_object_name = "categorias"
    paginate_by = 10

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "core/categoria_form.html"
    success_url = reverse_lazy("categoria_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Categoría creada exitosamente.")
        return super().form_valid(form)


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "core/categoria_form.html"
    success_url = reverse_lazy("categoria_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada exitosamente.")
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = "core/categoria_confirm_delete.html"
    success_url = reverse_lazy("categoria_list")

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        categoria = self.get_object()
        if Ingreso.objects.filter(categoria=categoria).exists() or Gasto.objects.filter(categoria=categoria).exists():
            messages.error(request, "No se puede eliminar una categoría con movimientos asociados.")
            return redirect("categoria_list")
        messages.success(request, "Categoría eliminada exitosamente.")
        return super().delete(request, *args, **kwargs)


# ─── Ingresos CRUD ───────────────────────────────────────────────

class IngresoListView(LoginRequiredMixin, ListView):
    model = Ingreso
    template_name = "core/ingreso_list.html"
    context_object_name = "ingresos"
    paginate_by = 10

    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user).select_related("categoria")


class IngresoCreateView(LoginRequiredMixin, CreateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = "core/ingreso_form.html"
    success_url = reverse_lazy("ingreso_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Ingreso registrado exitosamente.")
        return super().form_valid(form)


class IngresoUpdateView(LoginRequiredMixin, UpdateView):
    model = Ingreso
    form_class = IngresoForm
    template_name = "core/ingreso_form.html"
    success_url = reverse_lazy("ingreso_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Ingreso actualizado exitosamente.")
        return super().form_valid(form)


class IngresoDeleteView(LoginRequiredMixin, DeleteView):
    model = Ingreso
    template_name = "core/ingreso_confirm_delete.html"
    success_url = reverse_lazy("ingreso_list")

    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Ingreso eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ─── Gastos CRUD ─────────────────────────────────────────────────

class GastoListView(LoginRequiredMixin, ListView):
    model = Gasto
    template_name = "core/gasto_list.html"
    context_object_name = "gastos"
    paginate_by = 10

    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user).select_related("categoria")


class GastoCreateView(LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = "core/gasto_form.html"
    success_url = reverse_lazy("gasto_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Gasto registrado exitosamente.")
        return super().form_valid(form)


class GastoUpdateView(LoginRequiredMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = "core/gasto_form.html"
    success_url = reverse_lazy("gasto_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Gasto actualizado exitosamente.")
        return super().form_valid(form)


class GastoDeleteView(LoginRequiredMixin, DeleteView):
    model = Gasto
    template_name = "core/gasto_confirm_delete.html"
    success_url = reverse_lazy("gasto_list")

    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Gasto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ─── Presupuestos CRUD ───────────────────────────────────────────

class PresupuestoListView(LoginRequiredMixin, ListView):
    model = Presupuesto
    template_name = "core/presupuesto_list.html"
    context_object_name = "presupuestos"
    paginate_by = 10

    def get_queryset(self):
        return Presupuesto.objects.filter(usuario=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        for p in ctx["presupuestos"]:
            gastado = Gasto.objects.filter(
                usuario=self.request.user,
                fecha__month=p.mes,
                fecha__year=p.año,
            ).aggregate(Sum("monto"))["monto__sum"] or 0
            p.gastado = gastado
            p.disponible = p.monto - gastado
            p.porcentaje = float(gastado) / float(p.monto) * 100 if p.monto > 0 else 0
        return ctx


class PresupuestoCreateView(LoginRequiredMixin, CreateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = "core/presupuesto_form.html"
    success_url = reverse_lazy("presupuesto_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Presupuesto registrado exitosamente.")
        return super().form_valid(form)


class PresupuestoUpdateView(LoginRequiredMixin, UpdateView):
    model = Presupuesto
    form_class = PresupuestoForm
    template_name = "core/presupuesto_form.html"
    success_url = reverse_lazy("presupuesto_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        return Presupuesto.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Presupuesto actualizado exitosamente.")
        return super().form_valid(form)


class PresupuestoDeleteView(LoginRequiredMixin, DeleteView):
    model = Presupuesto
    template_name = "core/presupuesto_confirm_delete.html"
    success_url = reverse_lazy("presupuesto_list")

    def get_queryset(self):
        return Presupuesto.objects.filter(usuario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Presupuesto eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)


# ─── Resumen Financiero ──────────────────────────────────────────

class ResumenView(LoginRequiredMixin, TemplateView):
    template_name = "core/resumen.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ingresos = Ingreso.objects.filter(usuario=user)
        gastos = Gasto.objects.filter(usuario=user)

        total_ingresos = ingresos.aggregate(Sum("monto"))["monto__sum"] or 0
        total_gastos = gastos.aggregate(Sum("monto"))["monto__sum"] or 0
        balance = total_ingresos - total_gastos

        count_gastos = gastos.count()
        promedio_gasto = total_gastos / count_gastos if count_gastos > 0 else 0

        categoria_mayor_gasto = (
            gastos.values("categoria__nombre")
            .annotate(total=Sum("monto"))
            .order_by("-total")
            .first()
        )

        ctx.update({
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "balance": balance,
            "promedio_gasto": promedio_gasto,
            "categoria_mayor_gasto": categoria_mayor_gasto,
        })
        return ctx


# ─── Búsqueda y Filtros ──────────────────────────────────────────

class BusquedaView(LoginRequiredMixin, TemplateView):
    template_name = "core/busqueda.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        request = self.request

        q = request.GET.get("q", "")
        tipo = request.GET.get("tipo", "")
        categoria_id = request.GET.get("categoria", "")
        fecha_desde = request.GET.get("fecha_desde", "")
        fecha_hasta = request.GET.get("fecha_hasta", "")
        mes = request.GET.get("mes", "")
        año = request.GET.get("año", "")

        ingresos = Ingreso.objects.filter(usuario=user).select_related("categoria")
        gastos = Gasto.objects.filter(usuario=user).select_related("categoria")

        if q:
            ingresos = ingresos.filter(descripcion__icontains=q)
            gastos = gastos.filter(descripcion__icontains=q)

        if categoria_id:
            ingresos = ingresos.filter(categoria_id=categoria_id)
            gastos = gastos.filter(categoria_id=categoria_id)

        if fecha_desde:
            ingresos = ingresos.filter(fecha__gte=fecha_desde)
            gastos = gastos.filter(fecha__gte=fecha_desde)

        if fecha_hasta:
            ingresos = ingresos.filter(fecha__lte=fecha_hasta)
            gastos = gastos.filter(fecha__lte=fecha_hasta)

        if mes:
            ingresos = ingresos.filter(fecha__month=mes)
            gastos = gastos.filter(fecha__month=mes)

        if año:
            ingresos = ingresos.filter(fecha__year=año)
            gastos = gastos.filter(fecha__year=año)

        resultados = []
        if not tipo or tipo == "INGRESO":
            for i in ingresos:
                resultados.append({"tipo": "Ingreso", "obj": i, "color": "success"})
        if not tipo or tipo == "GASTO":
            for g in gastos:
                resultados.append({"tipo": "Gasto", "obj": g, "color": "danger"})

        resultados.sort(key=lambda r: r["obj"].fecha, reverse=True)

        categorias = Categoria.objects.filter(usuario=user)

        ctx.update({
            "resultados": resultados,
            "categorias": categorias,
            "q": q,
            "tipo": tipo,
            "categoria_id": categoria_id,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "mes": mes,
            "año": año,
        })
        return ctx
