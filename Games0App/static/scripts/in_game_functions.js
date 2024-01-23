document.addEventListener('DOMContentLoaded', function() {

    var answerForm = document.querySelector('.in-game-box form');
    if (answerForm) {
        var isSelectionChoice = answerForm.getAttribute('data-selection-choice') === 'true';

        answerForm.addEventListener('submit', function(event) {
            var isValid = false;

            if (isSelectionChoice) {
                var radios = document.querySelectorAll('.answer-radio');
                for (var i = 0; i < radios.length; i++) {
                    if (radios[i].checked) {
                        isValid = true;
                        break;
                    }
                }
            } else {
                var textInput = document.querySelector('.answer-input');
                if (textInput.value.trim() !== '') {
                    isValid = true;
                }
            }
            if (!isValid) {
                event.preventDefault();
            }
        });
    }

});

document.addEventListener('DOMContentLoaded', (event) => {
    if (document.querySelector('.before-countdown')) {
        startFirstCountdown();
    }
});

function startFirstCountdown() {
    const countdownElement = document.querySelector('.before-countdown');
    let countdownValue = parseInt(countdownElement.textContent, 10);
    const questionTitleOpening = document.querySelector('.func-pre');
    const questionInGame = document.querySelector('.func-in');
    const inGameCountdown = document.querySelector('.in-countdown');
    const gameBox = document.querySelector('.in-game-box');

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
                inGameCountdown.style.display = 'block';
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
    const questionInGame = document.querySelector('.func-in');
    const gameBox = document.querySelector('.in-game-box');
    const helperBox = document.querySelector('.helper-box');
    const hiddenTimerInput = document.getElementById('countdown-timer');
    const gameForm = document.querySelector('.in-game-box form');

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