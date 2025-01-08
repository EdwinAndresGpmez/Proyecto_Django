from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
# from django.contrib.auth.hashers import make_password, check_password
from .forms import FormRegistrar, FormIniciar
from .models import UsuarioRoles
from administrador import views as modelsAdministrador


# Create your views here.


def iniciarSesion(request):

    # Si ya tiene sesión, redirigir a la página de inicio
    user = request.user
    if user.is_authenticated:
        return redirect('inicio')

    if request.method == 'GET':
        # Si la petición es GET, mostrar el formulario de inicio de sesión vacío
        form = FormIniciar()

        return render(request, 'entrar.html', {
            'form': form,
        })
    else:
        # Si la petición es POST, procesar el formulario
        form = FormIniciar(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']  # Usamos cleaned_data, no request.POST directamente
            password = form.cleaned_data['password']

            # Autenticamos al usuario con la cédula y la contraseña
            cuenta = authenticate(request, cedula=cedula, password=password)

            if cuenta is not None:
                login(request, cuenta)

                # Verificamos si el usuario tiene roles asignados
                if not UsuarioRoles.objects.filter(id_usu=request.user).exists():
                    # Si no tiene roles, creamos un nuevo rol para el usuario
                    roles = UsuarioRoles(id_usu=request.user)
                    roles.save()

                    # Auditoría: Registramos la creación de un nuevo rol
                    Audi = modelsAdministrador.Auditoria(
                        descripcion_aut=f"Se creó un 'rol' en la tabla *UsuarioRoles*, obteniendo permisos de usuario ({roles.es_usuario}), con el id {roles.pk}, creado por el usuario: {request.user.id},")
                    Audi.save()

                # Redirigimos al inicio si la autenticación fue exitosa
                return redirect('inicio')
            else:
                # Si no hay una cuenta con la cédula y contraseña proporcionados, mostramos un error
                form.add_error(None, "Los datos suministrados no existen o son incorrectos.")
        else:
            # Si el formulario no es válido, puedes manejar los errores si es necesario
            print("Formulario no válido")

    # Retornamos el formulario de nuevo con los errores si los hubo
    return render(request, 'entrar.html', {
        'form': form,
    })

def Registrarse(request):

    # Si ya tiene sesión no le abre esta página
    user = request.user
    if user.is_authenticated:
        # HttpResponse('<script>alert("funcionó");</script>')
        return redirect('inicio')

    if request.method == 'GET':
        form = FormRegistrar()
        return render(request, 'registrar.html', {
            'form': form
        })
    else:
        form = FormRegistrar(request.POST)
        if form.is_valid():

            print(type(form))
            id_crear = form.save()

            # Aqui ponemos el codigo del trigger -------

            Audi = modelsAdministrador.Auditoria(
                descripcion_aut=f"Se creó una 'cuenta' en la tabla *CrearCuenta*, con el nombre {id_crear.nombre}, usuario {id_crear.username} y la cédula {id_crear.cedula}, creado por el usuario: {request.user.id},")
            Audi.save()

            # fin de trigger ------
            return redirect('iniciarSesion')
        else:
            print("")

    return render(request, 'registrar.html', {
        'form': form,
    })


def cerrarSesion(request):
    logout(request)
    return redirect('informacion_invitado')
    # return render(request, 'cerrar.html')
