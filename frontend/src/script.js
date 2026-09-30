const API_URL = "https://personal-finance-advisor-bot-final.onrender.com";

const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

function addMessage(message, type) {

```
const messageDiv = document.createElement("div");

messageDiv.className = "message " + type;

messageDiv.textContent = message;

chatBox.appendChild(messageDiv);

chatBox.scrollTop = chatBox.scrollHeight;
```

}

async function sendMessage() {

```
const message = userInput.value.trim();

if (!message) {
    return;
}

addMessage(message, "user");

userInput.value = "";

sendButton.disabled = true;
sendButton.textContent = "Sending...";

try {

    /*
     * Change "/chat" below if your backend uses
     * a different API endpoint.
     */

    const response = await fetch(
        `${API_URL}/chat`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            `Server returned ${response.status}`
        );
    }

    const data = await response.json();

    /*
     * Supports several common backend response formats.
     */

    const reply =
        data.response ||
        data.reply ||
        data.message ||
        data.answer ||
        "I received your request, but no response was returned.";

    addMessage(reply, "bot");

} catch (error) {

    console.error("API Error:", error);

    addMessage(
        "Sorry, I couldn't connect to the finance advisor server. Please try again.",
        "bot"
    );

} finally {

    sendButton.disabled = false;
    sendButton.textContent = "Send";

    userInput.focus();
}
```

}

sendButton.addEventListener(
"click",
sendMessage
);

userInput.addEventListener(
"keydown",
function(event) {

```
    if (event.key === "Enter") {
        sendMessage();
    }

}
```

);
