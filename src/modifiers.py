from dataclasses import dataclass  # Facilita la creación de clases de datos inmutables
from typing import List, Tuple, Any # Para anotar tipos de datos de listas, tuplas y cualquier tipo


# Clase base 'Modifier' que representa un modificador en el juego, con atributos comunes a productos, proyectos y recursos.
@dataclass
class Modifier:
    name: str  # Nombre del modificador
    cost: int  # Costo del modificador en unidades monetarias
    ID: int   # Identificador único del modificador
    purchased_on: int or None  # Mes en el que fue adquirido (None si no ha sido comprado)

# Clase 'Product' que hereda de 'Modifier', representando un producto específico que puede tener requisitos
@dataclass
class Product(Modifier):
    requirements: List  # Lista de requisitos que se deben cumplir para comprar o utilizar el producto

# Clase 'Project' que hereda de 'Modifier' y representa un proyecto que puede entregar productos al finalizar
@dataclass
class Project(Modifier):
    delivered_products: List   # Lista de productos entregados al finalizar el proyecto
    start_datum: Any = None  # Mes de inicio del proyecto (None si aún no ha comenzado)
    project_length: int = 3  #  # Duración del proyecto en meses, con un valor predeterminado de 3 meses
 # Método que verifica si el proyecto ha terminado, comparando el mes actual con la fecha de inicio y duración
    def is_finished(self, actual_month):
        if actual_month - self.project_length > self.start_datum:
              # Si el mes actual menos la duración del proyecto es mayor que el mes de inicio, el proyecto ha terminado
            return True
        return False

# Clase 'Resource' que hereda de 'Modifier', representando un recurso (p. ej., un empleado) con salario mensual
@dataclass
class Resource(Modifier):
    developed_products: List # Lista de productos que el recurso ha desarrollado
    monthly_salary: int   # Salario mensual del recurso
