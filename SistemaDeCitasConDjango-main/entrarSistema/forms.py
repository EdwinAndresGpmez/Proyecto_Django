from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import UsuarioRoles


from django.contrib.auth import get_user_model, authenticate
User = get_user_model()


class FormIniciar(forms.Form):

    # Inicializamos el formulario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración del campo 'cedula'
        self.fields['cedula'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar cédula',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'cedula',  # Cambiado de 'username' a 'cedula'
            'id': 'cedula',
        })
        
        # Configuración del campo 'password'
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresar contraseña',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'password',
            'id': 'password',
        })

    # Declaración de los campos
    cedula = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User  # Puede cambiar a CrearCuenta si usas este modelo personalizado
        fields = ('cedula', 'password')

    # Lógica de validación personalizada
    def clean(self):
        cleaned_data = super().clean()
        cedula = cleaned_data.get('cedula')
        password = cleaned_data.get('password')

        # Verificamos si la cédula y la contraseña son correctos
        user = authenticate(cedula=cedula, password=password)  # Usa cedula en lugar de username

        # Si el usuario no se autentica correctamente, lanzamos un error
        if user is None:
            raise forms.ValidationError(
                {'password': ["Los datos suministrados no existen o son incorrectos."]})

        return cleaned_data

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
        }),
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
        }),
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
        }),
        self.fields['nacionalidad'].widget.attrs.update({
            'type': 'select',
            'class': 'form-select',
            'required': 'true',
            'name': 'nacionalidad',
            'id': 'nacionalidad',
        }),
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
        }),
        self.fields['numero'].widget.attrs.update({
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'Ingresar número de telefono. Ejemplo: 04161234567',
            'onkeypress': 'return SoloNumeros(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '20',
            'required': 'true',
            'name': 'numero',
            'id': 'numero',
        }),
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
        }),
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingresar contraseña',
            'onkeypress': 'return SoloLetrasYNumerosYGuiones(event);',
            'onpaste': 'return false;',
            'minlength': '3',
            'maxlength': '30',
            'required': 'true',
            'name': 'password2',
            'id': 'password2',
        })

    nombre = forms.CharField()
    # usuario = forms.CharField()

    CHOICES = (
    ('NIT', 'NIT'),
    ('RC', 'Registro Civil'),
    ('CC', 'Cédula de ciudadanía'),
    ('TI', 'Tarjeta de identidad'),
    ('CE', 'Cédula de extranjería'),
    ('PA', 'Pasaporte'),
    ('AS', 'Adulto sin identificación'),
    ('MS', 'Menor sin identificación'),
    ('PE', 'Permiso especial'),
    ('CN', 'Nacido Vivo'),
    ('PT', 'Permiso protección Temporal'),
)

    nacionalidad = forms.ChoiceField(choices=CHOICES)

    cedula = forms.CharField()
    numero = forms.CharField()

    correo = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + \
            ('nombre', 'username', 'correo', 'nacionalidad',
             'cedula', 'numero', 'password1', 'password2')

    def clean(self):
        cleaned_data = super(FormRegistrar, self).clean()

        if not self.cleaned_data.get('password1'):
            del self.errors['password1']
            self.add_error(
                'password1', "Necesita escribir la contraseñas en ambos inputs.")
            self.add_error(
                'password2', "Necesita escribir la contraseñas en ambos inputs.")
        elif not self.cleaned_data.get('password2'):
            del self.errors['password2']
            self.add_error(
                'password1', "Necesita escribir la contraseñas en ambos inputs.")
            self.add_error(
                'password2', "Necesita escribir la contraseñas en ambos inputs.")
        else:
            if not self.cleaned_data.get('password1') == self.cleaned_data.get('password2'):
                del self.errors['password2']
                self.add_error(
                    'password2', "Las contraseñas no coinciden.")

        if User.objects.filter(username=self.cleaned_data.get('username')).exists():
            del self.errors['username']
            self.add_error(
                'username', "El usuario ya ha sido elegido, intente otro.")

        if not self.cleaned_data.get('username'):
            del self.errors['username']
            self.add_error(
                'username', "Necesita escribir un usuario.")

        if not self.cleaned_data.get('nombre'):
            del self.errors['nombre']
            self.add_error(
                'nombre', "Necesita escribir un nombre.")

        if User.objects.filter(correo=self.cleaned_data.get('correo')).exists():
            del self.errors['correo']
            self.add_error(
                'correo', "El usuario ya ha sido elegido, intente otro.")
        elif not self.cleaned_data.get('correo'):
            del self.errors['correo']
            self.add_error(
                'correo', "Necesita escribir un correo electrónico.")

        if not self.cleaned_data.get('nacionalidad'):
            del self.errors['nacionalidad']
            self.add_error(
                'nacionalidad', "Necesita elegir una nacionalidad.")

        if User.objects.filter(cedula=self.cleaned_data.get('cedula')).exists():
            del self.errors['cedula']
            self.add_error(
                'cedula', "La cédula ya ha sido elegida, intente otra.")
        elif not self.cleaned_data.get('cedula'):
            del self.errors['cedula']
            self.add_error(
                'cedula', "Necesita escribir una cedula.")

        if not self.cleaned_data.get('numero'):
            del self.errors['numero']
            self.add_error(
                'numero', "Necesita escribir un número telefónico.")
        return cleaned_data
