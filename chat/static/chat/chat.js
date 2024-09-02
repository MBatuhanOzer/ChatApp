document.addEventListener("DOMContentLoaded", function () {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');


    // Initialize WebSocket connection
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + user2Id + '/'
    );

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const message = data.message;
        const senderId = data.sender_id;
        const senderUsername = data.sender_username;

        appendMessage(message, senderId === parseInt(userId) ? 'user' : 'other', senderUsername);
    };

    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };

    function appendMessage(message, senderType, senderUsername) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', senderType);
        messageElement.textContent = `${senderUsername}: ${message}`;
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Handle form submission to send a message
    messageForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = ''; // Clear input field
        }
    });
});
