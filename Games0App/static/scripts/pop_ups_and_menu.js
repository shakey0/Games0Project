document.addEventListener('DOMContentLoaded', function() {

    var legalInfoBtn = document.getElementById('legal-info-btn');
    if (legalInfoBtn) {
        legalInfoBtn.addEventListener('click', function(event) {
            event.preventDefault();
        });
    }

    const openBoxButtons = document.querySelectorAll('[data-legal-button-target], [data-about-button-target], [data-contact-button-target], [data-login-button-target], [data-forgotten-password-button-target], [data-register-button-target], [data-amend-score-box-target], [data-quit-game-target]');
    const cancelBoxButtons = document.querySelectorAll('[data-cancel-button]');
    const cancelLoginBox = document.querySelectorAll('[data-cancel-login-box]');
    const overlay = document.getElementById('overlay');
    const confirmLegalBox = document.querySelector('.confirm-legal-box');
    const registerBox = document.querySelector('.register-box');

    openBoxButtons.forEach(button => {
        button.addEventListener('click', () => {
            const boxSelector = button.dataset.legalButtonTarget || button.dataset.aboutButtonTarget || button.dataset.contactButtonTarget || button.dataset.loginButtonTarget || button.dataset.forgottenPasswordButtonTarget || button.dataset.registerButtonTarget || button.dataset.amendScoreBoxTarget || button.dataset.quitGameTarget;
            const box = document.querySelector(boxSelector);
            openBox(box);
        });
    });

    cancelBoxButtons.forEach(button => {
        button.addEventListener('click', () => {
            const box = button.closest('.confirm-legal-box, .legal-box, .about-box, .contact-box, .login-box, .forgotten-password-box, .register-box, .amend-score-box, .quit-game-box');
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

    overlay.addEventListener('click', () => {
        const boxes = document.querySelectorAll('.legal-box.active, .about-box.active, .contact-box.active, .quit-game-box.active');
        boxes.forEach(box => {
            closeBox(box);
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
        clearInputFields(box);
        clearTextContent(box);
        box.classList.remove('active');
        if ((!confirmLegalBox || !confirmLegalBox.classList.contains('active')) && (!registerBox || !registerBox.classList.contains('active'))) {
            overlay.classList.remove('active');
        }
        // toggleScrollLock(false);
    }

    function closeLoginBox(box) {
        if (box == null) return;
        clearInputFields(box);
        clearTextContent(box);
        box.classList.remove('active');
    }

    function clearInputFields(box) {
        if (box == null) return;
        const inputFields = box.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        inputFields.forEach(field => {
            field.value = '';
        });
        const checkBoxes = box.querySelectorAll('input[type="checkbox"]');
        checkBoxes.forEach(box => {
            box.checked = false;
        });
    }

    function clearTextContent(box) {
        if (box == null) return;
        const textElements = box.querySelectorAll('.clear-error, .close-clear');
        textElements.forEach(element => {
            element.textContent = '';
        });
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

    const usernameFields = document.querySelectorAll('.username-lower');

    usernameFields.forEach(function(field) {
        field.addEventListener('input', function() {
            this.value = this.value.toLowerCase();
        });
    });

    
    var confirmQuitBtn = document.getElementById('confirm-quit');
    if (confirmQuitBtn) {
        confirmQuitBtn.addEventListener('click', function() {
            var url = document.getElementById('destinationUrl').value;
            window.location.href = url;
        });
    }
    
    function adjustOptionsMenuPosition() {
        const optionsMenu = document.querySelector('.options-menu');
        if (window.innerWidth < document.body.offsetWidth) {
            // Adjust based on the difference between the viewport and the document width
            optionsMenu.style.right = (document.body.offsetWidth - window.innerWidth) + 'px';
        } else {
            optionsMenu.style.right = '0px';
        }
    }
    
    // Adjust on resize and document load
    window.addEventListener('resize', adjustOptionsMenuPosition);
    document.addEventListener('DOMContentLoaded', adjustOptionsMenuPosition);
    
});