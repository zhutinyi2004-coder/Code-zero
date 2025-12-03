// main message sending function with backend integration
let isTyping = false;

async function sendMessage() {
    if (isTyping) return; // prevent spam while bot is responding
    
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (!message) return;
    
    // add user message with animation
    addMessageWithAnimation(message, 'user');
    userInput.value = '';
    userInput.disabled = true;
    isTyping = true;
    
    // show typing indicator
    const typingIndicator = addTypingIndicator();

    try { 
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: 'web_user_' + Date.now()
            })
        });

        // check if response ok
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        
        // remove typing indicator
        removeTypingIndicator(typingIndicator);

        // check if we got a response
        if (data.response) {
            await addBotMessageWithTypingEffect(data.response);
        } else {
            throw new Error('No response from server');
        }

    } catch (error) {
        console.error('Error details:', error);
        removeTypingIndicator(typingIndicator);
        
        // show specific error message
        const errorMsg = error.message.includes('Failed to fetch') 
            ? 'Cannot connect to server. Make sure backend is running (python app.py)'
            : 'Something went wrong. Check console for details.';
        
        addMaterialMessage(errorMsg, 'bot');
    } finally {
        userInput.disabled = false;
        userInput.focus();
        isTyping = false;
    }
}

// add message with fade-in animation
function addMessageWithAnimation(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(10px)';
    messageDiv.textContent = text;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // animate in
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.3s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
}

// add bot message with typing effect
async function addBotMessageWithTypingEffect(text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'mui-message bot';
    messageDiv.style.opacity = '0';
    
    const icon = 'smart_toy';
    const iconColor = '#1976d2';
    
    messageDiv.innerHTML = `
        <div style="display: flex; align-items: start; gap: 8px;">
            <span class="material-icons" style="color: ${iconColor}; flex-shrink: 0;">${icon}</span>
            <span class="bot-text"></span>
        </div>
    `;
    
    chatBox.appendChild(messageDiv);
    
    // fade in container
    setTimeout(() => {
        messageDiv.style.transition = 'opacity 0.3s ease';
        messageDiv.style.opacity = '1';
    }, 10);
    
    // typing effect
    const textSpan = messageDiv.querySelector('.bot-text');
    let index = 0;
    const speed = 15; // ms per character
    
    return new Promise((resolve) => {
        const typeInterval = setInterval(() => {
            if (index < text.length) {
                textSpan.textContent += text.charAt(index);
                index++;
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                clearInterval(typeInterval);
                resolve();
            }
        }, speed);
    });
}

// add regular message
function addMessage(text, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// using material-ui style to add messages
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

// add typing indicator
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

// remove typing indicator
function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
        indicator.parentNode.removeChild(indicator);
    }
}

// enter key to send message
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// quick message function
function sendQuickMessage(message) {
    const userInput = document.getElementById('user-input');
    userInput.value = message;
    sendMessage();
    
    // hide suggestions after first interaction
    const suggestions = document.querySelector('.quick-suggestions');
    if (suggestions) {
        suggestions.style.display = 'none';
    }
}

// focus input on page load
window.addEventListener('load', function() {
    document.getElementById('user-input').focus();
});

// theme switch
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const icon = document.querySelector('.header-action-btn .material-icons');
    if (icon) {
        icon.textContent = document.body.classList.contains('dark-theme') ? 'light_mode' : 'dark_mode';
    }
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

// clear chat function - actually works now
function clearChat() {
    if(confirm('clear all messages?')) {
        const chatBox = document.getElementById('chat-box');

        // remove ALL messages and cards
        const allMessages = chatBox.querySelectorAll('.message, .mui-message, .nutrition-card, .typing-indicator, .quick-suggestions');
        allMessages.forEach(msg => msg.remove());
        
        // add fresh welcome message
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'mui-message bot';
        welcomeDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="material-icons" style="color: #38a169;">smart_toy</span>
                <span>chat cleared! ask me anything about singaporean food nutrition.</span>
            </div>
        `;
        chatBox.appendChild(welcomeDiv);
        
        // scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }
} 

// scroll to bottom function
function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

// auto-show/hide scroll button
const chatBox = document.getElementById('chat-box');
const scrollButton = document.querySelector('.scroll-to-bottom');
const fabButton = document.querySelector('.floating-action-button');

if (chatBox) {
    chatBox.addEventListener('scroll', function() {
        const isNearBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 100;
        
        if (scrollButton) {
            scrollButton.classList.toggle('visible', !isNearBottom);
        }
        if (fabButton) {
            fabButton.style.display = isNearBottom ? 'none' : 'flex';
        }
    });
}

// add timestamp to messages
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

// voice input functionality (for styling only, as requested)
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

// load saved theme
window.addEventListener('load', function() {
    // theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
        const icon = document.querySelector('.header-action-btn .material-icons');
        if (icon) icon.textContent = 'light_mode';
    }
    
    // auto-focus
    document.getElementById('user-input').focus();
    
    // add css for dark theme
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
