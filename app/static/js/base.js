(function(){
    'use strict';

    const successMsg = document.querySelector('.success-message');

    if (successMsg){
        setTimeout(() => {
            successMsg.style.opacity = 0
        }, 2000)
    };
})();