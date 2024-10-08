document.addEventListener("DOMContentLoaded", function () {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatWindow = document.getElementById('chat-window');


    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + user2Id + '/'
    );

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const message = data.message;
        const senderId = data.sender_id;
        const senderUsername = data.sender_username;
        const timestamp = data.timestamp;  

        appendMessage(message, senderId === parseInt(userId) ? 'user' : 'other', senderUsername, timestamp);
    };

    chatSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };

    function appendMessage(message, senderType, senderUsername, timestamp) {
        const messageText = `${senderUsername}: ${message}`;
        const existingMessages = Array.from(chatWindow.querySelectorAll('.message'))
            .map(msg => msg.getAttribute('data-timestamp')); 

        if (!existingMessages.includes(timestamp)) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', senderType);
            messageElement.setAttribute('data-timestamp', timestamp);  
            messageElement.textContent = messageText;
            chatWindow.appendChild(messageElement);
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    }

    messageForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = ''; 
        }
    });
});
