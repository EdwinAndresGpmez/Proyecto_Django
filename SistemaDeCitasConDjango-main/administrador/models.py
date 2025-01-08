from django.db import models
from datetime import datetime
import datetime
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils.timezone import now



class Profesional(models.Model):
    id_prof = models.AutoField(primary_key=True)
    num_doc_prof = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número de Documento"
    )
    nombre_prof = models.CharField(max_length=255)
    especialidad_prof = models.CharField(max_length=255)
    telefono_prof = models.CharField(max_length=15, null=True, blank=True, unique=True)
    email_prof = models.EmailField(null=True, blank=True, unique=True)
    estado_prof = models.BooleanField(default=True)
    lugares = models.ManyToManyField(  
        'Lugares', 
        related_name="profesionales", 
        verbose_name="Lugares Asociados"
    )

    def __str__(self):
        lugares_asociados = ", ".join([lugar.nombre_lugar for lugar in self.lugares.all()])
        return f"{self.nombre_prof} - Lugares: {lugares_asociados if lugares_asociados else 'Sin lugar asociado'}"



class Horas(models.Model):
    id_hora = models.AutoField(primary_key=True)
    inicio_hora = models.TimeField(verbose_name="Hora de Inicio")
    final_hora = models.TimeField(verbose_name="Hora de Fin")
    horas_estado = models.BooleanField(default=True, verbose_name="Estado Activo")
    id_prof = models.ForeignKey(
        'Profesional',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='Horas',
        verbose_name="Profesional Asociado"
    )
    fecha_habilitada = models.DateField(
        default=datetime.date.today,
        verbose_name="Fecha Habilitada"
    )

    def clean(self):
        """
        Validaciones personalizadas:
        1. La hora de inicio debe ser anterior a la hora de fin.
        2. Evitar horarios duplicados (inicio, fin, fecha, profesional).
        """
        if self.inicio_hora and self.final_hora and self.inicio_hora >= self.final_hora:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin.")

        # Verificar duplicados
        if Horas.objects.filter(
            inicio_hora=self.inicio_hora,
            final_hora=self.final_hora,
            fecha_habilitada=self.fecha_habilitada,
            id_prof=self.id_prof
        ).exclude(id_hora=self.id_hora).exists():
            raise ValidationError("Ya existe un horario con estas características para este profesional.")

    @property
    def duracion(self):
        """
        Calcula la duración entre inicio_hora y final_hora.
        """
        if self.inicio_hora and self.final_hora:
            inicio = datetime.datetime.combine(datetime.date.today(), self.inicio_hora)
            final = datetime.datetime.combine(datetime.date.today(), self.final_hora)
            return final - inicio
        return timedelta(0)

    def __str__(self):
        return f"{self.inicio_hora.strftime('%H:%M')} - {self.final_hora.strftime('%H:%M')}"




class Lugares(models.Model):
    id_lugar = models.AutoField(primary_key=True)
    nombre_lugar = models.CharField(max_length=255, blank=True, null=True)
    ubicacion_lugar = models.CharField(max_length=255, blank=True, null=True)
    lugares_estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_lugar


class Pacientes(models.Model):
    id_pac = models.AutoField(primary_key=True)
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('OT', 'Otro'),
    ]
    
    TIPO_USUARIO_CHOICES = [
        ('Particular', 'Particular'),
        ('Foga', 'Foga'),
    ]
    
    tipo_doc = models.CharField(
        max_length=2,
        choices=TIPO_DOCUMENTO_CHOICES,
        verbose_name="Tipo de Documento"
    )
    num_doc = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número de Documento"
    )
    nombre_pac = models.CharField(max_length=255, verbose_name="Nombre del Paciente")
    nacimiento_pac = models.DateField(verbose_name="Fecha de Nacimiento")
    genero_pac = models.CharField(
        max_length=20, 
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        verbose_name="Género"
    )
    direccion = models.CharField(max_length=255, verbose_name="Dirección", blank=True, null=True)
    tipo_usuario = models.CharField(
        max_length=15,
        choices=TIPO_USUARIO_CHOICES,
        verbose_name="Tipo de Usuario"
    )
    pacientes_estado = models.BooleanField(default=True, verbose_name="Estado Activo")

    def __str__(self):
        return self.nombre_pac



class Auditoria(models.Model):
    id_aut = models.AutoField(primary_key=True)
    descripcion_aut = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

class Consultorio(models.Model):
    id_con = models.AutoField(primary_key=True)
    id_cit = models.ForeignKey(
        to='usuario.Citas', null=True, blank=True, on_delete=models.CASCADE)
    nota_con = models.TextField()
    nacimiento_con = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    consultorio_estado = models.BooleanField(default=True)
    # Relación con Profesional
    id_prof = models.ForeignKey(
        'Profesional', null=True, blank=True, on_delete=models.SET_NULL, related_name='consultorios')


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Nombre del Servicio"
    )
    descripcion_servicio = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción"
    )
    servicio_estado = models.BooleanField(
        default=True, 
        verbose_name="Estado Activo"
    )
    profesionales = models.ManyToManyField(
        Profesional, 
        blank=True, 
        related_name='servicios', 
        verbose_name="Profesionales Asociados"
    )

    def __str__(self):
        return self.nombre_servicio
