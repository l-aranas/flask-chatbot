document.addEventListener("DOMContentLoaded", function () {
    const userInputField = document.getElementById('user-input');
    userInputField.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

function sendMessage() {
    let userInputField = document.getElementById('user-input');
    let userInput = userInputField.value.trim();
    
    if (!userInput) return; // Prevent sending empty messages

    userInputField.value = '';

    // Display user message
    displayMessage(userInput, 'user');

    // Create and display typing indicator
    let chatbox = document.getElementById('chatbox');
    let typingIndicator = document.createElement('div');
    typingIndicator.classList.add('typing-indicator');
    typingIndicator.textContent = 'Chatbot is typing';
    typingIndicator.id = 'typing-indicator'; // Add an ID so we can remove it later
    chatbox.appendChild(typingIndicator);
    chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll

    // Simulate delay before bot response
    setTimeout(() => {
        fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('typing-indicator').remove(); // Remove typing indicator
            displayMessage(data.response, 'bot');
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById('typing-indicator').remove();
            displayMessage("Error communicating with the server.", 'bot');
        });
    }, 1500); // Keep typing indicator visible for 1.5 seconds
}

function displayMessage(message, sender) {
    let chatbox = document.getElementById('chatbox');

    // Create message container
    let messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container');

    // Create sender label
    let senderLabel = document.createElement('div');
    senderLabel.classList.add(sender === 'user' ? 'user-label' : 'bot-label');
    senderLabel.textContent = sender === 'user' ? 'You' : 'Chatbot';

    // Create message bubble
    let messageElement = document.createElement('div');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = message;

    // Add proper alignment
    messageContainer.classList.add(sender === 'user' ? 'user-container' : 'bot-container');

    // Append elements
    messageContainer.appendChild(senderLabel);
    messageContainer.appendChild(messageElement);
    chatbox.appendChild(messageContainer);
    
    // Auto-scroll to latest message
    chatbox.scrollTop = chatbox.scrollHeight;
}
