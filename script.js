//connect to backend flask
async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (!message) return;

    // add user message
    addMessage(message, 'user');
    userInput.value = '';

    try {
        // flask backend
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: 'web_user'
            })
        });

        const data = await response.json();

        //chatbot response
        addMaterialMessage(data.response, 'bot');

    } catch (error) {
        console.error('Error:', error);
        addMaterialMessage('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

// messages - simple style
function addMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// using Material-UI style to add messages
function addMaterialMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `mui-message ${sender}`;

    const icon = sender === 'user' ? 'person' : 'smart_toy';
    const iconColor = sender === 'user' ? 'white' : '#1976d2';

    messageDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <span class="material-icons" style="color: ${iconColor};">${icon}</span>
            <span>${text}</span>
        </div>
    `;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// enter to send messages
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// focus on user input when page reloads
window.addEventListener('load', function() {
    document.getElementById('user-input').focus();
});
