const menuItems = document.querySelectorAll('.item-menu');
const chat = document.querySelector(".chat");
const chatMessages = chat.querySelector(".chat__messages");
const chatForm = chat.querySelector(".chat__form");
const chatInput = chat.querySelector(".chat__input");

function selectIcon() {
    menuItems.forEach((item) => item.classList.remove('ativo'));
    this.classList.add('ativo');
}

menuItems.forEach((item) => {
    item.addEventListener('click', selectIcon);
});

const btnExp = document.getElementById('btn-exp');
const menuLateral = document.querySelector('.menu-lateral');

btnExp.addEventListener('click', () => {
    menuLateral.classList.toggle('expandir');
    document.body.classList.toggle('menu-expandido');
});

chat.style.display = "flex";

// Conectar ao servidor Socket.IO
const socket = io.connect("http://127.0.0.1:5000/");

// Evento para quando a conexão for estabelecida
socket.on('connect', function() {
    console.log("Conectado ao servidor Socket.IO!");
});

// Evento para receber mensagens
socket.on('message', function(msg) {
    console.log("Mensagem recebida:", msg);

    // Criar um novo elemento para a mensagem recebida
    const messageElement = document.createElement("div");



    // Adicionar a mensagem à área do chat
    chatMessages.appendChild(messageElement);

    // Salvar as mensagens no localStorage
    saveMessages();

    // Rolar para o final do chat
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// Enviar mensagem
chatForm.addEventListener('submit', function(event) {
    event.preventDefault();  // Impede o envio do formulário

    const message = chatInput.value.trim();
    if (message) {
        console.log("Enviando mensagem:", message);

        // Enviar a mensagem para o servidor Socket.IO
        socket.send(message);

        // Adicionar a mensagem à área do chat (para visualização imediata)
        const messageElement = document.createElement("div");
        messageElement.classList.add("message--self");  // Estilo para mensagem enviada
        messageElement.innerText = message;
        chatMessages.appendChild(messageElement);

        // Salvar as mensagens no localStorage
        saveMessages();

        // Limpar o campo de input
        chatInput.value = "";

        // Rolar para o final do chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});

// Função para salvar as mensagens no localStorage
function saveMessages() {
    const messages = [];
    const messageElements = chatMessages.querySelectorAll(".message");
    messageElements.forEach((element) => {
        messages.push({
            text: element.innerText,
            class: element.classList.contains("message--self") ? "message--self" : "message-other"
        });
    });
    localStorage.setItem('messages', JSON.stringify(messages));
}

// Função para carregar as mensagens do localStorage
function loadMessages() {
    const savedMessages = JSON.parse(localStorage.getItem('messages'));
    if (savedMessages) {
        savedMessages.forEach((msg) => {
            const messageElement = document.createElement("div");
            messageElement.classList.add(msg.class);
            messageElement.innerText = msg.text;
            chatMessages.appendChild(messageElement);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Carregar as mensagens ao iniciar
loadMessages();
