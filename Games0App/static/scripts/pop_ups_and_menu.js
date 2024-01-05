document.addEventListener('DOMContentLoaded', function() {

    const openBoxButtonsOver = document.querySelectorAll('[data-login-button-target], [data-register-button-target]');
    const cancelBoxButtonsOver = document.querySelectorAll('[data-cancel-button-over]');
    const overlay = document.getElementById('overlay');

    openBoxButtonsOver.forEach(button => {
        button.addEventListener('click', () => {
            const boxSelector = button.dataset.loginButtonTarget || button.dataset.registerButtonTarget;
            const box = document.querySelector(boxSelector);
            openBoxOver(box);
        });
    });

    cancelBoxButtonsOver.forEach(button => {
        button.addEventListener('click', () => {
            const box = button.closest('.login-box, .register-box');
            closeBoxOver(box);
        });
    });

    function openBoxOver(box) {
        if (box == null) return;
        box.classList.add('active');
        overlay.classList.add('active');
        // toggleScrollLock(true);
    }

    function closeBoxOver(box) {
        if (box == null) return;
        box.classList.remove('active');
        overlay.classList.remove('active');
        // toggleScrollLock(false);
    }

    // function toggleScrollLock(isLocked) {
    //     const body = document.body;
    
    //     if (isLocked) {
    //         const scrollY = window.scrollY;
    //         body.style.position = 'fixed';
    //         body.style.top = `-${scrollY}px`;
    //         body.style.width = '100%';
    //     } else {
    //         const scrollY = body.style.top;
    //         body.style.position = '';
    //         body.style.top = '';
    //         window.scrollTo(0, parseInt(scrollY || '0') * -1);
    //     }
    // }

    var menuButton = document.querySelector('.menu-button');
    var optionsMenu = document.getElementById('options-menu');
    var optionsButtons = document.querySelectorAll('.options-button');
    var isMenuVisible = false;

    function toggleMenu() {
        isMenuVisible = !isMenuVisible;
        optionsMenu.style.display = isMenuVisible ? 'flex' : 'none';
        menuButton.style.color = isMenuVisible ? 'rgb(251, 223, 158)' : 'rgb(232, 213, 203)';
    }
    function handleClickOutside(event) {
        if (isMenuVisible && !optionsMenu.contains(event.target) && !menuButton.contains(event.target)) {
            toggleMenu();
        }
    }
    function handleOptionButtonClick() {
        if (isMenuVisible) {
            toggleMenu();
        }
    }

    if (menuButton) {
        menuButton.addEventListener('click', toggleMenu);
    }
    document.addEventListener('click', handleClickOutside);
    optionsButtons.forEach(function(button) {
        button.addEventListener('click', handleOptionButtonClick);
    });

});