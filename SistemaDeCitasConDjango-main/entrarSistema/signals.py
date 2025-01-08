from django.db.models.signals import post_save
from django.dispatch import receiver
from entrarSistema.models import CrearCuenta
from administrador.models import Pacientes

@receiver(post_save, sender=CrearCuenta)
def asociar_paciente_a_cuenta(sender, instance, created, **kwargs):
    if created:  # Solo ejecuta al crear un usuario
        try:
            paciente = Pacientes.objects.get(num_doc=instance.cedula)
            instance.paciente = paciente
            instance.save()
        except Pacientes.DoesNotExist:
            # Opcional: manejar el caso en que no exista un paciente asociado
            print(f"No se encontró un paciente con cédula {instance.cedula}")
