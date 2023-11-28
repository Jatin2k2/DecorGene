document.addEventListener('DOMContentLoaded', function() {
    const chatDisplay = document.getElementById('chat-display');
    const userInputElement = document.getElementById('user-input');
    const sendButton = document.getElementById('send-btn');
    
    const apiKey = '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'; // Replace with your actual OpenAI API key
    const baseUrl = 'http://127.0.0.1:5000'; // Replace with your backend URL
    
    sendButton.addEventListener('click', sendMessage);
    
    function sendMessage() {
        const userMessage = userInputElement.value.trim();
        if (userMessage) {
            displayMessage('You', userMessage);
            
            fetch(`${baseUrl}/send-message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `user_input=${encodeURIComponent(userMessage)}`
            })
            .then(response => response.json())
            .then(data => {
                const botReply = data.bot_reply;
                displayMessage('Chatbot', botReply);
            })
            .catch(error => {
                console.error('Error:', error);
            });
            
            userInputElement.value = '';
            sendButton.disabled = true; // Disable the send button temporarily
            setTimeout(() => {
            sendButton.disabled = false; // Re-enable the send button after a delay
            }, 2000);
        }
    }
    
    function displayMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatDisplay.appendChild(messageElement);
        chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll to bottom
    }
});
