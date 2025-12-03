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

//theme switch
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const icon = document.querySelector('.header-action-btn .material-icons');
    if (icon) {
        icon.textContent = document.body.classList.contains('dark-theme') ? 'light_mode' : 'dark_mode';
    }
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

//clear chat
function clearChat() {
    if(confirm('Are you sure you want to clear the chat?')) {
        const chatbox = document.getElementById('chat-box');
        const welcomeMessage = chatbox.querySelectorAll('.bot message, .mui-message');
        const chatstatus = chatbox.querySelector('.chat-status';

        //clear all messgaes except welcome
        const allMessages = chatBox.querySelectorAll('.message:not(.bot-message), .mui-message:not(.bot), .nutrition-card');
        all.forEach(msg => msg.remove());
        
        // Show confirmation
        addMaterialMessage('Chat cleared! Ask me anything about Singaporean food nutrition.', 'bot');
    }
} 

//scroll  to bottom function
function scrollToBotoom() {
    const chatbox =document.getElementByld('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Auto-show/hide scroll button
const chatBox = document.getElementById('chat-box');
const scrollButton = document.querySelector('.scroll-to-bottom');
const fabButton = document.querySelector('.floating-action-button');

chatBox.addEventListener('scroll', function() {
    const isNearBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 100;
    
    if (scrollButton) {
        scrollButton.classList.toggle('visible', !isNearBottom);
    }
    if (fabButton) {
        fabButton.style.display = isNearBottom ? 'none' : 'flex';
    }
});

// Add timestamp to messages
function addMessageWithTimestamp(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.innerHTML = `
        <div>${text}</div>
        <div class="message-timestamp">${timestamp}</div>
        ${sender === 'user' ? '<div class="message-status"><span class="material-icons">done_all</span></div>' : ''}
    `;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    messageDiv.classList.add('new-message');
    setTimeout(() => messageDiv.classList.remove('new-message'), 1000);
}

// Voice input functionality
function startVoiceInput() {
    const userInput = document.getElementById('user-input');
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        recognition.start();
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
        };
        
        recognition.onspeechend = function() {
            recognition.stop();
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
        };
    } else {
        alert('Speech recognition not supported in this browser.');
    }
}

// Load saved theme
window.addEventListener('load', function() {
    // Theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        const icon = document.querySelector('.header-action-btn .material-icons');
        if (icon) icon.textContent = 'light_mode';
    }
    
    // Auto-focus
    document.getElementById('user-input').focus();
    
    // Show suggestions after delay
    setTimeout(() => {
        if (!document.querySelector('.quick-suggestions')) {
            showQuickQuestions();
        }
    }, 1000);
    
    // Add CSS for dark theme
    if (!document.querySelector('#dark-theme-css')) {
        const style = document.createElement('style');
        style.id = 'dark-theme-css';
        style.textContent = `
            .dark-theme {
                background: #0f172a;
            }
            .dark-theme .chat-container {
                background: rgba(30, 41, 59, 0.95);
                border-color: rgba(255, 255, 255, 0.1);
            }
            .dark-theme #chat-box {
                background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            }
            .dark-theme .bot-message {
                background: #334155;
                color: #e2e8f0;
            }
            .dark-theme #user-input {
                background: #334155;
                color: white;
                border-color: #475569;
            }
            .dark-theme .quick-button {
                background: #334155;
                color: #cbd5e1;
                border-color: #475569;
            }
        `;
        document.head.appendChild(style);
    }
});

// Add typing animation with dots
function showTypingAnimation() {
    const chatBox = document.getElementById('chat-box');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <span class="material-icons" style="color: #38a169;">smart_toy</span>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #4a5568;">Assistant is typing</span>
            <div class="typing-dots">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return typingDiv;
}


    
