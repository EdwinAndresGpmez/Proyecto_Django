from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from administrador.models import Pacientes

class ControladorCrearCuenta(BaseUserManager):
    def create_user(self, username, nombre, correo, nacionalidad, cedula, numero, password=None, **extra_fields):
        if not username:
            raise ValueError("Debe ingresar un username único")
        if not nombre:
            raise ValueError("Debe ingresar un nombre válido")
        if not correo:
            raise ValueError("Debe ingresar un correo válido")
        if not cedula:
            raise ValueError("Debe ingresar una cédula válida")
        if not numero:
            raise ValueError("Debe ingresar un número válido")

        extra_fields.setdefault('is_active', True)  # Valor por defecto para usuarios normales

        user = self.model(
            username=username,
            correo=self.normalize_email(correo),
            nombre=nombre,
            nacionalidad=nacionalidad,
            cedula=cedula,
            numero=numero,
            **extra_fields,  # Agrega los campos adicionales como is_staff, is_superuser, etc.
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nombre, correo, password, nacionalidad, cedula, numero, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        return self.create_user(username, nombre, correo, nacionalidad, cedula, numero, password, **extra_fields)


class CrearCuenta(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    correo = models.EmailField(max_length=255, unique=True)
    nacionalidad = models.CharField(max_length=20)
    cedula = models.CharField(max_length=255, unique=True)
    numero = models.CharField(max_length=255)
    
    paciente = models.OneToOneField(
        Pacientes,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Paciente asociado",
        db_column="paciente_id"
    )

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    usuario_estado = models.BooleanField(default=True, null=True)

    USERNAME_FIELD = 'cedula'  # LOGIN
    REQUIRED_FIELDS = ['username', 'nombre', 'correo', 'nacionalidad', 'numero']  # REGISTER

    objects = ControladorCrearCuenta()

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_Label):
        return True


class UsuarioRoles(models.Model):

    id_rol = models.AutoField(primary_key=True)
    id_usu = models.ForeignKey(
        CrearCuenta, null=True, blank=True, on_delete=models.CASCADE, related_name='roles')
    es_usuario = models.BooleanField(default=True)
    es_administrador = models.BooleanField(default=False)
    es_programador = models.BooleanField(default=False)
