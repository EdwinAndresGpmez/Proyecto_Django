from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import UsuarioRoles
from .models import CrearCuenta
from administrador.models import Pacientes
from django.core.exceptions import ValidationError


from django.contrib.auth import get_user_model, authenticate
User = get_user_model()


class FormIniciar(forms.Form):
    cedula = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresar cédula',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresar contraseña',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        cedula = cleaned_data.get('cedula')
        password = cleaned_data.get('password')

        # Verificar autenticación
        user = authenticate(username=cedula, password=password)
        if not user:
            raise forms.ValidationError("Credenciales inválidas.")
        return cleaned_data


User = get_user_model()

class FormRegistrar(forms.Form, UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar nombre',
            'onkeypress': 'return SoloLetras(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '60',
            'required': 'true',
            'name': 'nombre',
            'id': 'nombre',
        })
        self.fields['username'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar usuario',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'username',
            'id': 'username',
        })
        self.fields['correo'].widget.attrs.update({
            'type': 'email',
            'class': 'form-control',
            'placeholder': 'Ingresar Correo Electrónico',
            'onkeypress': 'return SoloCorreo(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '50',
            'required': 'true',
            'name': 'correo',
            'id': 'correo',
        })
        self.fields['nacionalidad'].widget.attrs.update({
            'type': 'select',
            'class': 'form-select',
            'required': 'true',
            'name': 'nacionalidad',
            'id': 'nacionalidad',
        })
        self.fields['cedula'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar cédula',
            'onkeypress': 'return SoloNumeros(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '20',
            'required': 'true',
            'name': 'cedula',
            'id': 'cedula',
        })
        self.fields['numero'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar número de teléfono. Ejemplo: 04161234567',
            'onkeypress': 'return SoloNumeros(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '20',
            'required': 'true',
            'name': 'numero',
            'id': 'numero',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresar contraseña',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'password1',
            'id': 'password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'password2',
            'id': 'password2',
        })

    nombre = forms.CharField()
    
    nacionalidad = forms.ChoiceField(
        choices=[
            ('CC', 'Cédula de ciudadanía'),
            ('TI', 'Tarjeta de identidad'),
            ('CE', 'Cédula de extranjería'),
            ('PA', 'Pasaporte'),
            ('OT', 'Otro'),
        ]
    )
    cedula = forms.CharField()
    numero = forms.CharField()
    correo = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'nombre', 'username', 'correo', 'nacionalidad',
            'cedula', 'numero', 'password1', 'password2'
        )

    def clean(self):
        cleaned_data = super(FormRegistrar, self).clean()
        cedula = cleaned_data.get('cedula')

        # Verificar si existe un paciente con esta cédula
        try:
            Pacientes.objects.get(num_doc=cedula)
        except Pacientes.DoesNotExist:
            raise ValidationError(
                {"cedula": "No existe un paciente asociado con esta cédula. Comuníquese con la Clínica para registrarlo."}
            )

        # Validación de contraseñas
        if not cleaned_data.get('password1') or not cleaned_data.get('password2'):
            raise ValidationError("Debe ingresar y confirmar la contraseña.")
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            self.add_error('password2', "Las contraseñas no coinciden.")

        # Validación de unicidad
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            self.add_error('username', "El usuario ya ha sido elegido, intente otro.")
        if User.objects.filter(correo=cleaned_data.get('correo')).exists():
            self.add_error('correo', "El correo ya ha sido elegido, intente otro.")
        if User.objects.filter(cedula=cedula).exists():
            self.add_error('cedula', "La cédula ya ha sido elegida, intente otra.")

        return cleaned_data
