from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
# from django.contrib.auth.hashers import make_password, check_password
from .forms import FormRegistrar, FormIniciar
from .models import UsuarioRoles
from administrador import views as modelsAdministrador
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()
# Create your views here.
def iniciarSesion(request):
    if request.method == "POST":
        form = FormIniciar(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data.get("cedula")
            password = form.cleaned_data.get("password")

            # Autenticar usuario, usando 'username=cedula' porque en tu modelo:
            # USERNAME_FIELD = 'cedula'
            user = authenticate(request, username=cedula, password=password)
            if user:
                # 1. Asociar el paciente si existe
                try:
                    paciente = modelsAdministrador.Pacientes.objects.get(num_doc=cedula)
                    if not user.paciente:
                        user.paciente = paciente
                        user.save()
                        messages.success(request, "Se actualizó su cuenta con el paciente asociado.")
                except modelsAdministrador.Pacientes.DoesNotExist:
                    messages.warning(
                        request,
                        "No tiene un paciente asociado. Comuníquese con la Clínica para activarse como paciente y poder solicitar citas."
                    )

                # 2. Verificar si el usuario ya tiene rol
                if not UsuarioRoles.objects.filter(id_usu=user).exists():
                    # Crear un rol por defecto
                    nuevo_rol = UsuarioRoles(
                        id_usu=user,
                        es_usuario=True,        # O los valores que consideres
                        es_administrador=False,
                        es_programador=False
                    )
                    nuevo_rol.save()

                    # 2.1. Guardar registro de auditoría
                    modelsAdministrador.Auditoria.objects.create(
                        descripcion_aut=(
                            f"Se creó un 'rol' en la tabla *UsuarioRoles*, "
                            f"con permisos de usuario ({nuevo_rol.es_usuario}), "
                            f"ID rol: {nuevo_rol.pk}, creado por el usuario: {user.id}"
                        )
                    )
                    messages.success(request, "Se creó un rol por defecto para su cuenta.")

                # 3. Finalmente, iniciar sesión
                login(request, user)
                return redirect('inicio')  # Ajusta la URL del redirect
            else:
                messages.error(request, "Credenciales inválidas.")
        else:
            messages.error(request, "Formulario inválido. Verifique los datos ingresados.")
    else:
        form = FormIniciar()

    return render(request, 'entrar.html', {'form': form})

def Registrarse(request):
    # 1. Verificar si el usuario ya inició sesión:
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'GET':
        # 2. Mostrar el formulario vacío
        form = FormRegistrar()
        return render(request, 'registrar.html', {'form': form})
    else:
        # 3. Procesar la información del formulario (POST)
        form = FormRegistrar(request.POST)
        if form.is_valid():
            id_crear = form.save()

            # 4. Guardar en Auditoría
            Audi = modelsAdministrador.Auditoria(
                descripcion_aut=(
                    f"Se creó una 'cuenta' en la tabla *CrearCuenta*, "
                    f"con el nombre {id_crear.nombre}, usuario {id_crear.username} "
                    f"y la cédula {id_crear.cedula}, creado por el usuario: {request.user.id}."
                )
            )
            Audi.save()

            # 5. Redireccionar al inicio de sesión
            return redirect('iniciarSesion')
        else:
            # 6. El formulario es inválido: podrías mostrar mensajes de error
            #    o simplemente recargar la página con los errores
            print("Formulario de registro inválido.")
            # Con Django Messages podrías hacer:
            # messages.error(request, "Hay errores en el formulario. Por favor revisa los campos.")
    
    return render(request, 'registrar.html', {'form': form})



def cerrarSesion(request):
    logout(request)
    return redirect('informacion_invitado')
    # return render(request, 'cerrar.html')
