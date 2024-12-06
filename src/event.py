from dataclasses import dataclass  # Facilita la creación de clases de datos inmutables
from typing import List, Tuple, Any   # Para definir tipos de datos en las anotaciones
from efficiency import Efficiency   # Importa la clase Efficiency, que probablemente maneja puntos de eficiencia


# Definición de la clase Event, que representa un evento en el juego
@dataclass
class Event:
    description: str   # Descripción del evento (explicación o narrativa del evento)
    appear_first_in_trimester: int  # Trimestre en el que este evento puede aparecer por primera vez
    required_efficiencies: List  # Lista de eficiencias requeridas para enfrentar el evento
    result_success: Tuple  # Resultado del evento en caso de éxito (por ejemplo, puntos ganados, dinero)
    result_failure: Tuple   # Resultado del evento en caso de fracaso (por ejemplo, puntos perdidos, dinero)
    ID: int = None # Identificador único del evento, opcional (inicialmente None)
    level: int = None # Nivel de riesgo del evento, opcional (inicialmente None)

