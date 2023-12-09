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

    menuButton.addEventListener('click', toggleMenu);
    document.addEventListener('click', handleClickOutside);
    optionsButtons.forEach(function(button) {
        button.addEventListener('click', handleOptionButtonClick);
    });

});

document.addEventListener('DOMContentLoaded', (event) => {
    // Start the first countdown as the page loads
    if (document.querySelector('.before-countdown')) {
        startFirstCountdown();
    }
});

function startFirstCountdown() {
    const countdownElement = document.querySelector('.before-countdown');
    let countdownValue = parseInt(countdownElement.textContent, 10);
    const questionTitleOpening = document.querySelector('.question-title-opening');
    const questionInGame = document.querySelector('.question-in-game');
    const gameBox = document.querySelector('.game-box');

    const intervalId = setInterval(() => {
        countdownElement.innerText = countdownValue;
        countdownValue--;

        if (countdownValue < 0) {
            clearInterval(intervalId);

            // Change the divs visibility here
            if (questionTitleOpening) {
                questionTitleOpening.style.display = 'none';
            }
            if (questionInGame) {
                questionInGame.style.display = 'block';
                gameBox.style.display = 'block';
            }

            // Start the second countdown 1 second after the first one finishes
            setTimeout(startSecondCountdown, 0);
        }
    }, 1000);
}

function startSecondCountdown() {
    const countdownElement = document.querySelector('.in-countdown');
    let countdownValue = parseInt(countdownElement.textContent, 10);
    const questionInGame = document.querySelector('.question-in-game');
    const gameBox = document.querySelector('.game-box');
    const helperBox = document.querySelector('.helper-box');
    const hiddenTimerInput = document.getElementById('countdown-timer');
    const gameForm = document.querySelector('.game-box form');

    const intervalId = setInterval(() => {
        countdownElement.innerText = countdownValue;
        hiddenTimerInput.value = countdownValue;
        countdownValue--;

        if (countdownValue < 0) {
            clearInterval(intervalId);
            if (questionInGame) {
                questionInGame.style.display = 'none';
                gameBox.style.display = 'none';
                helperBox.style.display = 'block';
            }
            gameForm.submit();
        }
    }, 1000);
}

$(document).ready(function(){

    $('.log-in-button').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/login',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    localStorage.setItem('loginSuccessMessage', response.message);
                    window.location.reload();
                } else {
                    $('.login-error-message').text(response.error);
                    $('.login-error-message').removeClass('hidden');
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $('.login-error-message').text('An unexpected error occurred. Please try again later.');
                $button.prop('disabled', false);
            }
        });
    });

    $('.sign-up-button').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/register',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    localStorage.setItem('loginSuccessMessage', response.message);
                    window.location.reload();
                } else {
                    const errorsArray = Object.entries(response.errors).map(([key, value]) => ({ field: key, message: value }));
                    errorsArray.sort((a, b) => a.field.localeCompare(b.field));
                    errorsArray.forEach(error => {
                        const errorField = `register-${error.field}-error-message`;
                        $(`#${errorField}`).text(error.message);
                    });
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $('.register-error-message').text('An unexpected error occurred. Please try again later.');
                $button.prop('disabled', false);
            }
        });
    });

});