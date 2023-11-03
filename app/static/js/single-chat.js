(function(){
    'use strict';

    // Get DOM elements
    const chatBox = document.getElementById('chat-box'); // Chat container
    const toBottomBtn = document.getElementById('to-bottom-btn'); // Button to scroll to bottom
    const toBottomBtnCont = document.getElementById('to-bottom-btn-container'); // Container for scroll to bottom button
    const msgCircle = document.getElementById('msg-circle'); // Unread messages circle
    const cxtItemSelector = document.querySelector('.context-item-selector');
    const generalCxt = cxtItemSelector.querySelector('button');

    // Scroll to the bottom of the chat box when the "scroll to bottom" button is clicked
    toBottomBtn.onclick = function(){
        chatBox.scrollTop = chatBox.scrollHeight;
    };
    
    function cxtItemFunc(){
        window.itemId = this.id ? this.id.split('-')[1]: null;

        cxtItemSelector.style.transform = 'translateY(100%)';
        
        cxtItemSelector.removeChild(this);
        cxtItemSelector.prepend(this);
        setTimeout(() => {
            cxtItemSelector.removeAttribute('style');
        }, 700);
    };

    generalCxt.addEventListener('click', cxtItemFunc);
    
    // Send message when the "Send" button is clicked
    document.getElementById('send').addEventListener('click', function(){
        // Create a text message object with message content and item ID
        const textMessage = {
            'text-message': document.getElementById('text-message').value,
            'item-id': window.itemId
        };

        // Check if the message is not empty
        if (textMessage['text-message'] != ''){
            // Send the message using fetch API
            fetch(window.sendMsgLink, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrf
                },
                body: JSON.stringify(textMessage)
            });
            // Clear the input field after sending the message
            document.getElementById('text-message').value = '';
        };
    });

    // Focus on the message input field
    const messageInp = document.getElementById('text-message');
    messageInp.focus()

    // Send message when Enter key is pressed
    messageInp.addEventListener('keydown', function(event){
        if (event.key == 'Enter') {
            document.getElementById('send').click();
            document.getElementById('text-message').value = '';
        };
    });

    // Function to mark messages as viewed
    function tagAsViewed(lst){
        fetch(window.tagAsViewedLink, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrf
            },
            body: JSON.stringify({'ids': lst})
        });
    };

    // Create an element to show number of unread messages
    const unRead = document.createElement('div');
    unRead.setAttribute('id', 'unread');

    // Variables for tracking unread messages
    let unReadPosition;
    let unReadNumber;
    
    let chat;
    let firstLoad = true;

    // Array to store message IDs
    const idsLst = [];

    // Variable to store the last message ID
    let last_msg_id = -2;

    const itemIds = [];

    // Function to update messages and handle unread messages
    function updateMsg(){
        let last_msg_id_link = `?last-msg-id=${last_msg_id}`;

        // Check if there is an item ID, add it to the API request
        if (window.itemId){
            last_msg_id_link += `&item-id=${window.itemId}`;
        };

        // Fetch new messages from the server
        fetch(window.chatJson + last_msg_id_link)
        .then(response => response.json())
        .then(data => {
            // Get the ID of the last message from the server
            const last_msg_id_server = data[Object.values(data).length-1] ? data[Object.values(data).length-1]['id']: -1;

            // Check if there are new messages
            if (last_msg_id_server != 'same'){
                last_msg_id = last_msg_id_server;
                chatBox.innerHTML = '';

                // Check if there are messages in the response
                if (Object.values(data).length > 0){
                    const dateList = [];
                    // Loop through the messages
                    for (let i in data){
                        chat = data[i];

                        // Check for unread messages and add their IDs to the list
                        if (!chat.viewed && !idsLst.includes(chat.id) && chat.sent_by == window.contactId){
                            idsLst.push(chat.id);
                        };

                        // Create DOM elements for each message
                        const chatElementContainer = document.createElement('div');
                        chatElementContainer.setAttribute('class', 'chat-text-container');
                        const chatElement = document.createElement('div');

                        // Check if the message is related to an item and add a link to the item
                        if (chat.item_id){
                            const itemTitleElement = document.createElement('a');
                            itemTitleElement.setAttribute('href', `/${chat.item_id}/`);
                            itemTitleElement.classList.add('item-link');
                            itemTitleElement.innerHTML = "<span>Item: </span>" + chat.item_title;

                            chatElement.appendChild(itemTitleElement);
                        };

                        const reverseChat = data[Object.values(data).length-1-i]
                        if (reverseChat.item_id && !itemIds.includes(reverseChat.item_id)){

                            if (!itemIds.length){
                                window.itemId = reverseChat.item_id;
                            };

                            itemIds.push(reverseChat.item_id);

                            const cxtItem = document.createElement('button');
                            cxtItem.id = `item-${reverseChat.item_id}`;
                            cxtItem.title = reverseChat.item_title;
                            cxtItem.innerText = reverseChat.item_title;
                            cxtItem.onclick = cxtItemFunc;
                            
                            cxtItemSelector.insertBefore(cxtItem, generalCxt);
                        };

                        const chatText = document.createElement('div');
                        chatText.innerText = chat.text;
                        chatText.className = 'text';
                        
                        const chatTime = document.createElement('div');
                        chatTime.innerText = chat.time;
                        chatTime.className = 'time';

                        // Determine sender/receiver and apply appropriate styles
                        if (chat.sent_by == window.userId){
                            chatElement.className = 'sender chat-text';
                        } else {
                            chatElement.className = 'receiver chat-text';
                        };

                        // Check if the message date is already displayed, if not, add it
                        if (!dateList.includes(chat.date)){
                            const dateContainer = document.createElement('div');
                            dateContainer.className = 'date-container';
                            
                            const dateElement = document.createElement('span');
                            dateElement.className = 'date';
                            
                            dateElement.innerText = chat.date;
                            
                            dateContainer.appendChild(dateElement);
                            chatBox.appendChild(dateContainer);
                            
                            dateList.push(chat.date);
                        };

                        // Append message elements to the chat box
                        chatElement.appendChild(chatText);
                        chatElement.appendChild(chatTime);
                        chatElementContainer.appendChild(chatElement);
                        chatBox.appendChild(chatElementContainer);

                        // Calculate position of unread message circle
                        if (idsLst.length == 1){
                            unReadPosition = Array.from(chatBox.children).indexOf(chatElementContainer);
                        };
                    };

                    // Display unread messages and mark them as viewed
                    unReadNumber = idsLst.length;
                    if (unReadNumber && firstLoad){
                        if (unReadNumber > 1){
                            unRead.innerText = '** ' + unReadNumber + ' unread messages **';
                        } else {
                            unRead.innerText = '** ' + unReadNumber + ' unread message **';
                        };

                        tagAsViewed(idsLst);
                        idsLst.length = 0;

                        chatBox.insertBefore(unRead, chatBox.children[unReadPosition]);
                        unRead.scrollIntoView();
                    } else if (unReadNumber){
                        tagAsViewed(idsLst);

                        msgCircle.innerText = parseInt(msgCircle.innerText) + 1;
                        msgCircle.style.display = 'block';
                        idsLst.length = 0;

                        if (toBottomBtnCont.style.display != 'block'){
                            chatBox.scrollTop = chatBox.scrollHeight;
                        };

                    } else {
                        chatBox.scrollTop = chatBox.scrollHeight;
                    };

                    firstLoad = false;

                } else {
                    // Text to show if there is no message history
                    chatBox.innerHTML = '<div class="send-first-msg">--- Send The First Message! ---</div>';
                };
            };

            // Call the function recursively after a delay
            setTimeout(updateMsg, 1500);

        });
    };

    // Event listner for displaying and hiding to-bottom-btn
    chatBox.addEventListener('scroll', function(){
        if (chatBox.scrollHeight - 15 > chatBox.clientHeight + chatBox.scrollTop){
            toBottomBtnCont.style.display = 'block';
        } else {
            toBottomBtnCont.style.display = 'none';
            msgCircle.innerText = 0;
            msgCircle.style.display = 'none';
        };
    });
    
    updateMsg();
})()