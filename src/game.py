import random
from player import Player  # Importa la clase Player que maneja la lógica del jugador
from data_loader import load_products, load_projects, load_resources, load_efficiencies, load_events, load_legacy
from pathlib import Path  # Para trabajar con rutas de archivos
import numpy as np  # Para operaciones numéricas, incluidos lanzamientos de dados
import math
from copy import deepcopy  # Para hacer copias profundas de objetos (evita modificar los originales)
from operator import itemgetter  # Para obtener elementos específicos de estructuras de datos
import logging   # Para registrar mensajes de información
logging.basicConfig(level=logging.INFO)  # Configuración de nivel de registro de información

# Define el directorio de datos donde se almacenan los archivos del juego
DATA_DIR = Path().parent.resolve().parent.resolve().joinpath("data")

# Definición de la clase Contexto, que carga y almacena todos los datos necesarios para el juego
class Context:
    def __init__(self, data_dir):
        self.data_dir = data_dir  # Directorio donde se encuentran los datos
        self.PRODUCTS = None   # Almacena productos cargados
        self.PROJECTS = None    # Almacena proyectos cargados
        self. RESOURCES = None   # Almacena recursos cargados
        self. EFFICIENCIES = None   # Almacena eficiencias cargadas
        self.EVENTS = None   # Almacena eventos cargados
        self. LEGACY = None   # Almacena herencias cargadas
        self.load_data()   # Carga todos los datos desde los archivos
        self.board = self.load_bord()  # Carga el tablero de juego

 # Método que carga todos los archivos de datos y los almacena en los atributos de clase
    def load_data(self):
        data_dir = self.data_dir
        products_path = data_dir.joinpath("products.csv")
        projects_path = data_dir.joinpath("projects.csv")
        resources_path = data_dir.joinpath("resources.csv")
        efficiencies_path = data_dir.joinpath("efficiencies.csv")
        events_path = data_dir.joinpath("events.csv")
        legacy_path = data_dir.joinpath("legacy.csv")

        self.PRODUCTS = load_products(products_path) # Carga productos
        self.PROJECTS = load_projects(projects_path)  # Carga proyectos
        self.RESOURCES = load_resources(resources_path)  # Carga recursos
        self.EFFICIENCIES = load_efficiencies(efficiencies_path)  # Carga eficiencias
        self.EVENTS = load_events(events_path)  # Carga eventos
        self.LEGACY = load_legacy(legacy_path)   # Carga elementos de herencia

    def load_bord(self):
        board_path = self.data_dir.joinpath("board.csv")
        board = []
        with open(board_path) as f:
            content = f.read().splitlines()
            for line in content[1:]:  # Omite la primera línea (cabecera)
                board.append(line.split(";")[1:])  # Omite el nombre del mes
        return np.array(board, dtype=int)  # Convierte el tablero en un array numpy de enteros


# Inicialización del contexto y el jugador
context = Context(DATA_DIR)
player = Player(context=context, initial_budget=1000000)  # Crea un jugador con un presupuesto inicial
random.seed(0)  # Establece una semilla para obtener resultados aleatorios reproducibles
np.random.seed(0)  

# Ciclo principal del juego, continúa mientras el mes del jugador sea menor o igual a 13
while player.month <= 13:

   # Verifica si es el primer turno del mes
    if player.first_turn_in_month:

    #----- compra------
        input("Estás en el primer cambio de mes. Puedes comprar los modificadores que quieras.")#You are on the first turn of the month. You can buy the modifiers you like
        wanna_buy = True
        while wanna_buy:
            purchase = input("¿Qué te gustaría comprar? (producto, proyecto, recurso, nada)")#What would you like to buy? (product, project, resource, nothing)
            purchase = purchase.lower()
            if purchase == "nothing":
                wanna_buy = False  # Termina el ciclo de compra
            elif purchase == "producto":
                product_id = input("¿Qué producto te gustaría comprar?") #Which product would you like to buy?
                # TODO make this dummy proof (only integers are allowed)
                player.buy_product(str(product_id))
            elif purchase == "proyecto":
                project_id = input("¿Qué proyecto te gustaría comprar?") #Which project would you like to buy?
                player.buy_project(str(project_id))
            elif purchase == "recurso":
                resource_id = input("¿Qué recurso te gustaría contratar?") #Which resource would you like to hire?
                player.hire_resource(str(resource_id))
            else:
                input("Por favor seleccione producto, proyecto, recurso o nada") #Please select product, project, resource or nothing
                continue
    else:
        print("No estás en el primer turno de mes. No puedes comprar nada pero tienes que enfrentar desafíos.") #You are not in the first turn of the month. You can't buy anything but you have to face challenges


    # Cambia a false para indicar que ya no es el primer turno del mes
    player.first_turn_in_month = False
    # Muestra las eficiencias actuales del jugador
    player.display_efficiencies()
     # Lanzamiento de dados y movimiento
    throw = input(f"¿Listo para tirar los dados? Haga clic en cualquier cosa")#Ready to throw the dices? Click anything
    old_month = player.month  # Almacena el mes actual antes de actualizarlo
    dices, steps = player.throw_dices(5) # Lanza 5 dados
    player.actual_date += steps   # Actualiza la fecha del jugador sumando los pasos obtenidos
    field = context.board.reshape(-1)[player.actual_date] # Obtiene el valor del tablero correspondiente
    print(f"Tiraste los dados: {dices}, avanzando {steps} pasos.") #You threw the dices:/, moving forward / steps.
    print(f"En realidad estas en {player.actual_date % 30}-{player.month} y " #You are actually on/ and 
          f"Tener que tirar {field} dados para obtener el nivel de riesgo de tu evento") #have to throw /dices to get the level risk of your event

   # Verifica si ha comenzado un nuevo mes
    if old_month < player.month:
        player.first_turn_in_month = True
        player.pay_salaries()  # Paga los salarios de los recursos
        player.get_products_from_projects()  # Obtiene productos de proyectos completados
        player.get_products_from_resources() # Obtiene productos desarrollados por recursos
        print(f"Un nuevo mes ha comenzado. has pagado{player.salaries_to_pay} dólares en salarios") #A new month has begun. You have paid / dollars on salaries

     # Verifica si es sábado o domingo
    if player.actual_date % 7 in [6, 0]:
        print("Hoy es fin de semana, no está permitido aceptar ningún desafío.") #Today is weekend, it is not allowed to take any challenges
        continue  # Salta al siguiente ciclo, no se permite enfrentarse a desafíos en fines de semana

    # Toma un evento aleatorio en función del trimestre actual
    current_trimester = np.ceil(player.month / 3)
    possible_events = [
        event_id for event_id, event in context.EVENTS.items() if event.appear_first_in_trimester <= current_trimester
    ]
    random_event_id = random.choice(possible_events)  # Selecciona un evento aleatorio
    event = deepcopy(context.EVENTS.get(random_event_id))  # Copia profunda del evento
    take_event = input(f"Presione una tecla para obtener un evento aleatorio")#Press a key to get a random event
    print("Tomando evento aleatorio")#Taking random event
    print(event.description) # Muestra la descripción del evento

    # Determina el nivel de riesgo del evento
    throw = input(f"¿Listo para saber qué nivel de riesgo tiene tu evento? Presione cualquier tecla") #Ready to know which level of risk your event has? Press any key
    dices, risk_level = player.throw_dices(field)  # Lanza dados para determinar el nivel de riesgo
    print(f"tiraste los dados: {dices} ") #you threw the dices: 
    event.level = risk_level
    print(f"Con nivel de riesgo de {event.level}") #With risk level of 

    # Evalúa si el jugador puede superar el desafío del evento
    required_efficiencies_ids = event.required_efficiencies
    required_efficiencies = itemgetter(*required_efficiencies_ids)(player.efficiencies)
    max_efficiencies_point = max([eff.points for eff in required_efficiencies])

    print(f"Puede gestionar este evento con las siguientes eficiencias y sus puntos en ellas.")#You can manage this event with following efficiencies and your points on them
    for efficiency in required_efficiencies:
        print(f"{efficiency.name}: {efficiency.points}")

    # Verifica si las eficiencias son suficientes para manejar el evento
    if max_efficiencies_point >= event.level:
        print(f"¡Felicitaciones! Has gestionado este evento con éxito"#Congrats! You have managed this event successfully 
              f"victorioso{event.result_success[0]} puntos y {event.result_success[1]} dólares.") #winning /points and/dollars.
        player.apply_challenge_result(event.result_success)
    else:
        print(f"¡Unión Postal Universal! Sus eficiencias no fueron suficientes para este evento." #¡Unión Postal Universal! Sus eficiencias no fueron suficientes para este evento.
              f"tienes perdido {event.result_failure[0]} puntos y {event.result_failure[1]} dólares.")#You have lost /points and / dollars. 
        player.apply_challenge_result(event.result_failure)

    print(f"Su puntuación real es: {player.score} y el presupuesto es {player.budget}") #Your actual score is:/and budget is


