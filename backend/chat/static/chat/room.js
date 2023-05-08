const roomId = JSON.parse(document.getElementById('roomId').textContent);
const chatInput = document.querySelector('#chat_input')
const chatSubmit = document.querySelector('#button-addon2')
const user = JSON.parse(document.querySelector('#username').textContent)
// chat log and buble creation


const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomId
    + '/'
);
console.log(chatSocket)


chatInput.focus();
chatInput.onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        chatSubmit.click();
    }
};


chatSubmit.onclick = function(e){
    const message = chatInput.value;
    if (message !== ''){
        chatSocket.send(JSON.stringify({
            'message': message,
            'command': 'new_message'
        }));
        chatInput.value = ''
    }
}

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data.message;
    const author = data.author;
    const timestamp = data.timestamp;
    
    const chatLog = document.querySelector('#chat_log')
    const outDiv = document.createElement('div')
    const avatar = document.createElement('i')
    const inDiv = document.createElement('div')
    const pText = document.createElement('p')
    const pInfo = document.createElement('p')
    
    console.log('USER :', user, '\n Mst Author :', author)
    
    if (user === author){
        chatLog.appendChild(outDiv)
        outDiv.appendChild(inDiv)
        inDiv.appendChild(pText)
        pText.textContent = message
        inDiv.appendChild(pInfo)
        pInfo.textContent = `${author}|${timestamp}`
        outDiv.appendChild(avatar)
        // classes and styles 
        outDiv.className = 'd-flex flex-row justify-content-end mb-4 pt-1'
        pText.className = 'small p-2 me-1 mb-1 text-white rounded-3 bg-primary'
        pInfo.className = 'small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end'
        avatar.className = 'bi bi-person-circle'
        avatar.style.fontSize = '1.5em'

    }else{
        chatLog.appendChild(outDiv)
        outDiv.appendChild(avatar)
        outDiv.appendChild(inDiv)
        inDiv.appendChild(pText)
        pText.textContent = message
        inDiv.appendChild(pInfo)
        pInfo.textContent = `${author}|${timestamp}`

        // classes and styles 
        outDiv.className = 'd-flex flex-row justify-content-start'
        pText.className = 'small p-2 ms-1 mb-1 rounded-3'    
        pInfo.className = 'small ms-3 mb-3 rounded-3 text-muted smaller'  
        pText.style.backgroundColor = '#d7d8d9'
        avatar.className = 'bi bi-person-lines-fill'
        avatar.style.fontSize = '1.5em'
    }

    window.scrollTo(0, document.body.scrollHeight);
};

chatSocket.onopen = function(e){
    
    chatSocket.send(JSON.stringify({
        'command': 'load_messages',
    }))
    console.log('chat socket connected')
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// document.querySelector('#chat-message-submit').onclick = function(e) {
//     const messageInputDom = document.querySelector('#chat-message-input');
//     const message = messageInputDom.value;
//     chatSocket.send(JSON.stringify({
//         'message': message
//     }));
//     messageInputDom.value = '';
// };