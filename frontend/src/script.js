```javascript
const API_URL = "https://personal-finance-advisor-bot-final.onrender.com";

const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

// Store conversation history
let chatHistory = [];


// ==========================================
// ADD MESSAGE TO CHAT UI
// ==========================================

function addMessage(message, type) {

    const messageDiv = document.createElement("div");

    messageDiv.className = "message " + type;

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


// ==========================================
// SEND MESSAGE TO FASTAPI
// ==========================================

async function sendMessage() {

    const message = userInput.value.trim();

    if (!message) {
        return;
    }

    // Show user's message
    addMessage(message, "user");

    userInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Thinking...";


    try {

        // Get JWT token saved after login
        const token = localStorage.getItem("credit_token");

        if (!token) {

            throw new Error(
                "Please log in before using the AI advisor."
            );
        }


        // ==========================================
        // CALL YOUR ACTUAL FASTAPI ENDPOINT
        // ==========================================

        const response = await fetch(
            `${API_URL}/api/advisor/chat`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",

                    // FastAPI current_user() requires this
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({

                    message: message,

                    // Backend expects:
                    // history: [{ role, content }]

                    history: chatHistory.slice(-10)

                })
            }
        );


        // ==========================================
        // HANDLE HTTP ERRORS
        // ==========================================

        if (response.status === 401) {

            localStorage.removeItem("credit_token");

            throw new Error(
                "Your session has expired. Please log in again."
            );
        }


        if (!response.ok) {

            let errorMessage =
                `Server returned ${response.status}`;

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    errorMessage = errorData.detail;
                }

            } catch {
                // Keep default error message
            }

            throw new Error(errorMessage);
        }


        // ==========================================
        // READ FASTAPI RESPONSE
        // ==========================================

        const data = await response.json();


        // Your backend returns:
        //
        // {
        //     "reply": "...",
        //     "source": "gemini"
        // }

        const reply =
            data.reply ||
            "I received your request, but no response was returned.";


        // ==========================================
        // SAVE CONVERSATION HISTORY
        // ==========================================

        chatHistory.push({
            role: "user",
            content: message
        });

        chatHistory.push({
            role: "assistant",
            content: reply
        });

        // Keep only last 10 messages
        chatHistory = chatHistory.slice(-10);


        // ==========================================
        // DISPLAY AI RESPONSE
        // ==========================================

        addMessage(reply, "bot");


    } catch (error) {

        console.error("API Error:", error);

        addMessage(
            error.message ||
            "Sorry, I couldn't connect to the finance advisor server.",
            "bot"
        );


    } finally {

        sendButton.disabled = false;
        sendButton.textContent = "Send";

        userInput.focus();
    }
}


// ==========================================
// SEND BUTTON
// ==========================================

sendButton.addEventListener(
    "click",
    sendMessage
);


// ==========================================
// ENTER KEY
// ==========================================

userInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage();
        }

    }
);
```
