from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit , join_room, leave_room
import pymysql
import hashlib
from pathlib import Path
import random
import numpy as np
from copy import deepcopy
from player import Player
from data_loader import load_products, load_projects, load_resources, load_efficiencies, load_events, load_legacy
from operator import itemgetter  
import logging   
import csv

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")


DATA_DIR = Path().parent.resolve().parent.resolve().joinpath("data")
context = None
player = None

def conexion_db():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="david",
        db="challangegru9",
        cursorclass=pymysql.cursors.DictCursor
    )
# Función para encriptar la contraseña
def encriptar_contraseña(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_game():
    global context, player
    context = Context(DATA_DIR)
    player = Player(context=context, initial_budget=1000000)
    random.seed(0)
    np.random.seed(0)


class Context:

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.PRODUCTS = None
        self.PROJECTS = None
        self.RESOURCES = None
        self.EFFICIENCIES = None
        self.EVENTS = None
        self.LEGACY = None
        self.load_data()
        self.board = self.load_board()

    def load_data(self):
        data_dir = self.data_dir
        self.PRODUCTS = load_products(data_dir.joinpath("products.csv"))
        self.PROJECTS = load_projects(data_dir.joinpath("projects.csv"))
        self.RESOURCES = load_resources(data_dir.joinpath("resources.csv"))
        self.EFFICIENCIES = load_efficiencies(data_dir.joinpath("efficiencies.csv"))
        self.EVENTS = load_events(data_dir.joinpath("events.csv"))
        self.LEGACY = load_legacy(data_dir.joinpath("legacy.csv"))

    def load_board(self):
        board_path = self.data_dir.joinpath("board.csv")
        board = []
        with open(board_path) as f:
            content = f.read().splitlines()
            for line in content[1:]:
                board.append(line.split(";")[1:])
        return np.array(board, dtype=int)

initialize_game()

# estado de juego
def estado_juego():
    status = {
        "month": int(player.month), #mes
        "budget": int(player.budget),#presupuesto
        "score": int(player.score),#puntaje              
        "current_date": int(player.actual_date), #fecha actual
        "steps": int(steps), 
      "efficiencies": {int(key): int(eff.points) for key, eff in player.efficiencies.items()},
    }
    socketio.emit("game_status", status,) 


@socketio.on("enviar_mensaje")
def manejar_mensaje(data):
    """Recibir un mensaje del cliente y enviarlo a todos los conectados."""
    emit("nuevo_mensaje", data, broadcast=True)

# Diccionario para gestionar las salas
salas = {}
usuarios_conectados = {}
usuarios = {}

@socketio.on("crear_sala")
def crear_sala(data):
    user = data.get("user")
    avatar = data.get("avatar")  
    sala_id = f"sala_{random.randint(1000, 9999)}"
    salas[sala_id] = {"usuarios": [{"nombre": user, "avatar": avatar}]}
    join_room(sala_id)
    emit("sala_creada", {"sala_id": sala_id, "usuarios": salas[sala_id]["usuarios"]}, room=sala_id)

@socketio.on("unirse_sala")
def unirse_sala(data):
    sala_id = data.get("sala_id")
    user = data.get("user")
    avatar = data.get("avatar") 
    if sala_id in salas:
        salas[sala_id]["usuarios"].append({"nombre": user, "avatar": avatar})
        join_room(sala_id)
        emit("actualizar_sala", {"sala_id": sala_id, "usuarios": salas[sala_id]["usuarios"]}, room=sala_id)
    else:
        emit("error", {"message": "La sala no existe"}, to=request.sid)
        
@socketio.on("iniciar_juego")
def iniciar_juego(data):
    sala_id = data.get("sala_id")
    if sala_id in salas:
        logging.info(f"Iniciando juego en sala {sala_id} con usuarios {salas[sala_id]['usuarios']}")
        emit("iniciar_juego", {"sala_id": sala_id, "usuarios": salas[sala_id]["usuarios"]}, room=sala_id)


@socketio.on("salir_sala")
def salir_sala(data):
    """Permite a un usuario salir de una sala."""
    sala_id = data.get("sala_id")
    user = data.get("user")

    if sala_id in salas:
        salas[sala_id]["usuarios"].remove(user)
        leave_room(sala_id)
        if not salas[sala_id]["usuarios"]:
            del salas[sala_id] 
        else:
            emit("actualizar_sala", {"sala_id": sala_id, "usuarios": salas[sala_id]["usuarios"]}, room=sala_id)


@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    conn = conexion_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personajes")
    personajes = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(personajes), 200

@app.route('/monedas', methods=['GET'])
def obtener_monedas():
    conn = conexion_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monedas")
    monedas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(monedas), 200

# Ruta para registrar un nuevo usuario
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    data = request.json
    nombre = data['nombre']
    password = encriptar_contraseña(data['password'])
    conn = conexion_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (nombre, password )
            VALUES (%s, %s)
        """, (nombre, password))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Usuario registrado correctamente", "id_user": new_id}), 201

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"message": "No se pudo registrar usuario", "error": str(e)}), 500

# Ruta para iniciar sesión
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    try:
        data = request.json
        nombre = data['nombre']
        password = encriptar_contraseña(data['password'])
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s AND password = %s", (nombre, password))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario:
            user_id = usuario['id'] 
            if user_id not in usuarios:
                usuarios[user_id] = {
                    "context": Context(DATA_DIR),
                    "player": Player(context=Context(DATA_DIR), initial_budget=1000000)
                    }
            return jsonify({"message": "Inicio de sesión exitoso", "user": usuario}), 200
        else:
            return jsonify({"message": "Nombre o contraseña incorrectos"}), 401
    except ConnectionError:
        return jsonify({"message": "Sin conexión al servidor"}), 503
    except Exception as e:
        return jsonify({"message": f"Error en el servidor: {str(e)}"}), 500



@app.route('/seleccionar_personaje', methods=['POST'])
def seleccionar_personaje():
    data = request.json
    id_user = data['id_user']
    id_traje = data['id_traje']
    conn = conexion_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personajes WHERE id = %s", (id_traje,))
    traje = cursor.fetchone()
    
    if not traje:
        cursor.close()
        conn.close()
        return jsonify({"message": "El traje no existe"}), 404

    try:
        cursor.execute("""
            INSERT INTO usuario_trajes (usuario_id, traje_id)
            VALUES (%s, %s)
        """, (id_user, id_traje))
        conn.commit()
        cursor.close()
        conn.close()
        if id_user in usuarios_conectados:
            socketio.emit("traje_seleccionado", {"id_user": id_user, "id_traje": id_traje}, room=usuarios_conectados[id_user])

        return jsonify({"message": "Traje seleccionado correctamente"}), 201
    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"message": "Error al seleccionar el traje", "error": str(e)}), 500

@app.route("/game/buy", methods=["POST"])
def buy_item():
    #Permite comprar productos, proyectos o recursos.
    data = request.json
    item_type = data.get("type")
    item_id = data.get("id")

    if not player.first_turn_in_month:
        return jsonify({"message": "No estás en el primer turno del mes."}), 400

    try:
        if item_type == "producto":
            player.buy_product(item_id)
        elif item_type == "proyecto":
            player.buy_project(item_id)
        elif item_type == "recurso":
            player.hire_resource(item_id)
        else:
            return jsonify({"error": "Tipo de ítem inválido"}), 400
        estado_juego()


        return jsonify({"message": f"{item_type.capitalize()} {item_id} comprado con éxito."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route("/game/roll_dice", methods=["POST"])
def roll_dice():
    global steps
    data = request.json
    
    num_dices = data.get("num_dices", 5)
    dices, steps = player.throw_dices(num_dices)
    old_month = player.month

    player.actual_date += steps
    field = int(context.board.reshape(-1)[player.actual_date]) 

    response = {
        "dices": [int(d) for d in dices],  
        "steps": int(steps),              
        "current_date": int(player.actual_date), 
        "field": field,                  
        "new_month": bool(old_month < player.month), 
    }

    if response["new_month"]:
        player.first_turn_in_month = True
        player.pay_salaries()
        player.get_products_from_projects()
        player.get_products_from_resources()
    estado_juego()
    return jsonify(response)


@app.route("/game/products", methods=["GET"])
def get_products():
    try:
        products = []
        with open(DATA_DIR.joinpath("products.csv"), "r", encoding="latin-1") as csvfile: 
            reader = csv.reader(csvfile, delimiter=";")
            for row in reader:
                if row:
                    products.append({
                        "id": row[0],
                        "name": row[1],
                        "cost": int(row[2]) if row[2] else 0,
                        "efficiencies": row[3].split(",") if row[3] else [],
                        "dependencies": row[4].split(",") if row[4] else [],
                    })
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": f"Error al cargar productos: {str(e)}"}), 500

@app.route("/game/projects", methods=["GET"])
def get_projects():
    try:
        projects = []
        with open(DATA_DIR.joinpath("projects.csv"), "r", encoding="latin-1") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            for row in reader:
                if len(row) >= 2:
                    projects.append({
                        "id": row[0] if row[0].strip() else "0",
                        "name": row[1] if row[1].strip() else "Sin nombre",
                        "cost": int(row[2]) if len(row) > 2 and row[2].isdigit() else 0,
                        "efficiencies": row[3].split(",") if len(row) > 3 and row[3] else [],
                        "dependencies": row[4].split(",") if len(row) > 4 and row[4] else [],
                    })
        return jsonify(projects), 200
    except Exception as e:
        return jsonify({"error": f"Error al cargar proyectos: {str(e)}"}), 500

@app.route("/game/resources", methods=["GET"])
def get_resources():
    try:
        resources = []
        with open(DATA_DIR.joinpath("resources.csv"), "r", encoding="latin-1") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            for row in reader:
                if len(row) >= 2: 
                    resources.append({
                        "id": row[0] if row[0].strip() else "0",
                        "name": row[1] if row[1].strip() else "Sin nombre",
                        "cost": int(row[2]) if len(row) > 2 and row[2].isdigit() else 0,
                        "efficiencies": row[3].split(",") if len(row) > 3 and row[3] else [],
                        "dependencies": row[4].split(",") if len(row) > 4 and row[4] else [],
                    })
        return jsonify(resources), 200
    except Exception as e:
        return jsonify({"error": f"Error al cargar recursos: {str(e)}"}), 500


@app.route("/game/random_event", methods=["GET"])
def random_event():
    current_trimester = np.ceil(player.month / 3)
    possible_events = [
        event_id for event_id, event in context.EVENTS.items() if event.appear_first_in_trimester <= current_trimester
    ]
    random_event_id = random.choice(possible_events)
    event = deepcopy(context.EVENTS.get(random_event_id))
    dices, risk_level = player.throw_dices(5)
    event.level = int(risk_level) 
    required_efficiencies_ids = event.required_efficiencies
    required_efficiencies = [
        player.efficiencies[eff_id] for eff_id in required_efficiencies_ids
    ]
    max_efficiencies_point = max([eff.points for eff in required_efficiencies])

    if max_efficiencies_point >= event.level:
        player.apply_challenge_result(event.result_success)
        result = {
            "status": "success",
            "points": int(event.result_success[0]),
            "budget": int(event.result_success[1]),
        }
    else:
        player.apply_challenge_result(event.result_failure)
        result = {
            "status": "failure",
            "points": int(event.result_failure[0]),
            "budget": int(event.result_failure[1]),
        }

    response = {
        "event_description": event.description,
        "risk_level": int(risk_level), 
        "result": result,
    }

    return jsonify(response)

if __name__ == "__main__":
    from gevent import monkey
    monkey.patch_all() 
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
