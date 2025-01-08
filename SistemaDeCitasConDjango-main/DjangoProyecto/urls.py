"""
URL configuration for DjangoProyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from invitado import views as invitado_views
from entrarSistema import views as entrarSistema_views
from usuario import views as usuario_views
from administrador import views as administrador_views
from programador import views as programador_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", invitado_views.informacion_invitado, name="informacion_invitado"),
    path("contacto/", invitado_views.contacto_invitado, name="contacto_invitado"),
    path("entrar/", entrarSistema_views.iniciarSesion, name="iniciarSesion"),
    path("registrar/", entrarSistema_views.Registrarse, name="registrarse"),
    path("inicio/", usuario_views.inicio, name="inicio"),
    path("cita/", usuario_views.cita, name="cita"),
    path(
        "cancelar-cita/<int:id_cit>/", usuario_views.cancelarCita, name="cancelarCita"
    ),
    path("historial/", usuario_views.historial, name="historial"),
    path("configuracion/", usuario_views.configuracion, name="configuracion"),
    path("cerrar/", entrarSistema_views.cerrarSesion, name="cerrar"),
    path("inicio_admin/", administrador_views.inicioAdmin, name="inicioAdmin"),
    path(
        "lista_pacientes/", administrador_views.lista_pacientes, name="lista_pacientes"
    ),
    path("consultorio/", administrador_views.consultorio, name="consultorio"),
    path(
        "consultorio_cita/",
        administrador_views.consultorio_cita,
        name="consultorio_cita",
    ),
    path("citas_admin/", administrador_views.citas_admin, name="citas_admin"),
    # deleteHora
    path(
        "deleteHora/<int:id_hora>/",
        administrador_views.eliminar_horario,
        name="eliminar_horario",
    ),
    path(
        "updateHora/<int:id_hora>/",
        administrador_views.editar_horario,
        name="editar_horario",
    ),
    path("cfg_admin/", administrador_views.cfg_admin, name="configuracion_admin"),
    path(
        "inicio_programador/",
        programador_views.inicio_programador,
        name="inicio_programador",
    ),
    path(
        "roles_programador/",
        programador_views.roles_programador,
        name="roles_programador",
    ),
    # PDF
    path("pdf_citas/", administrador_views.pdfCitas, name="pdf_citas"),
    path(
        "editar-lugar/<int:id_lugar>/",
        administrador_views.editar_lugar,
        name="editar_lugar",
    ),
    path(
        "eliminar-lugar/<int:id_lugar>/",
        administrador_views.eliminar_lugar,
        name="eliminar_lugar",
    ),
    path(
        "lista_profesionales/",
        administrador_views.lista_profesionales,
        name="lista_profesionales",
    ),
    path(
        "editar_profesional/<int:id_prof>/",
        administrador_views.editar_profesional,
        name="editar_profesional",
    ),
    path(
        "eliminar_profesional/<int:id_prof>/",
        administrador_views.eliminar_profesional,
        name="eliminar_profesional",
    ),
    path("lista_lugar/", administrador_views.lista_lugar, name="lista_lugar"),
    path("lista_horario/", administrador_views.lista_horario, name="lista_horario"),
    path(
        "eliminar_paciente/<int:id_pac>/",
        administrador_views.eliminar_paciente,
        name="eliminar_paciente",
    ),
    path(
        "editar_paciente/<int:id_pac>/",
        administrador_views.editar_paciente,
        name="editar_paciente",
    ),
    path(
        "lista_servicios/", administrador_views.lista_servicios, name="lista_servicios"
    ),
    path(
        "eliminar_servicios/<int:id_servicio>/",
        administrador_views.eliminar_servicios,
        name="eliminar_servicios",
    ),
    path(
        "editar_servicios/<int:id_servicio>/",
        administrador_views.editar_servicios,
        name="editar_servicios",
    ),
    path(
        "get_profesionales/", usuario_views.get_profesionales, name="get_profesionales"
    ),
    path("get_horas/", usuario_views.get_horas, name="get_horas"),
    path("get_lugares/", usuario_views.get_lugares, name="get_lugares"),
    path("horarios/", administrador_views.lista_horario, name="lista_horario"),
    path("cargar_horario/", administrador_views.cargar_horario, name="cargar_horario"),
     path('crear_notificacion/', programador_views.crear_notificacion, name='crear_notificacion'),
    path('lista_notificaciones/', programador_views.lista_notificaciones, name='lista_notificaciones'),
    path('enviar_notificacion_whatsapp/', programador_views.enviar_notificacion_whatsapp, name='enviar_notificacion_whatsapp'),
   path('reportes/', administrador_views.reportes_list, name='reportes_list'),
    path('reportes/<str:report_type>/', administrador_views.generate_report, name='generate_report'),
]
