from dataclasses import dataclass  # Facilita la creación de clases de datos inmutables
from typing import List, Tuple, Any  # Para definir tipos de datos
import numpy as np # Para operaciones numéricas, como el redondeo de puntos

# Clase Efficiency, que representa un tipo de eficiencia en el juego y cómo se modifica
@dataclass
class Efficiency:
    name: str  # Nombre de la eficiencia
    modifiable_by_products: List  # Lista de IDs de productos que pueden modificar esta eficiencia
    modifiable_by_projects: List  # Lista de IDs de proyectos que pueden modificar esta eficiencia
    modifiable_by_resources: List  # Lista de IDs de recursos que pueden modificar esta eficiencia
    points: int = None  # Puntos actuales de la eficiencia, inicialmente indefinidos
    ID: int = None # Identificador único de la eficiencia, opcional
    max_points: int = 36  # Máximo de puntos que puede alcanzar esta eficiencia

   # Propiedad que devuelve el número de productos que pueden modificar esta eficiencia
    @property
    def number_of_products_modifiers(self):
        return len(self.modifiable_by_products)
    
 # Propiedad que devuelve el número de proyectos que pueden modificar esta eficiencia (o None si no hay ninguno)
    @property
    def number_of_projects_modifiers(self):
        length = len(self.modifiable_by_projects)
        return length if length > 0 else None
 # Propiedad que devuelve el número de recursos que pueden modificar esta eficiencia (o None si no hay ninguno)
    @property
    def number_of_resources_modifiers(self):
        length = len(self.modifiable_by_resources)
        return length if length > 0 else None

    # Método que actualiza la eficiencia según un producto adquirido
    def update_by_product(self, product, purchased_products):
           # Verifica si el producto tiene un ID que puede modificar esta eficiencia
        if product.ID in self.modifiable_by_products:
              # Calcula los puntos obtenidos dividiendo el máximo de puntos por el número de productos que modifican esta eficiencia
            achieved_points = int(self.max_points / self.number_of_products_modifiers)
             # Define los requisitos necesarios para que el producto otorgue su beneficio completo 
            requirements_for_product = product.requirements
            # Key: length of the requirements for the product
            # Diccionario para determinar la cantidad de requisitos necesarios según la cantidad total de requisitos
            requirements_dict = {0: 0, 1: 1, 2: 2, 3: 2, 4: 3}
            number_of_requirements_needed = requirements_dict.get(len(requirements_for_product), 4)
             # Filtra los requisitos que el jugador ya posee
            purchased_requirements = [
                requirement for requirement in requirements_for_product if requirement in purchased_products
            ]
              # Si se han comprado los requisitos necesarios, se otorga el beneficio completo, de lo contrario, solo la mitad
            if len(purchased_requirements) >= number_of_requirements_needed:
                self.points += np.round(achieved_points, 0) # Suma los puntos completos
            else: 
                self.points += np.round(achieved_points / 2, 0)  # Suma la mitad de los puntos
    # Método que actualiza la eficiencia según un proyecto completado
    def update_by_project(self, project):
         # Verifica que haya proyectos que modifiquen esta eficiencia, de lo contrario, no hace nada
        if not self.number_of_projects_modifiers:
            return
         # Si el proyecto tiene un ID que puede modificar esta eficiencia, se calculan los puntos obtenidos
        if project.ID in self.modifiable_by_projects:
            achieved_points = int(self.max_points / self.number_of_projects_modifiers)
            self.points += np.round(achieved_points, 0) # Suma los puntos redondeados a la eficiencia

 # Método que actualiza la eficiencia según un recurso contratado
    def update_by_resource(self, resource):
         # Verifica que haya recursos que modifiquen esta eficiencia, de lo contrario, no hace nada
        if not self.number_of_projects_modifiers:
            return
          # Si el recurso tiene un ID que puede modificar esta eficiencia, se calculan los puntos obtenidos
        if resource.ID in self.modifiable_by_resources:
            achieved_points = int(self.max_points / self.number_of_resources_modifiers)
            self.points += np.round(achieved_points, 0) # Suma los puntos redondeados a la eficiencia
