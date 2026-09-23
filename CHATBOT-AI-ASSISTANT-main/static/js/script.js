// DOM Elements
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const micButton = document.getElementById('mic-button');
const statusElement = document.getElementById('status');
const jarvisCircle = document.getElementById('jarvis-circle');
const settingsToggle = document.getElementById('settings-toggle');
const settingsPanel = document.getElementById('settings-panel');
const emojiButton = document.getElementById('emoji-button');
const fileButton = document.getElementById('file-button');
const featureButtons = document.querySelectorAll('.feature-btn');
const themeButtons = document.querySelectorAll('.theme-btn');
const typingIndicator = document.getElementById('typing');

// Initialize SpeechRecognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        document.body.classList.remove('listening');
        sendMessage();
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setStatus('Ready');
        document.body.classList.remove('listening');
    };

    recognition.onend = () => {
        setStatus('Ready');
        document.body.classList.remove('listening');
    };
} else {
    micButton.style.display = 'none';
    console.warn('Speech recognition not supported');
}

// Event Listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

micButton.addEventListener('click', startVoiceInput);

// Settings Panel Toggle
settingsToggle?.addEventListener('click', () => {
    settingsPanel.classList.toggle('active');
    settingsToggle.classList.toggle('active');
});

// Theme Switching
themeButtons?.forEach(button => {
    button.addEventListener('click', () => {
        const theme = button.dataset.theme;
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('jarvis-theme', theme);
        themeButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    });
});

// Feature Buttons
featureButtons?.forEach(button => {
    button.addEventListener('click', () => {
        featureButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        activateFeature(button.dataset.feature);
    });
});

// Emoji Button
emojiButton?.addEventListener('click', () => {
    // TODO: Implement emoji picker
    console.log('Emoji picker clicked');
});

// File Upload
fileButton?.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,.pdf,.doc,.docx,.txt';
    input.onchange = handleFileUpload;
    input.click();
});

// Functions
function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    // Add user message to chat
    addMessageToChat('user', message);
    userInput.value = '';

    // Set status and show typing indicator
    setStatus('Thinking...');
    showTypingIndicator();
    document.body.classList.add('thinking');

    // Get current feature mode
    const activeFeature = document.querySelector('.feature-btn.active')?.dataset.feature || 'chat';

    // Send message to server
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            query: message,
            mode: activeFeature
        })
    })
    .then(response => response.json())
    .then(data => {
        document.body.classList.remove('thinking');
        hideTypingIndicator();
        setStatus('Ready');
        
        // Add assistant's response to chat
        addMessageToChat('assistant', data.response);
        
        // Handle special response types
        if (data.type === 'code') {
            highlightCode(data.response);
        } else if (data.type === 'image') {
            displayImage(data.response);
        }
        
        // Speak response if in voice mode and speech synthesis is supported
        if (activeFeature === 'voice' && 'speechSynthesis' in window) {
            const speech = new SpeechSynthesisUtterance(data.response);
            speech.lang = 'en-US';
            window.speechSynthesis.speak(speech);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.body.classList.remove('thinking');
        hideTypingIndicator();
        setStatus('Error occurred');
        addMessageToChat('assistant', 'Sorry, an error occurred. Please try again.');
    });
}

function addMessageToChat(sender, content, type = 'text') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'code') {
        const pre = document.createElement('pre');
        const code = document.createElement('code');
        code.textContent = content;
        pre.appendChild(code);
        contentDiv.appendChild(pre);
    } else if (type === 'image') {
        const img = document.createElement('img');
        img.src = content;
        img.alt = 'Generated Image';
        contentDiv.appendChild(img);
    } else {
        contentDiv.textContent = content;
    }
    
    const timestampDiv = document.createElement('div');
    timestampDiv.className = 'message-timestamp';
    timestampDiv.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timestampDiv);
    chatBox.appendChild(messageDiv);
    
    // Add animation class
    setTimeout(() => messageDiv.classList.add('show'), 100);
    
    // Scroll to bottom with smooth animation
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

function highlightCode(code) {
    // If you want to add code syntax highlighting, you can integrate a library like Prism.js here
    addMessageToChat('assistant', code, 'code');
}

function displayImage(imageUrl) {
    addMessageToChat('assistant', imageUrl, 'image');
}

function startVoiceInput() {
    if (recognition) {
        try {
            recognition.start();
            setStatus('Listening...');
            document.body.classList.add('listening');
        } catch (error) {
            console.error('Error starting speech recognition:', error);
        }
    }
}

function setStatus(message) {
    statusElement.textContent = message;
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setStatus('Uploading file...');
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        setStatus('Ready');
        addMessageToChat('user', `Uploaded file: ${file.name}`);
        addMessageToChat('assistant', data.response);
    })
    .catch(error => {
        console.error('Error:', error);
        setStatus('Upload failed');
    });
}

function activateFeature(feature) {
    const inputArea = document.querySelector('.input-area');
    
    // Remove all feature-specific classes
    inputArea.className = 'input-area';
    
    switch (feature) {
        case 'chat':
            setStatus('Chat Mode');
            break;
        case 'voice':
            setStatus('Voice Mode');
            inputArea.classList.add('voice-mode');
            startVoiceInput();
            break;
        case 'image':
            setStatus('Image Mode');
            inputArea.classList.add('image-mode');
            break;
        case 'code':
            setStatus('Code Mode');
            inputArea.classList.add('code-mode');
            break;
    }
}

function showTypingIndicator() {
    if (typingIndicator) {
        typingIndicator.textContent = 'Jarvis is typing...';
        typingIndicator.classList.add('typing');
    }
}

function hideTypingIndicator() {
    if (typingIndicator) {
        typingIndicator.textContent = '';
        typingIndicator.classList.remove('typing');
    }
}

// Initial setup
window.addEventListener('load', () => {
    userInput.focus();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('jarvis-theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
        const themeBtn = document.querySelector(`[data-theme="${savedTheme}"]`);
        if (themeBtn) {
            themeBtn.classList.add('active');
        }
    }
    
    // Set initial feature
    const defaultFeature = document.querySelector('.feature-btn[data-feature="chat"]');
    if (defaultFeature) {
        defaultFeature.classList.add('active');
        activateFeature('chat');
    }
});

// Handle page visibility
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        userInput.focus();
    }
});

// Add example of how to interact
addMessageToChat('assistant', 'You can ask me to search the web, tell you the time, open applications, and more. Try saying "What time is it?" or "Open YouTube".'); 