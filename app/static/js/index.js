(function(){
    'use strict';

    let current_location = localStorage.getItem('location');

    function filterLocation(){
        if (current_location){
            for (let elem of document.querySelectorAll('.single-item-cont')){
                elem.style.display = 'none';
            };
            
            for (let elem of document.querySelectorAll(`.location-${current_location}`)){
                elem.style.display = 'block';
            };
        } else {
            for (let elem of document.querySelectorAll('.single-item-cont')){
                elem.style.display = 'block';
            };
        }
    };

    if (current_location){
        filterLocation();
    };

    const location = document.querySelector('.location');

    location.addEventListener('change', () => {
        localStorage.setItem('location', location.value);
        current_location = location.value;

        filterLocation();
    });
})();