const socket = io();

const chatBox = document.getElementById("chat-box");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");

const conversationId = chatBox.dataset.conversationId;
const currentUserId = chatBox.dataset.userId;


// Join conversation
socket.emit("join_chat", {
    conversation_id: conversationId
});


// Mark messages as read
socket.emit("mark_messages_read", {
    conversation_id: conversationId
});


// Send message
messageForm.addEventListener("submit", function(event) {

    event.preventDefault();

    const content = messageInput.value.trim();

    if (!content) {
        return;
    }

    socket.emit("send_message", {
        conversation_id: conversationId,
        content: content
    });

    messageInput.value = "";
    messageInput.focus();

});


// New message
socket.on("new_message", function(message) {

    const messageElement = document.createElement("div");

    messageElement.classList.add("message");

    messageElement.dataset.messageId = message.id;
    messageElement.dataset.senderId = message.sender_id;


    const sender = document.createElement("strong");
    sender.textContent = message.sender;


    const content = document.createElement("p");
    content.textContent = message.content;


    const createdAt = document.createElement("small");
    createdAt.textContent = message.created_at;


    messageElement.appendChild(sender);
    messageElement.appendChild(content);
    messageElement.appendChild(createdAt);


    if (String(message.sender_id) === String(currentUserId)) {

        const status = document.createElement("span");

        status.classList.add("message-status");

        status.textContent = "✓";

        messageElement.appendChild(status);
    }


    chatBox.appendChild(messageElement);

    chatBox.scrollTop = chatBox.scrollHeight;


    // If the message belongs to the other user,
    // mark it as read immediately.
    if (String(message.sender_id) !== String(currentUserId)) {

        socket.emit("mark_messages_read", {
            conversation_id: conversationId
        });

    }

});


// Messages were read
socket.on("messages_read", function(data) {

    if (String(data.conversation_id) !== String(conversationId)) {
        return;
    }


    const messages = chatBox.querySelectorAll(".message");


    messages.forEach(function(messageElement) {

        const senderId = messageElement.dataset.senderId;

        if (String(senderId) !== String(data.reader_id)) {
            return;
        }


        const status = messageElement.querySelector(".message-status");

        if (status) {
            status.textContent = "✓✓";
        }

    });

});