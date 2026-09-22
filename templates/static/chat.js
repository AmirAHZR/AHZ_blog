const socket = io();


const chatBox = document.getElementById("chat-box");

const messageForm = document.getElementById("message-form");

const messageInput = document.getElementById("message-input");


const conversationId =
    chatBox.dataset.conversationId;


// ورود به دایرکت
socket.emit("join_chat", {
    conversation_id: conversationId
});


// وقتی Send زده شد
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


// وقتی پیام جدید دریافت شد
socket.on("new_message", function(message) {

    const messageElement =
        document.createElement("div");

    messageElement.classList.add("message");


    messageElement.innerHTML = `

        <strong>
            ${message.sender}
        </strong>

        <p>
            ${message.content}
        </p>

        <small>
            ${message.created_at}
        </small>

    `;


    chatBox.appendChild(messageElement);


    chatBox.scrollTop =
        chatBox.scrollHeight;

});