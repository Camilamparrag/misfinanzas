from django import forms
from .models import Categoria, Ingreso, Gasto, Presupuesto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "tipo"]
        labels = {
            "nombre": "Nombre",
            "tipo": "Tipo",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if nombre:
            nombre = nombre.strip().capitalize()
        return nombre


class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ["descripcion", "monto", "fecha", "categoria"]
        labels = {
            "descripcion": "Descripción",
            "monto": "Monto",
            "fecha": "Fecha",
            "categoria": "Categoría",
        }
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        if self.user:
            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=self.user, tipo="INGRESO"
            )

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser un valor positivo.")
        return monto


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ["descripcion", "monto", "fecha", "categoria", "medio_pago"]
        labels = {
            "descripcion": "Descripción",
            "monto": "Monto",
            "fecha": "Fecha",
            "categoria": "Categoría",
            "medio_pago": "Medio de pago",
        }
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        if self.user:
            self.fields["categoria"].queryset = Categoria.objects.filter(
                usuario=self.user, tipo="GASTO"
            )

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser un valor positivo.")
        return monto


class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = ["mes", "año", "monto"]
        labels = {
            "mes": "Mes",
            "año": "Año",
            "monto": "Monto presupuestado",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["mes"] = forms.ChoiceField(
            label="Mes",
            choices=[
                (1, "Enero"), (2, "Febrero"), (3, "Marzo"),
                (4, "Abril"), (5, "Mayo"), (6, "Junio"),
                (7, "Julio"), (8, "Agosto"), (9, "Septiembre"),
                (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
            ],
        )
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser un valor positivo.")
        return monto
