document.addEventListener('DOMContentLoaded', (event) => {
    // Start the first countdown as the page loads
    if (document.querySelector('.before-countdown')) {
        startFirstCountdown();
    }
});

function startFirstCountdown() {
    let countdownValue = 5; // Adjust this value as needed
    const countdownElement = document.querySelector('.before-countdown');
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
    let countdownValue = 10; // Value from the backend
    const countdownElement = document.querySelector('.in-countdown');
    const questionInGame = document.querySelector('.question-in-game');
    const questionOver = document.querySelector('.question-over');
    const gameBox = document.querySelector('.game-box');
    const timeUp = document.querySelector('.time-up');

    const intervalId = setInterval(() => {
        countdownElement.innerText = countdownValue;
        countdownValue--;

        if (countdownValue < 0) {
            clearInterval(intervalId);
            if (questionInGame) {
                questionInGame.style.display = 'none';
            }
            if (questionOver) {
                questionOver.style.display = 'block';
                timeUp.style.display = 'block';
                gameBox.style.display = 'none';
            }
        }
    }, 1000);
}
