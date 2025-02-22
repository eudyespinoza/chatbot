from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import pickle

# Cargar variables de entorno
load_dotenv()

# Inicializar cliente de OpenAI
client = OpenAI()

# Inicializar Flask
app = Flask(__name__)

# Archivos de caché
PRODUCTOS_CACHE = "productos_cache.pkl"
STOCK_CACHE = "stock_cache.pkl"

# Cargar caché de productos y stock
def cargar_cache(archivo):
    try:
        with open(archivo, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return []

productos = cargar_cache(PRODUCTOS_CACHE)
stock = cargar_cache(STOCK_CACHE)

# Historial de conversación
conversation_history = [
    {"role": "system", "content": "Eres un vendedor de una empresa Argentina de materiales de construcción llamada "
                                  "Familia Bercomat. Tu nombre es Lautaro. Al iniciar una conversación siempre debes "
                                  "presentarte así: 'Hola, soy Lautaro, vendedor de Familia Bercomat. ¿En qué puedo ayudarte?'. "
                                  "Tu objetivo es cerrar la venta. Tus respuestar deben ser cortas y precisas, por ejemplo "
                                  "si te pide algun cálculo no necesitas explicar el proceso del cálculo a menos que te "
                                  "lo solicite, solo da la respuesta"}
]

@app.route("/")
def chat():
    """Carga la interfaz de chat"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def get_response():
    """Recibe el mensaje del usuario, consulta OpenAI y devuelve la respuesta"""
    user_message = request.json.get("message", "").strip()
    tienda = request.json.get("store_number", "Todas")  # Filtrar por tienda si se proporciona

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # 1. Buscar productos que coincidan con la consulta del usuario
    productos_encontrados = [
        p for p in productos if user_message.lower() in p["nombre_producto"].lower()
    ]

    if tienda != "Todas":
        productos_encontrados = [p for p in productos_encontrados if p["store_number"] == tienda]

    # 2. Combinar datos de stock
    resultados = []
    for producto in productos_encontrados:
        stock_info = next((s for s in stock if s["codigo"] == producto["numero_producto"] and s["almacen_365"] == producto["store_number"]), None)
        stock_disponible = stock_info["disponible_venta"] if stock_info else "No disponible"

        resultados.append(
            f"{producto['nombre_producto']} - {producto['categoria_producto']} | Precio: ${producto['precio_final_con_descuento']} | Stock: {stock_disponible} en {producto['store_number']}"
        )

    # 3. Preparar mensaje para OpenAI
    if resultados:
        info_productos = "\n".join(resultados)
        prompt = f"El usuario busca '{user_message}'. Aquí están los productos encontrados:\n{info_productos}\nResponde de manera clara recomendando opciones."
    else:
        prompt = f"El usuario busca '{user_message}', pero no encontré coincidencias en la caché. Sugiere alternativas o indica que no hay stock."

    # Agregar mensaje del usuario y la información del sistema al historial
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "system", "content": prompt})

    # 4. Obtener respuesta de OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )

    bot_message = response.choices[0].message.content

    # Agregar respuesta del bot al historial
    conversation_history.append({"role": "assistant", "content": bot_message})

    return jsonify({"response": bot_message})

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
