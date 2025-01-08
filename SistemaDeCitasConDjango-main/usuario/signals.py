from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Citas, HistoricoCitas

@receiver(post_save, sender=Citas)
def crear_historico_citas(sender, instance, created, **kwargs):
    if created:  # Solo ejecutar cuando se cree la cita (no cuando se actualice)
        HistoricoCitas.objects.create(
            id_usu=instance.id_usu.id if instance.id_usu else None,
            nombre_usuario=instance.id_usu.nombre if instance.id_usu else None,
            id_prof=instance.id_prof.id_prof if instance.id_prof else None,
            nombre_prof=instance.id_prof.nombre_prof if instance.id_prof else None,
            especialidad_prof=instance.id_prof.especialidad_prof if instance.id_prof else None,
            id_lugar=instance.id_lugar.id_lugar if instance.id_lugar else None,
            nombre_lugar=instance.id_lugar.nombre_lugar if instance.id_lugar else None,
            ubicacion_lugar=instance.id_lugar.ubicacion_lugar if instance.id_lugar else None,
            id_hora=instance.id_hora.id_hora if instance.id_hora else None,
            inicio_hora=instance.id_hora.inicio_hora if instance.id_hora else None,
            final_hora=instance.id_hora.final_hora if instance.id_hora else None,
            id_pac=instance.id_pac.id_pac if instance.id_pac else None,
            nombre_pac=instance.id_pac.nombre_pac if instance.id_pac else None,
            tipo_doc_pac=instance.id_pac.tipo_doc if instance.id_pac else None,
            num_doc_pac=instance.id_pac.num_doc if instance.id_pac else None,
            id_servicio=instance.id_servicio.id_servicio if instance.id_servicio else None,
            nombre_servicio=instance.id_servicio.nombre_servicio if instance.id_servicio else None,
            dia_cit=instance.dia_cit,
            nota_cit=instance.nota_cit,
            estado_cita=instance.estado_cita,
            citas_estado=instance.citas_estado,
        )
