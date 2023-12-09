document.addEventListener('DOMContentLoaded', function() {
    var menuButton = document.querySelector('.menu-button');
    var optionsMenu = document.getElementById('options-menu');
    var timeoutId;

    function showMenu() {
        clearTimeout(timeoutId);
        optionsMenu.style.display = 'flex';
    }

    function hideMenu() {
        timeoutId = setTimeout(function() {
            optionsMenu.style.display = 'none';
        }, 250);
    }

    menuButton.addEventListener('mouseenter', showMenu);
    optionsMenu.addEventListener('mouseenter', showMenu);
    menuButton.addEventListener('mouseleave', hideMenu);
    optionsMenu.addEventListener('mouseleave', hideMenu);
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
