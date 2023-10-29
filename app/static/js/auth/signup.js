(function(){
    'use strict';
    
    const firstName = document.getElementById('firstName');
    const lastName = document.getElementById('lastName');
    const checkDiv = document.querySelector('.check-username-div');
    const usernameInp = document.getElementById('username');
    const email = document.getElementById('email');
    const emailSpan = document.querySelector('.email-check');
    const passwordInp = document.getElementById('password');
    const rePassword = document.getElementById('r-password');
    
    document.querySelector('input[type="text"]:first-child').focus();

    const checkAll = {
        firstName: 1 ? firstName.value: 0,
        lastName: 1 ? lastName.value: 0,
        username: 0,
        email: 0,
        password: 0,
        rePassword: 0
    };

    function checkName(firstLast){
        if (firstLast.value.length >= 1){
            firstLast.style.borderColor = 'green';
            checkAll[firstLast.id] = 1;
        } else {
            firstLast.style.borderColor = 'tomato';
            checkAll[firstLast.id] = 0;
        };

        updateSubmitState();
    };

    function updateSubmitState(){
        if (Object.values(checkAll).includes(0)){
            document.querySelector('input[type="submit"]').disabled = true;
        } else {
            document.querySelector('input[type="submit"]').disabled = false;
        };
    };

    firstName.addEventListener('input', function(event){
        checkName(event.target);
    });

    lastName.addEventListener('input', function(event){
        checkName(event.target);
    });

    function checkUsername(){
        if (usernameInp.value.length > 0){
            checkDiv.querySelector('img').style.display = 'inline';

            const validUsername = /^[a-zA-Z0-9_-]{3,16}$/;

            if (validUsername.test(usernameInp.value)) {
                fetch(window.checkUserEmail, {
                    method: 'POST',
                    body: JSON.stringify({
                        username: usernameInp.value
                    }),
                    headers: {
                        'Content-type': 'application/json',
                        'X-CSRFToken': window.csrf
                    }
                })
                .then(response => response.json())
                .then(data => {
                    checkDiv.querySelector('img').style.display = 'none';
                    const msg = data['message'];
                    if (msg){
                        usernameInp.setAttribute('style', 'border-color: green;');
                        checkDiv.querySelector('span').className = 'green';
                        checkDiv.querySelector('span').innerHTML = 'Username is available&#9989;';
                        checkAll.username = 1;
                    } else {
                        usernameInp.setAttribute('style', 'border-color: tomato;');
                        checkDiv.querySelector('span').className = 'red';
                        checkDiv.querySelector('span').innerHTML = 'username was already taken&#10060;';
                        checkAll.username = 0;
                    };
                });
            } else {
                checkDiv.querySelector('img').style.display = 'none';
                usernameInp.setAttribute('style', 'border-color: tomato;');
                checkDiv.querySelector('span').className = 'red';
                checkDiv.querySelector('span').innerHTML = 'username is invalid&#10060;';
                checkAll.username = 0;
            };

        } else {
            usernameInp.setAttribute('style', 'border-color: tomato;');
            checkDiv.querySelector('span').innerText = '';
            checkAll.username = 0;
        };

        updateSubmitState();
    };

    if (usernameInp.value){
        checkUsername();
    };

    usernameInp.addEventListener('input', function(){
        setTimeout(checkUsername, 50);
    });

    function checkEmail(){
        if ( /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/.test(email.value)){
            fetch(window.checkUserEmail, {
                method: 'POST',
                body: JSON.stringify({
                    email: email.value
                }),
                headers: {
                    'Content-type': 'application/json',
                    'X-CSRFToken': window.csrf
                }
            })
            .then(response => response.json())
            .then(data => {
                const msg = data['message'];

                if (msg) {
                    emailSpan.className = 'green';
                    emailSpan.innerHTML = 'Email is available&#9989;';
                    email.style.borderColor = 'green';
                    checkAll.email = 1;
                } else {
                    emailSpan.className = 'red';
                    emailSpan.innerHTML = 'Email was already taken&#10060';
                    email.style.borderColor = 'tomato';
                    checkAll.email = 0;
                };
            });
        } else {
            emailSpan.innerHTML = '';
            email.style.borderColor = 'tomato';
            checkAll.email = 0;
        };

        updateSubmitState();
    };

    email.addEventListener('input', checkEmail);

    if (email.value){
        checkEmail();
    };

    passwordInp.addEventListener('input', function(){
        let redBorder = 0
        if (/[a-z]/.test(passwordInp.value)){
            document.getElementById('lc').className = 'passed';
        } else {
            document.getElementById('lc').className = 'failed';
            redBorder++;
        };
        
        if (/[A-Z]/.test(passwordInp.value)){
            document.getElementById('uc').className = 'passed';
        } else {
            document.getElementById('uc').className = 'failed';
            redBorder++;
        };

        if (/[0-9]/.test(passwordInp.value)){
            document.getElementById('n').className = 'passed';
        } else {
            document.getElementById('n').className = 'failed';
            redBorder++;
        };

        if (/[^a-zA-Z0-9\s]/.test(passwordInp.value)){
            document.getElementById('s').className = 'passed';
        } else {
            document.getElementById('s').className = 'failed';
            redBorder++;
        };

        if (!/\s/.test(passwordInp.value)){
            document.getElementById('ws').className = 'passed';
        } else {
            document.getElementById('ws').className = 'failed';
            redBorder++;
        };

        if (passwordInp.value.length >= 8){
            document.getElementById('len').className = 'passed';
        } else {
            document.getElementById('len').className = 'failed';
            redBorder++;
        };

        if (redBorder){
            passwordInp.style.borderColor = 'tomato';
            checkAll.password = 0;
        } else {
            passwordInp.style.borderColor = 'green';
            checkAll.password = 1;
        };

        updateSubmitState();
    });

    rePassword.addEventListener('input', function(){
        if (passwordInp.value == rePassword.value){
            rePassword.style.borderColor = 'green';
            document.querySelector('.not-matching').style.display = 'none';
            checkAll.rePassword = 1;
        } else {
            rePassword.style.borderColor = 'tomato';
            document.querySelector('.not-matching').style.display = 'inline';
            checkAll.rePassword = 0;
        };

        updateSubmitState();
    });

    document.querySelector('form.center-form').addEventListener('submit', function(event){
        if (Object.values(checkAll).includes(0)){
            event.preventDefault();
        };
    });
})()