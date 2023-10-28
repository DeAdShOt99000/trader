(function(){
    'use strict';
    
    let current_location = localStorage.getItem('location');
    const location = document.querySelector('.location');
    const search = document.querySelector('.search');

    function highlight(text, word){
        let lowerText = text.toLowerCase();
        word = word.toLowerCase();

        if (word.length > 0){
            let start = 0;
            let indecies = [];
            let currentInd;
            let inLst;
            
            while (lowerText.indexOf(word, start) != -1){
                currentInd = lowerText.indexOf(word, start);
                inLst = [];

                start = currentInd + 1;
                while (lowerText.indexOf(word, start) != -1 && (lowerText.indexOf(word, start) - currentInd) < word.length){
                    inLst.push(currentInd);
                    currentInd = lowerText.indexOf(word, start);
                    start = currentInd + 1;
                };

                if (inLst.length > 0){
                    inLst.push(currentInd);
                    indecies.push(inLst);
                } else {
                    indecies.push(currentInd);
                    currentInd = lowerText.indexOf(word, start);
                };
            };
    
            const opening = '<span style="background-color: rgb(47, 47, 47); color: white;">';
            const closing = '</span>';
            
            let newText = text;
            let incrementor = 0;

            let ind1;
            let ind2;
            for (let ind of indecies){
                if (Array.isArray(ind)){
                    ind1 = ind[0] + incrementor;
                    ind2 = word.length + (incrementor + ind[ind.length - 1]);
                } else {
                    ind1 = ind + incrementor;
                    ind2 = word.length + ind1;
                };

                newText = newText.slice(0, ind1) + opening + newText.slice(ind1, ind2) + closing + newText.slice(ind2);
                incrementor += (opening + closing).length;
            };
            return newText;
        };
        return text;
    };

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
        };
    };

    
    if (current_location){
        location.querySelector(`.${current_location}`).setAttribute('selected', 'selected')
        filterLocation();
    };

    search.addEventListener('input', () => {
        for (let elem of document.querySelectorAll('.single-item-cont')){
            if (elem.querySelector('.upper .item-title').innerText.toLowerCase().includes(search.value.toLowerCase()) || elem.querySelector('.upper .item-price').innerText.toLowerCase().includes(search.value.toLowerCase())){
                elem.querySelector('.upper .item-title').innerHTML = highlight(elem.querySelector('.upper .item-title').innerText, search.value);
                elem.querySelector('.upper .item-price').innerHTML = highlight(elem.querySelector('.upper .item-price').innerText, search.value);
                elem.style.display = 'block';
            } else {
                elem.style.display = 'none';
            };
        };
    });

    location.addEventListener('change', () => {
        localStorage.setItem('location', location.value);
        current_location = location.value;

        filterLocation();
    });
})();