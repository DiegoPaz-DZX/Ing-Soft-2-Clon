from abc import ABC, abstractmethod


class CifradorTexto(ABC):
    @abstractmethod
    def cifrar(self, texto):
        pass

    @abstractmethod
    def descifrar(self, texto_cifrado):
        pass
