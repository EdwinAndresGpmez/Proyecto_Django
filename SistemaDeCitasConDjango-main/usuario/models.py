from django.db import models


# Create your models here.


class Citas(models.Model):
    id_cit = models.AutoField(primary_key=True)
    id_usu = models.ForeignKey(
        to='entrarSistema.CrearCuenta', null=True, blank=True, on_delete=models.CASCADE
    )
    id_prof = models.ForeignKey(
        to='administrador.Profesional', null=True, blank=True, on_delete=models.CASCADE
    )
    id_lugar = models.ForeignKey(
        to='administrador.Lugares', null=True, blank=True, on_delete=models.CASCADE
    )  # Lugar donde se realizará la cita
    id_hora = models.ForeignKey(
        to='administrador.Horas', null=True, blank=True, on_delete=models.CASCADE
    )  # Hora asignada para la cita
    id_pac = models.ForeignKey(
        to='administrador.Pacientes', null=True, blank=True, on_delete=models.CASCADE
    )  # Paciente relacionado con la cita
    id_servicio = models.ForeignKey(
        to='administrador.Servicio', null=True, blank=True, on_delete=models.CASCADE, related_name='citas'
    )  # Servicio ofrecido en la cita
    dia_cit = models.DateField(verbose_name="Día de la cita")
    nota_cit = models.TextField(verbose_name="Nota adicional", blank=True, null=True)
    estado_cita = models.CharField(max_length=100, verbose_name="Estado de la cita")
    citas_estado = models.BooleanField(default=True, verbose_name="Estado activo de la cita")

    def __str__(self):
        return f"Cita {self.id_cit} - {self.id_pac} - {self.id_servicio.nombre_servicio}"


class HistoricoCitas(models.Model):
    id_historico = models.AutoField(primary_key=True)
    
    # Datos del usuario
    id_usu = models.IntegerField(null=True, blank=True, verbose_name="ID Usuario")
    nombre_usuario = models.CharField(max_length=255, blank=True, null=True)

    # Datos del profesional
    id_prof = models.IntegerField(null=True, blank=True, verbose_name="ID Profesional")
    nombre_prof = models.CharField(max_length=255, blank=True, null=True)
    especialidad_prof = models.CharField(max_length=255, blank=True, null=True)

    # Datos del lugar
    id_lugar = models.IntegerField(null=True, blank=True, verbose_name="ID Lugar")
    nombre_lugar = models.CharField(max_length=255, blank=True, null=True)
    ubicacion_lugar = models.CharField(max_length=255, blank=True, null=True)

    # Datos de la hora
    id_hora = models.IntegerField(null=True, blank=True, verbose_name="ID Hora")
    inicio_hora = models.TimeField(blank=True, null=True)
    final_hora = models.TimeField(blank=True, null=True)

    # Datos del paciente
    id_pac = models.IntegerField(null=True, blank=True, verbose_name="ID Paciente")
    nombre_pac = models.CharField(max_length=255, blank=True, null=True)
    tipo_doc_pac = models.CharField(max_length=2, blank=True, null=True)
    num_doc_pac = models.CharField(max_length=20, blank=True, null=True)

    # Datos del servicio
    id_servicio = models.IntegerField(null=True, blank=True, verbose_name="ID Servicio")
    nombre_servicio = models.CharField(max_length=255, blank=True, null=True)

    # Datos específicos de la cita
    dia_cit = models.DateField(verbose_name="Día de la cita")
    nota_cit = models.TextField(verbose_name="Nota adicional")
    estado_cita = models.CharField(max_length=100, verbose_name="Estado de la cita")
    citas_estado = models.BooleanField(default=True, verbose_name="Estado activo de la cita")
    
    # Fecha y hora de creación en el histórico
    fecha_historico = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return f"Histórico Cita {self.id_historico} - {self.nombre_pac} - {self.nombre_servicio}"
