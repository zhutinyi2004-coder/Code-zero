// connect to backend flask
async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (!message) return;
    addMessage(message, 'user');
    userInput.value = '';
    userInput.disabled = true; 
    const typingIndicator = addTypingIndicator();

    try {

        await new Promise(resolve => setTimeout(resolve, 1500)); 
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
        

        removeTypingIndicator(typingIndicator);


        addMaterialMessage(data.response, 'bot');

    } catch (error) {
        console.error('Error:', error);
        // Ensure indicator is removed even on error
        removeTypingIndicator(typingIndicator); 
        addMaterialMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        // Re-enable input
        userInput.disabled = false;
        userInput.focus();
    }
}


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


function addTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'typing-indicator';
    indicatorDiv.innerHTML = `
        <span class="material-icons" style="color: #38a169;">smart_toy</span>
        <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    chatBox.appendChild(indicatorDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return indicatorDiv; 
}


function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}


document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

window.addEventListener('load', function() {
    document.getElementById('user-input').focus();
});

function addTypingIndicator() {
    const chatBox = document.getElementById('chat-box');
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'typing-indicator';
    indicatorDiv.innerHTML = `
        <span class="material-icons" style="color: #38a169;">restaurant_menu</span>
        <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
        <span style="font-style: italic; color: #4a5568;">wait a sec...</span>
    `;
    chatBox.appendChild(indicatorDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return indicatorDiv; 
}
