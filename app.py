from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Configurar OpenAI
client = OpenAI(api_key=api_key)

# Inicializar Flask
app = Flask(__name__)

# Historial de conversación
conversation_history = [
    {"role": "system", "content": "Eres un vendedor de una empresa Argentina de materiales de contrucción que se llama "
                                  "Familia Bercomat. Tu nombre es Lautaro. al iniciar una conversacion siempre te debes"
                                  "presentarte asi Hola soy Lautaro vededor de Familia Bercomat ¿en que puedo ayudarte?."
                                  "Tu objetivo es cerrar la venta"}
]

@app.route("/")
def chat():
    """Carga la interfaz de chat"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def get_response():
    """Recibe el mensaje del usuario, consulta OpenAI y devuelve la respuesta"""
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    # Agregar mensaje del usuario al historial
    conversation_history.append({"role": "user", "content": user_message})

    # Obtener respuesta de OpenAI
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
