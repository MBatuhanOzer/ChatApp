document.addEventListener('DOMContentLoaded', () => {
    const chatSocket = new WebSocket(
        `ws://${window.location.host}/ws/chat/${window.chatId}/`
    );

    const chatBox = document.getElementById('chat-box');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const messageElement = document.createElement('div');
        messageElement.className = `message ${data.sender === 'me' ? 'right' : 'left'}`;
        messageElement.innerHTML = `<p>${data.message}</p>`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    messageForm.onsubmit = function(e) {
        e.preventDefault();
        const message = messageInput.value;
        if (message.trim() === '') return;

        chatSocket.send(JSON.stringify({
            'message': message
        }));

        messageInput.value = '';
    };
});
