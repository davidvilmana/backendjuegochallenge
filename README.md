# **Challenge**

## **Game API - Flask SocketIO**

### **Descripción**

Este proyecto es una API desarrollada en Flask que integra `Socket.IO` para manejar eventos en tiempo real. Es una plataforma para gestionar juegos en línea, donde los jugadores pueden unirse a salas, interactuar en tiempo real y realizar diversas operaciones relacionadas con el juego, como comprar productos, lanzar dados y manejar eventos aleatorios.

---

## **Características Principales**

### **Autenticación de Usuarios**
- Registro e inicio de sesión con contraseñas encriptadas.

### **Manejo de Salas**
- Creación, unión y abandono de salas para jugadores.

### **Simulación de Juego**
- Compra de productos, lanzamiento de dados y manejo de recursos.

### **Eventos Aleatorios**
- Gestión de eventos dentro del juego, evaluados por nivel de riesgo.

### **Integración con Base de Datos**
- Uso de MySQL para gestionar datos de usuarios y el estado del juego.

### **CORS y Conexión en Tiempo Real**
- Permite conexiones desde orígenes cruzados y comunicación en tiempo real con `Socket.IO`.

---

## **Requisitos Previos**

### **Entorno**
- **Python 3.8+**
- **MySQL**
- **React** ( Link de repositorio GITHUB https://github.com/davidvilmana/frontendjuego  )


### **Bibliotecas de Python**
Asegúrate de instalar las siguientes bibliotecas:
- `Flask`
- `Flask-CORS`
- `Flask-SocketIO`
- `pymysql`
- `numpy`
- `gevent`

---
## Correr el Api
Sigue estos pasos para ejecutar el proyecto en tu máquina local:

1. Clona el repositorio:
   ```bash
   git clone https://github.com/davidvilmana/backendjuegochallenge.git
   cd backendjuegochallenge

2. Inicia el servidor de desarrollo:
   ```bash
   cd src
   python app.py
3. Inicia el servidor de desarrollo:
   ```bash
    http://127.0.0.1:5000/
---