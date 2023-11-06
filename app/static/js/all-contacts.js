(function(){
    'use strict';

    // Get the DOM element for all contacts
    const allContacts = document.getElementById('all-contacts');

    // Variable to track the last message ID
    let last_msg_id = -2;

    // Function to update the home page with contacts
    function updateHome(){
        // Fetch data from the server, including the last message ID
        fetch(window.allContactsJsonLink + `?last-msg-id=${last_msg_id}`)
        .then(response => response.json())
        .then(data => {
            // Get the last message ID from the server response
            const last_msg = data[0] ? data[0]['last_msg']: -1;
        
            // Check if there are new messages
            if (last_msg != 'same'){
                // Update the last message ID
                last_msg_id = last_msg != -1 ? last_msg[2]: -1;
                
                // Clear the content of allContacts element
                allContacts.innerHTML = '';
                
                let contact;
                
                // Check if there are contacts in the response data
                if (Object.values(data).length > 0){
                    // Loop through the contacts data and create elements for each contact
                    for (let i in data){
                        contact = data[i];

                        // Create elements for each contact
                        const eachContact = document.createElement('div');
                        eachContact.className = 'each-contact';
                        eachContact.id = 'ec-' + contact.id;

                        // Redirect to the chat page when a contact is clicked
                        eachContact.onclick = function(){
                            window.location.href = "chat/" + eachContact.id.substring(3);
                        };
                        
                        const contactChatCont = document.createElement('div');
                        contactChatCont.className = 'contact-chat-cont';
    
                        const contactLogoCont = document.createElement('div');
                        contactLogoCont.className = 'contact-logo-cont';
                        contactLogoCont.setAttribute('style', `background-color: #${contact.profile_color}`);
    
                        const contactLogo = document.createElement('div');
                        contactLogo.className = 'contact-logo';
                        contactLogo.innerText = contact.firstname.substring(0, 1) + contact.lastname.substring(0, 1);
                            
                        const contactChat = document.createElement('span');
                        contactChat.id = 'fc-' + contact.id;
                        contactChat.className = 'contact-chat';
                        contactChat.title = contact.email;
                        contactChat.innerText = `${contact.firstname} ${contact.lastname}`;
        
                        const contactUser = document.createElement('span');
                        contactUser.id = 'pe-' + contact.id;
                        contactUser.className = 'contact-user';
                        contactUser.innerText = '@' + contact.username;
        
                        // A message circle that shows the number of unread messages
                        const msgCircle = document.createElement('div');
                        msgCircle.className = 'msg-circle';
                        
                        // Display unread message count if there are unread messages
                        if (contact.not_viewed){
                            msgCircle.innerText = contact.not_viewed;
                            msgCircle.style.display = 'block';
                        };
        
                        // Append created elements to eachContact element
                        contactLogoCont.appendChild(contactLogo);
                        contactChatCont.appendChild(contactLogoCont);
                        contactChatCont.appendChild(contactChat);
                        contactChatCont.appendChild(contactUser);
                        eachContact.appendChild(contactChatCont);

                        // Check if the contact has a related item and display it
                        if (contact.item){
                            const relatedItem = document.createElement('div');
                            relatedItem.className = 'related-item';
                            relatedItem.innerHTML = `<span>Related item: </span><a href="/${contact.item.item_id}/">${contact.item.item_title}</a>`;
                            eachContact.appendChild(relatedItem);
                        };
        
                        eachContact.appendChild(msgCircle);
                        // Append each contact container to allContacts element
                        allContacts.appendChild(eachContact);
                    }
                } else {
                    // If there are no contacts, display a message indicating no available contacts
                    const noContacts = document.createElement('h3');
                    noContacts.innerText = 'No available contacts';
                    noContacts.id = 'no-contacts';
                    allContacts.appendChild(noContacts);
                };
            };

            // Call the function recursively after a delay
            setTimeout(updateHome, 3000);
        });
    };

    // Initial call to the updateHome function
    updateHome();
})();
