(function(){
    'use strict';

    const chats = document.getElementById('chats');

    let last_msg_id = -2;
    function updateHome(){
        fetch(window.chatsJsonLink + `?last-msg-id=${last_msg_id}`)
        .then(response => response.json())
        .then(data => {
            const last_msg = data['last_msg'] ? data['last_msg']: -1;


            if (last_msg != 'same'){
                last_msg_id = last_msg != -1 ? last_msg[2]: -1;
                chats.innerHTML = '';
                let contact;
                if (Object.values(data).length > 0){
                    for (let i in data){
                        contact = data[i];

                        const eachChat = document.createElement('div');
                        eachChat.className = 'each-chat';
                        eachChat.id = 'ec-' + contact.id;
                        eachChat.onclick = function(){
                            window.location.href = "chat/" + eachChat.id.substring(3);
                        };
                        
                        const contactChatCont = document.createElement('div');
                        contactChatCont.className = 'friend-chat-cont';
    
                        const contactLogoCont = document.createElement('div');
                        contactLogoCont.className = 'friend-logo-cont';
                        contactLogoCont.setAttribute('style', `background-color: #${contact.profile_color}`)
    
                        const contactLogo = document.createElement('div');
                        contactLogo.className = 'friend-logo';
                        contactLogo.innerText = contact.firstname.substring(0, 1) + contact.lastname.substring(0, 1);
                            
                        const contactChat = document.createElement('span');
                        contactChat.id = 'fc-' + contact.id;
                        contactChat.className = 'friend-chat';
                        contactChat.title = contact.email;
                        contactChat.innerText = `${contact.firstname} ${contact.lastname}`;
        
                        const contactUser = document.createElement('span');
                        contactUser.id = 'pe-' + contact.id;
                        contactUser.className = 'friend-user';
                        contactUser.innerText = '@' + contact.username;
        
                        const msgCircle = document.createElement('div');
                        msgCircle.className = 'msg-circle';
                        
                        if (contact.not_viewed){
                            msgCircle.innerText = contact.not_viewed;
                            msgCircle.style.display = 'block';
                        };
        
                        contactLogoCont.appendChild(contactLogo);
    
                        contactChatCont.appendChild(contactLogoCont);
                        contactChatCont.appendChild(contactChat);
                        contactChatCont.appendChild(contactUser);
                        eachChat.appendChild(contactChatCont);

                        if (contact.item){
                            const relatedItem = document.createElement('div');
                            relatedItem.className = 'related-item';
                            relatedItem.innerHTML = `<span>Related item: </span><a href="/${contact.item.item_id}/">${contact.item.item_title}</a>`;
                            eachChat.appendChild(relatedItem);
                        };
        
                        eachChat.appendChild(msgCircle);
                        chats.appendChild(eachChat);
    
                    }
                } else {
                    const noContacts = document.createElement('h3');
                    noContacts.innerText = 'No available contacts';
                    noContacts.id = 'no-friends';
                    chats.appendChild(noContacts);
                };
            };

            setTimeout(updateHome, 3000)
        });
    };
    
    window.onload = updateHome;
})()