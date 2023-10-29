(function(){
    'use strict';

    const successMsg = document.querySelector('.success-message');

    if (successMsg){
        successMsg.style.opacity = 1;
        successMsg.style.top = '50px';

        setTimeout(() => {
            successMsg.style.opacity = 0;
        }, 2500);
    };
})();