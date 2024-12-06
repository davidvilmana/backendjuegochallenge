from modifiers import Product, Project, Resource
from efficiency import Efficiency
from event import Event

# Función para cargar eficiencias desde un archivo
def load_efficiencies(path):   # Diccionario que almacenará las eficiencias
    efficiencies_dict = dict()
    with open(path) as f:
        content = f.read().splitlines()  # Lee el archivo línea por línea
        for line in content:
            parts = line.split("%%%") # Divide la línea en partes por "%%%" (sección de modificadores)
            name_and_products = parts[0].split(";")  # Obtiene la primera parte que incluye ID, nombre y productos
            idx, name = name_and_products[0:2]  # Asigna ID y nombre de la eficiencia
            modifiers_products = name_and_products[2:]  # Obtiene los productos que modifican esta eficiencia
            modifiers_products = [idx for idx in modifiers_products if len(idx) != 0] # Filtra elementos vacíos

            modifiers_projects = parts[1].split(";") # Obtiene los proyectos que modifican la eficiencia
            modifiers_projects = [idx for idx in modifiers_projects if len(idx) != 0]

            modifiers_resources = parts[2].split(";")  # Obtiene los recursos que modifican la eficiencia
            modifiers_resources = [idx for idx in modifiers_resources if len(idx) != 0]
            # Crea una instancia de Efficiency y la agrega al diccionario
            efficiencies_dict[idx] = Efficiency(
                name=name, ID=idx, points=0, modifiable_by_products=modifiers_products,
                modifiable_by_projects=modifiers_projects, modifiable_by_resources=modifiers_resources
            )
    return efficiencies_dict  # Retorna el diccionario con las eficiencias cargadas

# Función para cargar productos desde un archivo
def load_products(path):
    products_dict = dict()   # Diccionario que almacenará los productos
    with open(path) as f:
        content = f.read().splitlines()  # Lee el archivo línea por línea
        for line in content:
            line_content = line.split(";") # Divide la línea por ";"
            idx, name, cost = line_content[0:3]  # Asigna el ID, nombre y costo del producto
            requirements = line_content[3:]  # Obtiene la lista de requisitos del producto
            requirements = [idx for idx in requirements if len(idx) != 0]  # Filtra elementos vacíos
             # Crea una instancia de Product y la agrega al diccionario
            products_dict[idx] = Product(
                name=name, cost=int(cost), ID=idx, requirements=requirements, purchased_on=None
            )
    return products_dict  # Retorna el diccionario con los productos cargados

# Función para cargar proyectos desde un archivo
def load_projects(path):
    projects_dict = dict()  # Diccionario que almacenará los proyectos
    with open(path) as f:
        content = f.read().splitlines()  # Lee el archivo línea por línea
        for line in content:
            line_content = line.split(";")  # Divide la línea por ";"
            idx, name, cost = line_content[0:3]  # Asigna el ID, nombre y costo del proyecto
            delivered_products = line_content[3:]  # Obtiene la lista de productos entregados por el proyecto
            delivered_products = [idx for idx in delivered_products if len(idx) != 0]  # Filtra elementos vacíos
            # Crea una instancia de Project y la agrega al diccionario
            projects_dict[idx] = Project(
                name=name, cost=int(cost), ID=idx, delivered_products=delivered_products, start_datum=0,
                purchased_on=None
            )
    return projects_dict # Retorna el diccionario con los proyectos cargados

# Función para cargar recursos desde un archivo
def load_resources(path):
    resources_dict = dict() # Diccionario que almacenará los recursos
    with open(path) as f:
        content = f.read().splitlines() # Lee el archivo línea por línea
        for line in content:
            line_content = line.split(";")  # Divide la línea por ";"
            idx, name, cost, monthly_salary = line_content[0:4]  # Asigna el ID, nombre, costo y salario del recurso
            developed_products = line_content[4:]  # Obtiene la lista de productos desarrollados por el recurso
            developed_products = [idx for idx in developed_products if len(idx) != 0]  # Filtra elementos vacíos
             # Crea una instancia de Resource y la agrega al diccionario
            resources_dict[idx] = Resource(
                name=name, cost=int(cost), ID=idx, developed_products=developed_products,
                monthly_salary=int(monthly_salary), purchased_on=None
            )
    return resources_dict # Retorna el diccionario con los recursos cargados

# Función para cargar eventos desde un archivo
def load_events(path):
    events_dict = dict()  # Diccionario que almacenará los eventos
    with open(path) as f:
        content = f.read().splitlines()  # Lee el archivo línea por línea
        for line in content:
            line_content = line.split(";")  # Divide la línea por ";"
            idx, trimester, description = line_content[0:3]  # Asigna el ID, trimestre y descripción del evento
            trimester = int(trimester[-1])  # Convierte el trimestre en un entero (extrae el último dígito de "Q1", etc.)
            required_efficiencies = line_content[3:6]  # Lista de eficiencias requeridas para el evento
            result_success = line_content[6:8] or (0, 0)  # Resultado en caso de éxito, o valores predeterminados
            result_success = tuple(map(lambda x: int(x), result_success))  # Convierte a enteros los valores de éxito
            result_failure = line_content[8:10] or (0, 0) # Resultado en caso de fracaso, o valores predeterminados
            result_failure = tuple(map(lambda x: -int(x), result_failure)) # Convierte a enteros los valores de fracaso
            # Crea una instancia de Event y la agrega al diccionario
            events_dict[idx] = Event(
                description=description, appear_first_in_trimester=trimester, ID=idx,
                required_efficiencies=required_efficiencies,
                result_success=result_success, result_failure=result_failure, level=0
            )
    return events_dict  # Retorna el diccionario con los eventos cargados

# Función para cargar elementos de herencia desde un archivo
def load_legacy(path):
    legacy_list = []  # Lista que almacenará las opciones de herencia
    with open(path) as f:
        content = f.read().splitlines()  # Lee el archivo línea por línea
        for line in content: 
            legacy_list.append(line.split(";"))   # Agrega cada línea como una lista de elementos de herencia
    return legacy_list  # Retorna la lista de herencia
