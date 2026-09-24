const socket = io();

const chatBox = document.getElementById("chat-box");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");

const conversationId = chatBox.dataset.conversationId;
const currentUserId = chatBox.dataset.userId;


// ========================================
// Join conversation
// ========================================

socket.emit("join_chat", {
    conversation_id: conversationId
});


// ========================================
// Mark existing messages as read
// ========================================

socket.emit("mark_messages_read", {
    conversation_id: conversationId
});


// ========================================
// Send message
// ========================================

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


// ========================================
// Receive new message
// ========================================

socket.on("new_message", function(message) {

    const messageElement = document.createElement("div");

    messageElement.classList.add("message");

    messageElement.dataset.messageId = message.id;
    messageElement.dataset.senderId = message.sender_id;


    // Sender

    const sender = document.createElement("strong");

    sender.textContent = message.sender;


    // Content

    const content = document.createElement("p");

    content.textContent = message.content;


    // Time

    const createdAt = document.createElement("small");

    createdAt.textContent = message.created_at;


    messageElement.appendChild(sender);
    messageElement.appendChild(content);
    messageElement.appendChild(createdAt);


    // اگر پیام مال خودمان است
    // یک تیک نمایش بده

    if (
        String(message.sender_id) ===
        String(currentUserId)
    ) {

        const status = document.createElement("span");

        status.classList.add("message-status");

        status.textContent = "✓";

        messageElement.appendChild(status);
    }


    chatBox.appendChild(messageElement);

    chatBox.scrollTop = chatBox.scrollHeight;


    // اگر پیام از طرف مقابل است،
    // همان لحظه read شود

    if (
        String(message.sender_id) !==
        String(currentUserId)
    ) {

        socket.emit("mark_messages_read", {
            conversation_id: conversationId
        });

    }

});


// ========================================
// Someone read our messages
// ========================================

socket.on("messages_read", function(data) {

    if (
        String(data.conversation_id) !==
        String(conversationId)
    ) {
        return;
    }


    // اگر خودمان پیام‌ها را read کرده‌ایم،
    // نباید پیام‌های خودمان دو تیک شوند.

    if (
        String(data.reader_id) ===
        String(currentUserId)
    ) {
        return;
    }


    const messages =
        chatBox.querySelectorAll(".message");


    messages.forEach(function(messageElement) {

        const senderId =
            messageElement.dataset.senderId;


        // فقط پیام‌های خودمان را ✓✓ کن.

        if (
            String(senderId) !==
            String(currentUserId)
        ) {
            return;
        }


        const status =
            messageElement.querySelector(
                ".message-status"
            );


        if (status) {
            status.textContent = "✓✓";
        }

    });

});