document.addEventListener('DOMContentLoaded', function() {
    
    var revealLetterBtn = document.querySelector('.reveal-letter-btn');
    var clickCount = 0;
    var totalHints = 0;
    
    if (revealLetterBtn) {
        revealLetterBtn.addEventListener('click', function (event) {
            event.preventDefault();

            var form = this.closest('.reveal-letter-form');

            if (form) {
                var formData = new FormData(form);

                fetch('/reveal_letter', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .then(function(data) {
                    var revealLetterBtn = document.querySelector('.reveal-letter-btn');
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var messageElement = document.getElementById('hint-message');
                        var textElement = document.getElementById('reveal-letter-text');
                        scoreElement.textContent = data.score;
                        totalHints++;
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                            messageElement.style.marginBottom = "10px";
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                        textElement.textContent = data.reveal_card_text;
                        clickCount++;
                        if (clickCount >= 2) {
                            revealLetterBtn.disabled = true;
                        }
                    } else {
                        if (data.reason === 'no_points') {
                            revealLetterBtn.disabled = true;
                        } else {
                            console.error('data.reason not in response object');
                        }
                    }
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var revealLengthBtn = document.querySelector('.reveal-length-btn');

    if (revealLengthBtn) {
        revealLengthBtn.addEventListener('click', function (event) {
            event.preventDefault();

            var form = this.closest('.reveal-length-form');

            if (form) {
                var formData = new FormData(form);

                fetch('/reveal_length', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (response.ok) {
                        return response.json(); // Parse the JSON response
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .then(function(data) {
                    var revealLengthBtn = document.querySelector('.reveal-length-btn');
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var messageElement = document.getElementById('hint-message');
                        var textElement = document.getElementById('reveal-length-text');
                        scoreElement.textContent = data.score;
                        totalHints++;
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                            messageElement.style.marginBottom = "10px";
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                        textElement.textContent = data.length_card_text;
                        revealLengthBtn.disabled = true;
                    } else {
                        if (data.reason === 'no_points') {
                            revealLengthBtn.disabled = true;
                        } else {
                            console.error('data.reason not in response object');
                        }
                    }
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var removeHigherBtn = document.querySelector('.remove-higher-btn');

    if (removeHigherBtn) {
        removeHigherBtn.addEventListener('click', function (event) {
            event.preventDefault();

            var form = this.closest('.remove-higher-form');

            if (form) {
                var formData = new FormData(form);

                fetch('/remove_higher', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .then(function(data) {
                    var removeHigherBtn = document.querySelector('.remove-higher-btn');
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var wrongAnswerElementId = data.answer_to_remove.replace(/\s+/g, '_') + '_box';
                        var wrongAnswerElement = document.getElementById(wrongAnswerElementId);
                        var textElement = document.getElementById('remove-higher-text');
                        scoreElement.textContent = data.score;
                        if (wrongAnswerElement) {
                            wrongAnswerElement.style.display = 'none';
                        }
                        textElement.textContent = data.higher_card_text;
                        removeHigherBtn.disabled = true;
                    } else {
                        if (data.reason === 'no_points') {
                            removeHigherBtn.disabled = true;
                        } else {
                            console.error('data.reason not in response object');
                        }
                    }
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var removeLowerBtn = document.querySelector('.remove-lower-btn');

    if (removeLowerBtn) {
        removeLowerBtn.addEventListener('click', function (event) {
            event.preventDefault();

            var form = this.closest('.remove-lower-form');

            if (form) {
                var formData = new FormData(form);

                fetch('/remove_lower', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Network response was not ok');
                    }
                })
                .then(function(data) {
                    var removeLowerBtn = document.querySelector('.remove-lower-btn');
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var wrongAnswerElementId = data.answer_to_remove.replace(/\s+/g, '_') + '_box';
                        var wrongAnswerElement = document.getElementById(wrongAnswerElementId);
                        var textElement = document.getElementById('remove-lower-text');
                        scoreElement.textContent = data.score;
                        if (wrongAnswerElement) {
                            wrongAnswerElement.style.display = 'none';
                        }
                        textElement.textContent = data.lower_card_text;
                        removeLowerBtn.disabled = true;
                    } else {
                        if (data.reason === 'no_points') {
                            removeLowerBtn.disabled = true;
                        } else {
                            console.error('data.reason not in response object');
                        }
                    }
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

});