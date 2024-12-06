from copy import deepcopy # Para realizar copias profundas de objetos (se asegura de no modificar el original)
import numpy as np # Para generar números aleatorios
import random # Para hacer selecciones aleatorias de listas
from typing import Tuple # Para definir tipos de datos en anotaciones de función
import logging # Para manejo de logs, no usado en este código pero importado

# Definición de la clase Player, que representa a un jugador en el juego
class Player:
    def __init__(self, context=None, initial_budget=0):
         # Inicialización de atributos básicos
        self.context = context  # Contexto del juego (configuración y recursos disponibles)
        self.efficiencies = deepcopy(self.context.EFFICIENCIES)  # # Copia profunda de las eficiencias iniciales
        self.products = dict() # Productos adquiridos por el jugador
        self.projects = dict()  # Proyectos en los que el jugador está involucrado
        self.resources = dict()  # Recursos que el jugador ha contratado
        self.budget = initial_budget  # Presupuesto inicial del jugador
        self.score = 0   # Puntuación inicial del jugador
        self.salaries_to_pay = 0  # Sueldos a pagar por los recursos contratados
        self.actual_date = 0   # Fecha en días en el juego
        self._get_legacy()  # Obtiene productos heredados al inicio del juego
        self.first_turn_in_month = True # Para controlar si es el primer turno del mes

 # Propiedad que calcula el mes en el que se encuentra el jugador (1 mes = 30 días)
    @property
    def month(self):
        return (self.actual_date // 30) + 1
# Propiedad que devuelve los proyectos actuales terminados hasta el mes actual
    @property
    def current_projects(self):
        return [key for key, value in self.projects.items() if value.is_finished(self.month)]

 # Método que asigna productos al jugador como herencia al inicio del juego
    def _get_legacy(self):
        legacy_list = self.context.LEGACY  # Lista de posibles productos para heredar
        legacy_choice = random.choice(legacy_list)  # Selección aleatoria de una lista de herencia
        for item in legacy_choice:
            self._add_product(item)  # Agrega cada producto heredado al inventario del jugador
            print(f"Has heredado: {self.context.PRODUCTS.get(item).name}") #You have inherited: 
 # Método que verifica si el presupuesto del jugador es suficiente para una compra
    def budget_enough_for_buying(self, modifier):
        if self.budget < modifier.cost:
            print(f"No tienes suficiente presupuesto para comprar: {modifier.name}") #You dont have enough budget to buy: 
            return False

        return True
# Método que agrega un producto al inventario del jugador
    def _add_product(self, product_id):
        product = self.context.PRODUCTS.get(product_id, None)
        name = product.name
        if product_id in self.products.keys():
            print(f"Product {name} ya esta disponible") #is already available //print
            return
        purchased_product = deepcopy(product)
        purchased_product.purchased_on = self.month  # Se marca el mes en el que fue adquirido
        self.products[product_id] = purchased_product # Se agrega al inventario del jugador
        for efficiency in self.efficiencies.values():  # Actualiza eficiencias con el producto
            efficiency.update_by_product(product, self.products)

 # Método para verificar el número de compras del jugador en un mes
    def check_number_of_purchases(self, modifier_type):
        purchased_modifiers = None

        if modifier_type == "product":
            purchased_modifiers = {
                key: value for key, value in self.products.items() if value.purchased_on == self.month
            }
            if len(purchased_modifiers) >= 5:
                return False  # Limita a 5 productos comprados al mes
            else:
                return True
        elif modifier_type == "project":
            purchased_modifiers = {
                key: value for key, value in self.projects.items() if value.purchased_on == self.month
            }
        elif modifier_type == "resource":
            purchased_modifiers = {
                key: value for key, value in self.resources.items() if value.purchased_on == self.month
            }
        else:
            pass
        if len(purchased_modifiers) >= 1:
            return False
        return True
  # Método que permite comprar un producto
    def buy_product(self, product_id):
        if not self.check_number_of_purchases("product"):
            print("Ya has comprado 5 productos este mes, no puedes comprar más") #You have already purchased 5 products this month, you are not allowed to buy more
            return
        product = self.context.PRODUCTS.get(product_id, None)

        if self.budget_enough_for_buying(product):
            self._add_product(product_id)
            # Todo: print some message if the requirements for the product are not bought
            self.budget -= product.cost
    # Método que permite comprar un proyecto
    def buy_project(self, project_id):
        if len(self.current_projects) >= 3:
            print("No se le permite ejecutar más de 3 proyectos en paralelo") #You are note allowed to run more than 3 projects in parallel
            return
        if not self.check_number_of_purchases("project"):
            print("Ya compraste 1 proyecto este mes, no puedes comprar más")#You have already bought 1 project this month, you are not allowed to buy more
            return
        project = self.context.PROJECTS.get(project_id, None)
        name = project.name
        if project_id in self.projects.keys():
            print(f"Project {name} ya esta disponible")#is already available
            return
        if self.budget_enough_for_buying(project):
            bought_project = deepcopy(project)
            bought_project.purchased_on = self.month
            bought_project.start_datum = self.month + 1
            # Todo: check datum --> do you still have time to get the products
            self.projects[project_id] = bought_project
            self.budget -= project.cost
    # Método para contratar un recurso
    def hire_resource(self, resource_id):
        if not self.check_number_of_purchases("resource"):
            print("Ya has contratado 1 recurso este mes, no puedes comprar más")#You have already hired 1 resource this month, you are not allowed to buy more
            return
        resource = self.context.RESOURCES.get(resource_id, None)
        name = resource.name
        if resource_id in self.resources.keys():
            print(f"Resource {name} ya esta disponible")#is already available
            return
        if not self.budget_enough_for_buying(resource):
            return

        hired_resource = deepcopy(resource)
        hired_resource.purchased_on = self.month
        self.resources[resource_id] = hired_resource
        self.salaries_to_pay += hired_resource.monthly_salary
        self.budget -= resource.cost

 # Método para pagar los salarios de los recursos contratados
    def pay_salaries(self):
        self.budget -= self.salaries_to_pay
        # TODO: charge salaries after hiring (not in the first month)

  # Método para obtener productos de proyectos completados
    def get_products_from_projects(self):
        for project_id, project in self.projects.items():
            time_passed = self.month - project.start_datum
            if time_passed == project.project_length:
                delivered_products_ids = project.delivered_products
                for product_id in delivered_products_ids:
                    self._add_product(product_id)  # add products and its efficiencies

                for efficiency in self.efficiencies.values():
                    efficiency.update_by_project(project)  # add points to efficiency corresponding to the project
 # Método para obtener productos de los recursos contratados el mes pasado
    def get_products_from_resources(self):
        last_month = self.month - 1
        purchased_resources_last_month = [
            resource for resource in self.resources.values() if resource.purchased_on == last_month
        ]
        for resource in purchased_resources_last_month:
            for product_id in resource.developed_products:
                self._add_product(product_id)

            for efficiency in self.efficiencies.values():
                efficiency.update_by_resource(resource)
    # Método para simular el lanzamiento de dados
    def throw_dices(self, number):
        dices = np.random.randint(1, 6, size=number)
        return dices, dices.sum()
    
 # Método para verificar las eficiencias, actualmente sin implementar
    def check_efficiencies(self):
        pass

  # Método que aplica los resultados de un desafío, sumando puntos y dinero
    def apply_challenge_result(self, result: Tuple):
        points, money = result
        self.score += points
        self.budget += money
 # Método para mostrar una lista de modificadores
    def display_modifier(self, list_modifiers):
        for modifier in list_modifiers:
            print(f"{modifier.ID}: {modifier.name}")
            print(f"Comprado en: {modifier.purchased_on} para: {modifier.cost} dólares.") #Purchased on: / for: /  dollars.
            print("--------------------------------------------------------------------")
  # Método para mostrar las eficiencias actuales del jugador
    def display_efficiencies(self):
        print(f"Valor real de las eficiencias") #Actual value of efficiencies
        for efficiency in self.efficiencies.values():
            print(f"{efficiency.name}: {efficiency.points}")
   #metodo agredao 
    def get_efficiencies(self):
        """Devuelve las eficiencias en un formato adecuado para la API."""
        if isinstance(self.efficiencies, dict):
            return {key: eff.points for key, eff in self.efficiencies.items()}
        else:
            raise ValueError("Eficiencias no están en el formato esperado.")
    
