from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Categoria, Ingreso, Gasto, Presupuesto


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        label="Nombre", max_length=30, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        label="Apellido", max_length=30, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Correo electrónico", widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario o correo electrónico",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and "@" in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username


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
