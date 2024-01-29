document.addEventListener('DOMContentLoaded', function() {

    const openBoxButtons = document.querySelectorAll('[data-login-button-target], [data-forgotten-password-button-target], [data-register-button-target], [data-amend-score-box-target]');
    const cancelBoxButtons = document.querySelectorAll('[data-cancel-button]');
    const cancelLoginBox = document.querySelectorAll('[data-cancel-login-box]');
    const overlay = document.getElementById('overlay');

    openBoxButtons.forEach(button => {
        button.addEventListener('click', () => {
            const boxSelector = button.dataset.loginButtonTarget || button.dataset.forgottenPasswordButtonTarget || button.dataset.registerButtonTarget || button.dataset.amendScoreBoxTarget;
            const box = document.querySelector(boxSelector);
            openBox(box);
        });
    });

    cancelBoxButtons.forEach(button => {
        button.addEventListener('click', () => {
            const box = button.closest('.login-box, .forgotten-password-box, .register-box, .amend-score-box');
            closeBox(box);
        });
    });

    cancelLoginBox.forEach(button => {
        button.addEventListener('click', () => {
            const boxSelector = button.dataset.cancelLoginBox;
            const box = document.querySelector(boxSelector);
            closeLoginBox(box);
        });
    });

    function openBox(box) {
        if (box == null) return;
        box.classList.add('active');
        overlay.classList.add('active');
        // toggleScrollLock(true);
    }

    function closeBox(box) {
        if (box == null) return;
        box.classList.remove('active');
        overlay.classList.remove('active');
        // toggleScrollLock(false);
    }

    function closeLoginBox(box) {
        if (box == null) return;
        box.classList.remove('active');
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

    var menuButton = document.querySelector('.menu-btn');
    var optionsMenu = document.getElementById('options-menu');
    var optionsButtons = document.querySelectorAll('.options-btn');
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

    document.getElementById('username').addEventListener('input', function() {
        this.value = this.value.toLowerCase();
    });    

});