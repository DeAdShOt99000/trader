(function(){
    'use strict';

    const location = document.querySelector('.location');

    let current_location = localStorage.getItem('location');

    if (current_location){
        location.querySelector(`.${current_location}`).setAttribute('selected', 'selected')
    };

    location.addEventListener('change', function(){
        localStorage.setItem('location', location.value)
    });
})();