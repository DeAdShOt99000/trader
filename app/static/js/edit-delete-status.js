(function(){
    'use strict';

    document.querySelectorAll('.edit-delete-status').forEach(each => {
        each.querySelector('.edit-btn').addEventListener('click', event => {
            window.location.href = `/my-items/edit/${event.target.id.substring(5)}${window.next ? window.next: ''}`;
        });
        
        each.querySelector('.delete-btn').addEventListener('click', event => {
            if (confirm("Are you sure you want to delete this item?")){
                window.location.href = `/my-items/delete/${event.target.id.substring(7)}`;
            };
        });
        
        each.querySelector('.status-btn').addEventListener('click', event => {
            window.location.href = `/my-items/status-toggle/${event.target.id.substring(7)}${window.next ? window.next: ''}`;
        })
    });
})();