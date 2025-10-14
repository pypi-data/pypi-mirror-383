from abc import ABC, abstractmethod
from typing import Optional

class transform_data(ABC):
    @abstractmethod
    def transform_data(self, url: str) -> Optional[str]:
        """Transforma datos y retorna la ruta del archivo procesado, o None si falla"""
        pass

class load_data(ABC):
    @abstractmethod
    def load_data(self, url: str) -> bool:
        """Carga datos y retorna True si fue exitoso, False si falló"""
        pass