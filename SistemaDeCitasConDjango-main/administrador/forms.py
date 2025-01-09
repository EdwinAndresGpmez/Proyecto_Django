from django import forms
from .models import Horas, Lugares, Profesional,Pacientes,Servicio


from django.forms import ModelForm


from .models import Horas
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from usuario.models import Citas
from django.core.exceptions import ValidationError
from datetime import datetime, date



def crear_objeto(request, form_class, success_url, template_name):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Objeto creado exitosamente!')
            return redirect(success_url)
    else:
        form = form_class()
    return render(request, template_name, {'form': form})

from django import forms
from .models import Profesional

class FormProfesional(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = ['num_doc_prof', 'nombre_prof', 'especialidad_prof', 'telefono_prof', 'email_prof', 'estado_prof', 'lugares']
        widgets = {
            'num_doc_prof': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_prof': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad_prof': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_prof': forms.TextInput(attrs={'class': 'form-control'}),
            'email_prof': forms.EmailInput(attrs={'class': 'form-control'}),
            'estado_prof': forms.Select(choices=[(True, 'Activo'), (False, 'Inactivo')], attrs={'class': 'form-control'}),
            'lugares': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Selección múltiple
        }


class FormLugares(forms.ModelForm):
    class Meta:
        model = Lugares
        fields = ['nombre_lugar', 'ubicacion_lugar', 'lugares_estado']
        widgets = {
            'lugares_estado': forms.Select(choices=[(True, 'Activo'), (False, 'Inactivo')], attrs={'class': 'form-control'})
        }

class FormHoras(forms.ModelForm):
    num_doc_prof = forms.ChoiceField(
        choices=[],
        label="Documento Profesional",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Horas
        fields = ['inicio_hora', 'final_hora', 'horas_estado', 'id_prof', 'fecha_habilitada']
        widgets = {
            'inicio_hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'final_hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fecha_habilitada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profesionales_activos = Profesional.objects.filter(estado_prof=True)
        self.fields['num_doc_prof'].choices = [
            (prof.num_doc_prof, f"{prof.num_doc_prof} - {prof.nombre_prof}")
            for prof in profesionales_activos
        ]
        if self.instance and self.instance.id_prof:
            self.fields['num_doc_prof'].initial = self.instance.id_prof.num_doc_prof

    def clean(self):
        """
        Validación personalizada para evitar fechas y horas inválidas,
        además de prevenir solapamientos.
        """
        cleaned_data = super().clean()
        inicio_hora = cleaned_data.get('inicio_hora')
        final_hora = cleaned_data.get('final_hora')
        fecha_habilitada = cleaned_data.get('fecha_habilitada')
        num_doc_prof = cleaned_data.get('num_doc_prof')

        # Validar que la fecha no sea anterior a hoy
        if fecha_habilitada and fecha_habilitada < date.today():
            self.add_error('fecha_habilitada', "La fecha no puede ser anterior a hoy.")

        # Validar que las horas no sean anteriores a la hora actual si la fecha es hoy
        if fecha_habilitada == date.today():
            current_time = datetime.now().time()
            if inicio_hora and inicio_hora < current_time:
                self.add_error('inicio_hora', "La hora de inicio no puede ser anterior a la hora actual.")
            if final_hora and final_hora <= inicio_hora:
                self.add_error('final_hora', "La hora de finalización debe ser mayor que la hora de inicio.")

        # Validar solapamientos de horarios para el profesional
        if num_doc_prof:
            profesional = Profesional.objects.filter(num_doc_prof=num_doc_prof).first()
            if profesional:
                horarios_ocupados = Horas.objects.filter(
                    fecha_habilitada=fecha_habilitada,
                    id_prof=profesional
                )
                for horario in horarios_ocupados:
                    if (inicio_hora < horario.final_hora and final_hora > horario.inicio_hora):
                        self.add_error(
                            None,
                            "Ya existe horario registrado para esta franja de fecha y hora."
                        )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        num_doc_prof = self.cleaned_data.get('num_doc_prof')
        if num_doc_prof:
            instance.id_prof = Profesional.objects.filter(num_doc_prof=num_doc_prof).first()
        if commit:
            instance.save()
        return instance

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        fields = [
            'tipo_doc',
            'num_doc',
            'nombre_pac',
            'nacimiento_pac',
            'genero_pac',
            'direccion',
            'tipo_usuario',
            'pacientes_estado',
        ]
        labels = {
            'tipo_doc': 'Tipo de Documento',
            'num_doc': 'Número de Documento',
            'nombre_pac': 'Nombre del Paciente',
            'nacimiento_pac': 'Fecha de Nacimiento',
            'genero_pac': 'Género',
            'direccion': 'Dirección',
            'tipo_usuario': 'Tipo de Usuario',
            'pacientes_estado': 'Estado Activo',
        }
        widgets = {
            'nacimiento_pac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Seleccione una fecha'}),
            'pacientes_estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_doc'].widget.attrs.update({'class': 'form-select'})
        self.fields['num_doc'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre_pac'].widget.attrs.update({'class': 'form-control'})
        self.fields['genero_pac'].widget.attrs.update({'class': 'form-select'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_usuario'].widget.attrs.update({'class': 'form-select'})

    def clean_nacimiento_pac(self):
        nacimiento_pac = self.cleaned_data.get('nacimiento_pac')
        if nacimiento_pac and nacimiento_pac > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser superior a la fecha de hoy.')
        return nacimiento_pac

    def clean_num_doc(self):
        num_doc = self.cleaned_data.get('num_doc')
        if not num_doc.isdigit():  # Verifica si el número de documento solo contiene dígitos
            raise ValidationError('El número de documento solo debe contener números.')
        return num_doc


class FormServicios(forms.ModelForm):
    ESTADOS = [
        ('True', 'Activo'),
        ('False', 'Inactivo'),
    ]

    class Meta:
        model = Servicio
        fields = ['id_servicio', 'nombre_servicio', 'descripcion_servicio', 'profesionales', 'servicio_estado']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Campo servicio_estado como un ChoiceField con las opciones definidas
        self.fields['servicio_estado'] = forms.ChoiceField(
            choices=self.ESTADOS,
            widget=forms.Select(attrs={'class': 'form-control'}),
            required=True  # Cambia según si es obligatorio
        )
    profesionales = forms.ModelMultipleChoiceField(queryset=Profesional.objects.all(), required=False)

    def clean_nombre_servicio(self):
        nombre_servicio = self.cleaned_data.get('nombre_servicio')
        if Servicio.objects.filter(nombre_servicio=nombre_servicio).exists():
            raise forms.ValidationError(f"El servicio con el nombre '{nombre_servicio}' ya existe.")
        return nombre_servicio


class CargarHorarioArchivoForm(forms.Form):
    archivo = forms.FileField(label="Subir archivo CSV o XLSX")

    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        # Validar que el archivo sea de tipo .xlsx o .csv
        if not archivo.name.endswith(('.xlsx', '.csv')):
            raise forms.ValidationError("Solo se permiten archivos .xlsx o .csv.")

        # También puedes verificar el tamaño si es necesario
        if archivo.size > 10 * 1024 * 1024:  # 10MB máximo
            raise forms.ValidationError("El archivo es demasiado grande. El tamaño máximo permitido es 10 MB.")

        return archivo

# --- Forms  para uso de los reportes  ---

class ProfesionalForm(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = '__all__'


class LugarForm(forms.ModelForm):
    class Meta:
        model = Lugares
        fields = '__all__'


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Pacientes
        fields = '__all__'


class HoraForm(forms.ModelForm):
    class Meta:
        model = Horas
        fields = '__all__'


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'


class CitaForm(forms.ModelForm):
    class Meta:
        model = Citas
        fields = '__all__'