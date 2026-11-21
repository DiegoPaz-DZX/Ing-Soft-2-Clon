from cryptography.fernet import Fernet

from .CifradorTexto import CifradorTexto


class CifradorFernet(CifradorTexto):
    def __init__(self, clave):
        self._fernet = Fernet(clave)

    def cifrar(self, texto):
        return self._fernet.encrypt(texto.encode("utf-8")).decode("utf-8")

    def descifrar(self, texto_cifrado):
        return self._fernet.decrypt(texto_cifrado.encode("utf-8")).decode("utf-8")
