from .CuentaNoEncontradaException import CuentaNoEncontradaException
from .PermisoDenegadoException import PermisoDenegadoException
from .RolInvalidoException import RolInvalidoException
from .RolUsuario import RolUsuario


class ServicioAdministracionUsuarios:
    def __init__(self, repositorio, servicio_tokens):
        self._repositorio = repositorio
        self._servicio_tokens = servicio_tokens

    def listar_usuarios(self, token):
        self._validar_administrador(token)
        return self._repositorio.listar()

    def cambiar_rol(self, token, cuenta_id, nuevo_rol):
        administrador = self._validar_administrador(token)
        if nuevo_rol not in RolUsuario.values:
            raise RolInvalidoException("El rol debe ser USUARIO o ADMINISTRADOR.")
        cuenta = self._repositorio.buscar_por_id(cuenta_id)
        if cuenta is None:
            raise CuentaNoEncontradaException("La cuenta indicada no existe.")
        if cuenta.pk == administrador.pk and nuevo_rol != RolUsuario.ADMINISTRADOR:
            raise PermisoDenegadoException("No puedes quitarte tu propio rol de administrador.")
        cuenta.rol = nuevo_rol
        self._repositorio.guardar(cuenta)
        return cuenta

    def _validar_administrador(self, token):
        cuenta = self._servicio_tokens.obtener_cuenta(token)
        if cuenta.rol != RolUsuario.ADMINISTRADOR:
            raise PermisoDenegadoException("Esta opción es solo para administradores.")
        return cuenta
