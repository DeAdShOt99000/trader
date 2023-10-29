(function(){
    'use strict';

    // Get the DOM element for the success message with the class 'success-message'
    const successMsg = document.querySelector('.success-message');

    // Check if the success message element exists
    if (successMsg){
        // Set the styles for the success message to make it visible
        successMsg.style.opacity = 1;
        successMsg.style.top = '50px';

        // Set a timeout function to fade out the success message after 2.5 seconds
        setTimeout(() => {
            // Fade out the success message by changing its opacity to 0
            successMsg.style.opacity = 0;
        }, 2500);
    };
})();