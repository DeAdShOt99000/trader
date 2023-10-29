(function(){
    'use strict';

    // Get the saved location from localStorage
    let current_location = localStorage.getItem('location');

    // Get DOM elements for location dropdown and search input
    const location = document.querySelector('.location');
    const search = document.querySelector('.search');

    // Function to highlight search results in the given text
    function highlight(text, word){
        // Convert text and search word to lowercase for case-insensitive search
        let lowerText = text.toLowerCase();
        word = word.toLowerCase();

        if (word.length > 0){
            // Variables to store indices of search word occurrences
            let start = 0;
            let indecies = [];

            // Loop through the text to find all occurrences of the search word
            while (lowerText.indexOf(word, start) != -1){
                let currentInd = lowerText.indexOf(word, start);
                let inLst = [];

                // Store indices of overlapping occurrences
                start = currentInd + 1;
                while (lowerText.indexOf(word, start) != -1 && (lowerText.indexOf(word, start) - currentInd) < word.length){
                    inLst.push(currentInd);
                    currentInd = lowerText.indexOf(word, start);
                    start = currentInd + 1;
                };

                // Store non-overlapping occurrences or overlapping occurrences as arrays
                if (inLst.length > 0){
                    inLst.push(currentInd);
                    indecies.push(inLst);
                } else {
                    indecies.push(currentInd);
                    currentInd = lowerText.indexOf(word, start);
                };
            }

            // HTML tags for highlighting
            const opening = '<span style="background-color: rgb(47, 47, 47); color: white;">';
            const closing = '</span>';

            let newText = text;
            let incrementor = 0;

            // Apply highlighting to the occurrences in the text
            for (let ind of indecies){
                let ind1, ind2;
                if (Array.isArray(ind)){
                    ind1 = ind[0] + incrementor;
                    ind2 = word.length + (incrementor + ind[ind.length - 1]);
                } else {
                    ind1 = ind + incrementor;
                    ind2 = word.length + ind1;
                };

                newText = newText.slice(0, ind1) + opening + newText.slice(ind1, ind2) + closing + newText.slice(ind2);
                incrementor += (opening + closing).length;
            }
            return newText;
        }
        return text;
    }

    // Function to filter items based on location
    function filterLocation(){
        if (current_location){
            // Hide all items
            for (let elem of document.querySelectorAll('.single-item-cont')){
                elem.style.display = 'none';
            }
            
            // Show items in the selected location
            for (let elem of document.querySelectorAll(`.location-${current_location}`)){
                elem.style.display = 'block';
            }
        } else {
            // Show all items if no location is selected
            for (let elem of document.querySelectorAll('.single-item-cont')){
                elem.style.display = 'block';
            }
        }
    }

    // Initialize the location dropdown if a location is saved
    if (current_location){
        location.querySelector(`.${current_location}`).setAttribute('selected', 'selected');
        filterLocation();
    }

    // Event listener for search input
    search.addEventListener('input', () => {
        // Loop through items and filter based on search input
        for (let elem of document.querySelectorAll('.single-item-cont')){
            // Check if item title or price contains the search input
            if (elem.querySelector('.upper .item-title').innerText.toLowerCase().includes(search.value.toLowerCase()) || 
                elem.querySelector('.upper .item-price').innerText.toLowerCase().includes(search.value.toLowerCase())){
                // Highlight matching text and display the item
                elem.querySelector('.upper .item-title').innerHTML = highlight(elem.querySelector('.upper .item-title').innerText, search.value);
                elem.querySelector('.upper .item-price').innerHTML = highlight(elem.querySelector('.upper .item-price').innerText, search.value);
                elem.style.display = 'block';
            } else {
                // Hide the item if it doesn't match the search input
                elem.style.display = 'none';
            }
        }
    });

    // Event listener for location dropdown change
    location.addEventListener('change', () => {
        // Save selected location to localStorage and update the displayed items
        localStorage.setItem('location', location.value);
        current_location = location.value;
        filterLocation();
    });
})();