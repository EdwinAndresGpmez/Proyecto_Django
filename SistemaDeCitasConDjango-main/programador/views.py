from django.shortcuts import render, redirect, get_object_or_404
from administrador import views as administradorViews
from administrador import models as administradorModels
from entrarSistema import models as entrarSistemaModels
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Notificacion
from .forms import NotificacionForm
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from twilio.rest import Client
# Create your views here.


def inicio_programador(request):
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = administradorViews.TipoRol(request)

    if not tipoRol.es_programador:
        return redirect('inicio')

    if request.method == 'GET':

        lista_auditoria = administradorModels.Auditoria.objects.all().order_by('-id_aut')
        listaRoles = entrarSistemaModels.UsuarioRoles.objects.filter(
            id_usu=request.user.id)

        return render(request, 'inicio_progr.html', {
            'auditorias': lista_auditoria,
            'listaRoles': listaRoles
        })


def roles_programador(request):
    # Si ya tiene sesión no le abre esta página
    user = request.user
    if not user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('iniciarSesion')

    tipoRol = administradorViews.TipoRol(request)

    if not tipoRol.es_programador:
        return redirect('inicio')

    if request.method == 'GET':

        listaUsuarios = entrarSistemaModels.CrearCuenta.objects.all()

        listaUserRoles = entrarSistemaModels.UsuarioRoles.objects.filter(
            id_usu__in=listaUsuarios)

        listaRoles = entrarSistemaModels.UsuarioRoles.objects.filter(
            id_usu=request.user.id)

        return render(request, 'roles_progr.html', {
            'listaRoles': listaRoles,
            'listaUsuarios': listaUserRoles
        })
    else:

        listaUsuarios = entrarSistemaModels.CrearCuenta.objects.all()

        listaUserRoles = entrarSistemaModels.UsuarioRoles.objects.filter(
            id_usu__in=listaUsuarios)

        listaRoles = entrarSistemaModels.UsuarioRoles.objects.filter(
            id_usu=request.user.id)

        print(request.POST)
        if 'option1' in request.POST:
            rol = entrarSistemaModels.UsuarioRoles.objects.get(
                id_usu=request.user.id)
            rol.es_usuario = True
            rol.save()
            print("1")
        if 'option2' in request.POST:
            rol = entrarSistemaModels.UsuarioRoles.objects.get(
                id_usu=request.user.id)
            rol.es_administrador = True
            rol.save()
            print("2")
        else:
            rol = entrarSistemaModels.UsuarioRoles.objects.get(
                id_usu=request.user.id)
            rol.es_administrador = False
            rol.save()
            print("2")

        if 'option3' in request.POST:
            rol = entrarSistemaModels.UsuarioRoles.objects.get(
                id_usu=request.user.id)
            rol.es_programador = True
            rol.save()
            print("3")
        else:
            rol = entrarSistemaModels.UsuarioRoles.objects.get(
                id_usu=request.user.id)
            rol.es_programador = False
            rol.save()
            print("3")

    return render(request, 'roles_progr.html', {
        'listaRoles': listaRoles,
        'listaUsuarios': listaUserRoles
    })


@login_required
def crear_notificacion(request):
    if request.method == 'POST':
        form = NotificacionForm(request.POST)
        if form.is_valid():
            # Guardar la notificación en la base de datos
            notificacion = form.save()

            # Renderizar el contenido del correo usando la plantilla 'email_notificacion.html'
            message = render_to_string('email_notificacion.html', {
                'usuario': notificacion.usuario,
                'mensaje': notificacion.mensaje,
                'asunto': notificacion.asunto,
            })

            # Enviar el correo con el cuerpo en formato HTML
            send_mail(
                notificacion.asunto,
                message,  # El mensaje será el HTML renderizado
                settings.EMAIL_HOST_USER,  # Correo del remitente configurado en settings.py
                [notificacion.usuario.correo],  # Correo del destinatario
                fail_silently=False,
                html_message=message,  # Usamos el parámetro 'html_message' para enviar HTML
            )

            # Redirigir a la lista de notificaciones o alguna página después de enviar el correo
            return redirect('lista_notificaciones')
    else:
        form = NotificacionForm()
    return render(request, 'crear_notificacion.html', {'form': form})

@login_required
def lista_notificaciones(request):
    # Obtener todas las notificaciones del usuario
    notificaciones = Notificacion.objects.filter(usuario=request.user)

    # Marcar las notificaciones como leídas si no lo están
    notificaciones_no_leidas = notificaciones.filter(leida=False)
    notificaciones_no_leidas.update(leida=True)

    return render(request, 'lista_notificaciones.html', {'notificaciones': notificaciones})

@login_required
def enviar_notificacion_whatsapp(request):
    if request.method == 'POST':
        form = NotificacionForm(request.POST)
        if form.is_valid():
            # Guardar la notificación en la base de datos
            notificacion = form.save()

            # Configuración de Twilio
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            twilio_number = settings.TWILIO_PHONE_NUMBER  # Número del sandbox
            client = Client(account_sid, auth_token)

            try:
                # Enviar mensaje por WhatsApp
                client.messages.create(
                    from_=f'whatsapp:{twilio_number}',
                    to=f'whatsapp:{notificacion.usuario.numero}',  # Asegúrate de tener el campo `telefono` en el modelo Usuario
                    body=f"📢 *{notificacion.asunto}*\n\n{notificacion.mensaje}",
                )
                messages.success(request, "Notificación enviada correctamente por WhatsApp.")
            except Exception as e:
                messages.error(request, f"No se pudo enviar la notificación: {str(e)}")

            # Redirigir a una lista de notificaciones o alguna página específica
            return redirect('enviar_notificacion_whatsapp')
    else:
        form = NotificacionForm()
    return render(request, 'enviar_notificacion_whatsapp.html', {'form': form})