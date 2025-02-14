document.addEventListener('DOMContentLoaded', function() {
    // Check if the addPlantForm exists
    const addPlantForm = document.getElementById('addPlantForm');

    if (addPlantForm) {
        addPlantForm.addEventListener('submit', function(event) {
            // Get form elements
            const plantName = document.getElementById('plant-name').value.trim();
            const plantType = document.getElementById('plant-type').value;
            const plantLocation = document.getElementById('plant-location').value.trim();
            const plantDate = document.getElementById('plant-date').value;

            // Simple validation
            if (!plantName || !plantType || !plantLocation || !plantDate) {
                alert('Please fill out all required fields.');
                event.preventDefault(); // Prevent form submission
            }
        });
    }

    // Menu functions
    window.openMenu = function() {
        const menu = document.getElementById("sideMenu");
        menu.style.width = "250px";
        menu.classList.add('open');
    }

    window.closeMenu = function() {
        const menu = document.getElementById("sideMenu");
        menu.style.width = "0";
        menu.classList.remove('open');
    }
});
