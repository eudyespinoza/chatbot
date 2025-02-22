document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");

    window.sendMessage = async function() {
        let message = userInput.value.trim();
        if (message === "") return;

        // Agregar mensaje del usuario
        appendMessage(message, "user-message");

        // Limpiar el input
        userInput.value = "";

        try {
            let response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            let data = await response.json();
            if (data.response) {
                appendMessage(data.response, "bot-message");
            }
        } catch (error) {
            appendMessage("Error al conectar con el servidor.", "bot-message");
        }
    };

    function appendMessage(text, className) {
        let messageDiv = document.createElement("div");
        messageDiv.classList.add("message", className);
        messageDiv.textContent = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Enviar mensaje con Enter
    userInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});

