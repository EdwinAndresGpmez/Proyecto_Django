from __future__ import unicode_literals
from django.shortcuts import render, redirect
from administrador import models as modelsAdministrador
from administrador import views as viewsAdministrador
from .forms import FormCitas
from entrarSistema import forms as formsEntrarSistema
from entrarSistema import models as modelsEntrarSistema
from .models import Citas
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from programador import models as modelsProgramador

from django.utils import timezone



# Create your views here.


def inicio(request):
    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:

        if request.method == 'GET':

            formCitas = FormCitas()

            lista_horas = modelsAdministrador.Horas.objects.filter(
                horas_estado=True)
            lista_lugares = modelsAdministrador.Lugares.objects.filter(
                lugares_estado=True)
            lista_citas = Citas.objects.filter(
                id_usu=request.user.id, citas_estado=True).order_by('-id_cit')

            listaRoles = modelsEntrarSistema.UsuarioRoles.objects.filter(
                id_usu=request.user.id)

            return render(request, 'inicio.html', {
                'form': formCitas,

                'listaHoras': lista_horas,
                'listaLugares': lista_lugares,
                'listaCitas': lista_citas,
                'listaRoles': listaRoles
            })
        else:
            # formCitas = FormCitas()

            lista_horas = modelsAdministrador.Horas.objects.filter(
                horas_estado=True)
            lista_lugares = modelsAdministrador.Lugares.objects.filter(
                lugares_estado=True)
            lista_citas = Citas.objects.filter(
                id_usu=request.user.id, citas_estado=True)

            id_cita = Citas.objects.get(id_cit=request.POST['id_cit'])
            id_hora = modelsAdministrador.Horas.objects.get(
                id_hora=request.POST['id_hora'])
            id_lugar = modelsAdministrador.Lugares.objects.get(
                id_lugar=request.POST['id_lugar'])

            print(request.POST['id_pac'])

            if request.POST['id_pac'] == 'nada':
                pass
            else:
                id_pac = modelsAdministrador.Pacientes.objects.get(
                    id_pac=request.POST['id_pac'])
                id_cita.id_pac = id_pac
            id_cita.dia_cit = request.POST['dia_cit']
            id_cita.nota_cit = request.POST['nota_cit']
            id_cita.id_hora = id_hora
            id_cita.id_lugar = id_lugar

            id_cita.save()
            # Aqui ponemos el codigo del trigger -------

            Audi = modelsAdministrador.Auditoria(
                descripcion_aut=f"Se modificó una 'cita' en la tabla *Citas*, para el día {request.POST['dia_cit']}, modificado por el usuario: {request.user.id},")
            Audi.save()

            # fin de trigger ------
            return redirect('inicio')

        return render(request, 'inicio.html', {
            'form': formCitas,

            'listaHoras': lista_horas,
            'listaLugares': lista_lugares,
            'listaCitas': lista_citas,
        })



def cancelarCita(request, id_cit):
    now = timezone.now()  # Obtiene la hora en UTC
    now_local = timezone.localtime(now)  # Convertir a hora local
    print(f"Fecha y hora actual: {now_local}")

    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)
    if not tipoRol.es_usuario:
        return redirect('cerrar')

    # Obtener la cita
    try:
        idCita = Citas.objects.get(id_cit=id_cit)
    except Citas.DoesNotExist:
        messages.error(request, "La cita no existe.")
        return redirect('inicio')
    
    print(f"Fecha de la cita (dia_cit): {idCita.dia_cit}")
    print(f"Fecha actual (hoy): {now_local.date()}")

    # Verificar si la cita ya está cancelada
    if idCita.estado_cita == "Cancelada":
        messages.info(request, "La cita ya se encuentra cancelada.")
        return redirect('inicio')

    # Verificar si la fecha de la cita es anterior a la actual
    if idCita.dia_cit < now_local.date():
        messages.error(request, "No es posible cancelar citas con fechas anteriores a hoy.")
        return redirect('inicio')

    # Verificar si la cita tiene hora asociada
    if idCita.id_hora:
        # Combinar el día de la cita con la hora de inicio
        cita_datetime = datetime.combine(idCita.dia_cit, idCita.id_hora.inicio_hora)
    else:
        # Si no tiene una hora asociada, asumir la medianoche (00:00)
        cita_datetime = datetime.combine(idCita.dia_cit, datetime.min.time())

    # Asegurarse de que cita_datetime tenga la misma zona horaria que now_local
    cita_datetime = timezone.make_aware(cita_datetime, timezone.get_current_timezone())

    print(f"Fecha y hora de la cita: {cita_datetime}")

    # Verificar si faltan menos de 8 horas para la cita
    if cita_datetime - now_local < timedelta(hours=8):
        messages.error(request, "Solo puedes cancelar citas con al menos 8 horas de anticipación.")
        return redirect('inicio')

    # Cancelar la cita
    idCita.estado_cita = "Cancelada"
    idCita.citas_estado = False
    idCita.save()

    # Registrar la auditoría
    Audi = modelsAdministrador.Auditoria(
        descripcion_aut=f"Se cambió el estado de la cita con ID {id_cit} a 'Cancelada', realizada por el usuario: {request.user.id}."
    )
    Audi.save()

    # Mensaje de éxito
    messages.success(request, "La cita ha sido cancelada exitosamente.")
    return redirect('inicio')

def cita(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)
    if not tipoRol.es_usuario:
        return redirect('cerrar')

    fecha = request.GET.get("fecha")
    
    if request.method == 'GET':
        formCitas = FormCitas()

        # Obtener citas del día
        citas_dia = Citas.objects.filter(
            dia_cit=fecha,
            estado_cita__in=["Aceptada", "Sin confirmar", "Realizada"],
            citas_estado=True
        )

        horas_ocupadas = citas_dia.values_list("id_hora_id", flat=True)
        lista_horas = modelsAdministrador.Horas.objects.filter(horas_estado=True).exclude(id_hora__in=horas_ocupadas)
        lista_lugares = modelsAdministrador.Lugares.objects.filter(lugares_estado=True)
        lista_pacientes = modelsAdministrador.Pacientes.objects.filter(
            pacientes_estado=True, tipo_usuario='Particular'
        )
        lista_profesionales = modelsAdministrador.Profesional.objects.filter(estado_prof=True)
        lista_servicios = modelsAdministrador.Servicio.objects.filter(servicio_estado=True)

        return render(request, 'citas.html', {
            'form': formCitas,
            'listaHoras': lista_horas,
            'listaLugares': lista_lugares,
            'listaPacientes': lista_pacientes,
            'listaServicios': lista_servicios,
            'listaProfesionales': lista_profesionales,
            'fecha': fecha
        })

    elif request.method == 'POST':
        formCitas = FormCitas(request.POST)
        
        print(request.POST)
        
        # Validar formulario
        if not formCitas.is_valid():
            # Reconsultar las listas para pasarlas al template
            citas_dia = Citas.objects.filter(
                dia_cit=formCitas.cleaned_data.get('dia_cit'),
                estado_cita__in=["Aceptada", "Sin confirmar", "Realizada"],
                citas_estado=True
            )

            horas_ocupadas = citas_dia.values_list("id_hora_id", flat=True)
            lista_horas = modelsAdministrador.Horas.objects.filter(horas_estado=True).exclude(id_hora__in=horas_ocupadas)
            lista_lugares = modelsAdministrador.Lugares.objects.filter(lugares_estado=True)
            lista_pacientes = modelsAdministrador.Pacientes.objects.filter(
                pacientes_estado=True, tipo_usuario='Particular'
            )
            lista_profesionales = modelsAdministrador.Profesional.objects.filter(estado_prof=True)
            lista_servicios = modelsAdministrador.Servicio.objects.filter(servicio_estado=True)

            return render(request, 'citas.html', {
                'form': formCitas,
                'listaHoras': lista_horas,
                'listaLugares': lista_lugares,
                'listaPacientes': lista_pacientes,
                'listaServicios': lista_servicios,
                'listaProfesionales': lista_profesionales,
                'fecha': formCitas.cleaned_data.get('dia_cit')
            })
        
        # Obtener los datos del formulario
        id_servicio = formCitas.cleaned_data.get('id_servicio')
        id_prof = formCitas.cleaned_data.get('id_prof')
        paciente_id = formCitas.cleaned_data.get('id_pac')
        id_lugar = formCitas.cleaned_data.get('id_lugar') 
        id_usuario = formCitas.cleaned_data.get('id_usu') 

        print(f"request.user: {request.user}")
        print(f"request.user.id: {request.user.paciente_id}")

        # Validación de servicio y profesional
        if not id_servicio or not id_prof:
            error = "Servicio o profesional no seleccionados"
            messages.error(request, error)
            return render(request, 'citas.html', {
                'form': formCitas,
                'listaHoras': lista_horas,
                'listaLugares': lista_lugares,
                'listaPacientes': lista_pacientes,
                'listaServicios': lista_servicios,
                'listaProfesionales': lista_profesionales,
                'fecha': fecha,
                'error': error
            })

        try:
            if isinstance(id_usuario, int):
                instance_User = modelsEntrarSistema.CrearCuenta.objects.get(id=id_usuario)
            else:  # Si ya tienes el objeto Servicio, solo asigna
                instance_User = id_usuario  # id_servicio ya es un objeto Servicio
            
            instance_Hora = modelsAdministrador.Horas.objects.get(id_hora=request.POST['id_hora'])

            if isinstance(id_servicio, int):  # Verifica que id_servicio sea un identificador numérico
                instance_Servicio = modelsAdministrador.Servicio.objects.get(id_servicio=id_servicio)
            else:  # Si ya tienes el objeto Servicio, solo asigna
                instance_Servicio = id_servicio  # id_servicio ya es un objeto Servicio

            if isinstance(id_prof, int):  # Verifica que id_prof sea un identificador numérico
                instance_Profesional = modelsAdministrador.Profesional.objects.get(id_prof=id_prof)
            else:  # Si ya tienes el objeto Profesional, solo asigna
                instance_Profesional = id_prof  # id_prof ya es un objeto Profesional

            if isinstance(id_lugar, int):  # Verifica que id_lugar sea un identificador numérico
                instance_Lugar = modelsAdministrador.Lugares.objects.get(id_lugar=id_lugar)
            else:  # Si ya tienes el objeto Lugar, solo asigna
                instance_Lugar = id_lugar  # id_lugar ya es un objeto Lugar
                
            if isinstance(paciente_id, int):
                instance_paciente = modelsEntrarSistema.CrearCuenta.objects.get(id=paciente_id)
            else: 
                 instance_paciente = paciente_id

            print(f"Usuario: {instance_User}")
            print(f"Hora: {instance_Hora}")
            print(f"Servicio: {instance_Servicio}")
            print(f"Profesional: {instance_Profesional}")
            print(f"Lugar: {instance_Lugar}")

        except ObjectDoesNotExist as e:
            error = f"Datos inválidos: {str(e)}"
            messages.error(request, error)
            return render(request, 'citas.html', {
                'form': formCitas,
                'listaHoras': lista_horas,
                'listaLugares': lista_lugares,
                'listaPacientes': lista_pacientes,
                'listaServicios': lista_servicios,
                'listaProfesionales': lista_profesionales,
                'fecha': fecha,
                'error': error
            })

        # Crear cita
        id_cita = Citas(
            id_usu=instance_User,
            id_lugar=instance_Lugar,
            id_hora=instance_Hora,
            id_pac=instance_paciente,
            id_servicio=instance_Servicio,
            id_prof=instance_Profesional,
            dia_cit=formCitas.cleaned_data['dia_cit'],
            nota_cit=formCitas.cleaned_data['nota_cit'],
            estado_cita='Sin confirmar'
        )

        # Guardar la cita
        id_cita.save()
        # Mostrar un mensaje de éxito
        messages.success(request, "¡Cita solicitada exitosamente!")

        # Obtener el objeto Horas y formatear la hora de inicio (por ejemplo, 'HH:MM')
        horario = formCitas.cleaned_data['id_hora']
        inicio_hora = horario.inicio_hora.strftime('%H:%M')

        # Crear y guardar la notificación (puedes almacenar el mensaje completo o dejarlo para la plantilla)
        try:
            # Crear la notificación en la base de datos
            notificacion = modelsProgramador.Notificacion(
                usuario=instance_User,
                mensaje='',  # El mensaje se compone en el email a través de la plantilla
                asunto="Nueva cita solicitada"
            )
            notificacion.save()
            
            # Renderizar la plantilla con las variables dinámicas
            message = render_to_string('email_notificacion.html', {
                'usuario': notificacion.usuario,
                'profesional': instance_Profesional.nombre_prof,
                'dia_cit': formCitas.cleaned_data['dia_cit'],
                'inicio_hora': inicio_hora,
                'asunto': notificacion.asunto,
            })
            
            # Enviar el correo
            send_mail(
                notificacion.asunto,
                message,  # Contenido de texto (aunque se usa HTML)
                settings.EMAIL_HOST_USER,
                [notificacion.usuario.correo],
                fail_silently=False,
                html_message=message,  # Se envía como HTML
            )
        
        except Exception as e:
            # Aquí se captura cualquier error y se ignora para que no afecte al usuario.
            # Opcional: registra el error en el log para poder revisarlo después.
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Error enviando la notificación por correo: %s", e)
            # O simplemente "pasar" sin afectar la experiencia del usuario:
            pass
        
        return redirect('cita')
    
def get_lugares(request):
    # Obtenemos el ID del profesional
    id_prof = request.GET.get('id_prof')
    print(f"ID del profesional recibido: {id_prof}")

    if id_prof:
        try:
            # Buscar el profesional
            profesional = viewsAdministrador.Profesional.objects.get(id_prof=id_prof)

            # Obtener los lugares asociados a ese profesional 
            # donde lugares_estado sea True
            lugares = profesional.lugares.filter(lugares_estado=True).distinct()

            print(f"Lugares encontrados: {[lugar.nombre_lugar for lugar in lugares]}")

        except viewsAdministrador.Profesional.DoesNotExist:
            print("No existe el profesional con ese ID.")
            lugares = []
    else:
        print("No se proporcionó un ID de profesional.")
        lugares = []

    # Construir la respuesta en formato JSON
    data = [
        {'id_lugar': lugar.id_lugar, 'nombre_lugar': lugar.nombre_lugar}
        for lugar in lugares
    ]
    return JsonResponse(data, safe=False)

def get_profesionales(request):
    id_servicio = request.GET.get('id_servicio')
    
    # Filtrar profesionales asociados al servicio con el estado activo
    profesionales = modelsAdministrador.Profesional.objects.filter(
        servicios__id_servicio=id_servicio,  # Usar la relación ManyToMany
        estado_prof=True  # Verificar que el profesional esté activo
    )
    
    # Construir la respuesta
    data = [{'id_prof': p.id_prof, 'nombre_prof': p.nombre_prof} for p in profesionales]
    
    return JsonResponse(data, safe=False)


def get_horas(request):
    id_prof = request.GET.get('id_prof')  # ID del profesional
    dia_cit = request.GET.get('dia_cit')  # Fecha seleccionada

    print(f"ID del profesional recibido: {id_prof}")  
    print(f"Fecha seleccionada recibida: {dia_cit}")

    try:
        profesional = modelsAdministrador.Profesional.objects.get(id_prof=id_prof, estado_prof=True)
        print(f"Profesional encontrado: {profesional}")

        # Convertir la fecha string a objeto date
        fecha = parse_date(dia_cit)
        print(f"Fecha convertida: {fecha}")

        if not fecha:
            print("Error: Fecha inválida")
            return JsonResponse({'error': 'Fecha inválida'}, status=400)

        # Obtener la fecha/hora actual con zona horaria local
        now_local = timezone.localtime(timezone.now())
        hoy = now_local.date()
        hora_actual = now_local.time()

        # 1. Si la fecha está en el pasado, no mostramos nada
        if fecha < hoy:
            print("La fecha seleccionada está en el pasado. No se devuelven horas.")
            return JsonResponse([], safe=False)

        # Filtrar las horas ocupadas
        horas_ocupadas = Citas.objects.filter(
            id_prof=profesional,
            dia_cit=fecha,
            citas_estado=True,
            estado_cita__in=["Aceptada", "Sin confirmar", "Realizada"]
        ).values_list('id_hora', flat=True)

        print(f"Horas ocupadas: {list(horas_ocupadas)}")

        # Construir Query base de horas disponibles
        horas_disponibles = modelsAdministrador.Horas.objects.filter(
            id_prof=profesional,
            horas_estado=True,
            fecha_habilitada=fecha
        ).exclude(id_hora__in=horas_ocupadas)

        # 2. Si es el día de hoy, filtrar horas que estén en o después de la hora actual
        if fecha == hoy:
            # Por ejemplo, filtras por la hora de inicio >= ahora
            horas_disponibles = horas_disponibles.filter(inicio_hora__gte=hora_actual)

        # Construir la respuesta
        data = [
            {
                'id_hora': h.id_hora,
                'rango_horas': f"{h.inicio_hora.strftime('%H:%M')} a {h.final_hora.strftime('%H:%M')}"
            }
            for h in horas_disponibles
        ]
        print(f"Respuesta construida: {data}")
    except modelsAdministrador.Profesional.DoesNotExist:
        print("Profesional no encontrado o no activo")
        data = []

    return JsonResponse(data, safe=False)



def historial(request):

    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:

        if request.method == 'GET':

            lista_citas = modelsAdministrador.Consultorio.objects.filter(
                id_cit__id_usu=request.user.id, id_cit__citas_estado=True)

            return render(request, 'historial.html', {
                'listaCitas': lista_citas,
            })


def configuracion(request):

    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = viewsAdministrador.TipoRol(request)

    if not tipoRol.es_usuario:
        return redirect('cerrar')
    else:
        form = formsEntrarSistema.FormRegistrar()
        if request.method == 'GET':
            form = formsEntrarSistema.FormRegistrar()
            return render(request, 'configuracion.html', {
                'form': form
            })
        else:

            idUser = modelsEntrarSistema.CrearCuenta.objects.get(
                id=request.user.id)

            if 'btnUsuario' in request.POST:

                if modelsEntrarSistema.CrearCuenta.objects.filter(username=request.POST['username']).exists():
                    HttpResponse(
                        "<script>alert('Ya existe ese usuario')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.username = request.POST['username']
                    idUser.save()

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el usuario por {request.POST['username']}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnCedula' in request.POST:
                if modelsEntrarSistema.CrearCuenta.objects.filter(cedula=request.POST['cedula']).exists():
                    HttpResponse(
                        "<script>alert('Ya se ha registrado esta cédula')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.cedula = request.POST['cedula']
                    idUser.save()
                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio la cedula, del usuario {request.user.id} .")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnTelefono' in request.POST:

                if not request.POST['numero']:
                    HttpResponse(
                        "<script>alert('Tiene que escribir un número telefónico')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.numero = request.POST['numero']
                    idUser.save()

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el numero de teléfono, del usuario {request.user.id} .")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnCorreo' in request.POST:

                if modelsEntrarSistema.CrearCuenta.objects.filter(correo=request.POST['correo']).exists():
                    HttpResponse(
                        "<script>alert('Ya existe este correo')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.correo = request.POST['correo']
                    idUser.save()
                    print(idUser.save())

                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio el correo electrónico por {request.user.id}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnContrasenna' in request.POST:

                if not request.POST['password1'] == request.POST['password2']:
                    HttpResponse(
                        "<script>alert('Las contraseñas deben ser iguales')</script>")

                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    idUser.set_password(request.POST['password1'])
                    idUser.save()
                    # Aqui ponemos el codigo del trigger -------

                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio la contraseña por {request.user.id}.")
                    Audi.save()

                    # fin de trigger ------

                    return render(request, 'configuracion.html', {
                        'form': form
                    })

            elif 'btnAll' in request.POST:
                if modelsEntrarSistema.CrearCuenta.objects.filter(correo=request.POST['correo']).exists() or modelsEntrarSistema.CrearCuenta.objects.filter(username=request.POST['username']).exists() or modelsEntrarSistema.CrearCuenta.objects.filter(cedula=request.POST['cedula']).exists():
                    HttpResponse(
                        "<script>alert('Los datos suministrados ya existen en el sistema, elija otros por favor.')</script>")
                    return render(request, 'configuracion.html', {
                        'form': form
                    })
                else:
                    if request.POST['password1'] == request.POST['password2']:

                        idUser.username = request.POST['username']
                        idUser.cedula = request.POST['cedula']
                        idUser.numero = request.POST['numero']
                        idUser.correo = request.POST['correo']
                        idUser.set_password(request.POST['password1'])
                        idUser.save()

                        # Aqui ponemos el codigo del trigger -------

                        Audi = modelsAdministrador.Auditoria(
                            descripcion_aut=f"Se modifico una 'cuenta' en la tabla *CrearCuenta*, se cambio todos los datos por {request.user.id}.")
                        Audi.save()

                        # fin de trigger ------

                        return render(request, 'configuracion.html', {
                            'form': form
                        })

                    else:
                        HttpResponse(
                            "<script>alert('Las contraseñas deben ser iguales')</script>")
                        return render(request, 'configuracion.html', {
                            'form': form
                        })

        return render(request, 'configuracion.html', {
            'form': form
        })


