from django import forms
from .models import Citas
from django.forms import ModelForm
from datetime import date
from administrador import models as modelsAdministrador


class FormCitas(forms.ModelForm):
    
    ESTADO_CHOICES = [
        ('Sin confirmar', 'Sin confirmar'),
        ('Aceptada', 'Aceptada'),
        ('Cancelada', 'Cancelada'),
    ]
    
    estado_cita = forms.ChoiceField(choices=ESTADO_CHOICES, required=False)
    paciente_id = forms.ModelChoiceField(
        queryset= modelsAdministrador.Pacientes.objects.all(),
        required=False,
        to_field_name='id_pac',  # Usa el campo `id_pac` del modelo Pacientes
        label="Paciente"
    )
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Opcional: Modificar los widgets de los campos si es necesario
        # Ejemplo para un campo de fecha
        self.fields['dia_cit'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Selecciona un día'})

    class Meta:
        model = Citas
        fields = ('id_usu', 'id_lugar', 'id_hora', 'id_pac', 
                  'dia_cit', 'nota_cit', 'estado_cita',  'id_servicio', 'id_prof')

    def clean(self):
        cleaned_data = super().clean()
        fecha_hoy = date.today()

        # Validar campo 'id_lugar'
        if not self.cleaned_data.get('id_lugar'):
            self.add_error('id_lugar', "Necesita elegir un lugar.")

        # Validar campo 'id_hora'
        elif not self.cleaned_data.get('id_hora'):
            self.add_error('id_hora', "Necesita elegir una hora.")

        # Validar campo 'dia_cit' (fecha de la cita)
        elif not self.cleaned_data.get('dia_cit'):
            self.add_error('dia_cit', "Necesita elegir un día de la cita.")
        elif self.cleaned_data.get('dia_cit') < fecha_hoy:
            self.add_error('dia_cit', "La fecha de la cita no puede ser en el pasado.")

        # Validar que no haya otra cita para el mismo usuario en el mismo día
        elif Citas.objects.filter(
            dia_cit=self.cleaned_data.get('dia_cit'),
            id_usu=self.cleaned_data.get('id_usu')
        ).exists():
            self.add_error('id_hora', "Ya tiene una cita programada para este día.")

        # Retornar los datos validados
        return cleaned_data