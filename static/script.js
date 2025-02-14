document.addEventListener('DOMContentLoaded', function() {
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
