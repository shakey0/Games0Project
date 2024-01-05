document.addEventListener('DOMContentLoaded', function() {
    
    var revealButton = document.querySelector('.reveal-letter');
    var clickCount = 0;
    var totalHints = 0;
    
    if (revealButton) {
        revealButton.addEventListener('click', function (event) {
            event.preventDefault();

            clickCount++;
            totalHints++;

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
                    var revealButton = document.querySelector('.reveal-letter');
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var messageElement = document.getElementById('hint-message');
                        var textElement = document.getElementById('reveal-letter-text');
                        scoreElement.textContent = data.score;
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                            messageElement.style.marginBottom = "10px";
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                        textElement.textContent = data.reveal_card_text;
                    } else {
                        var messageElement = document.getElementById('hint-message');
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                        revealButton.disabled = true;
                    }
                    if (clickCount >= 2) {
                        revealButton.disabled = true;
                    }
                })
                .catch(function(error) {
                    // Handle network errors or other exceptions here
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var lengthButton = document.querySelector('.reveal-length');

    if (lengthButton) {
        lengthButton.addEventListener('click', function (event) {
            event.preventDefault();

            totalHints++;

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
                    var lengthButton = document.querySelector('.reveal-length');
                    lengthButton.disabled = true;
                    if (data.success) {
                        var scoreElement = document.getElementById('score');
                        var messageElement = document.getElementById('hint-message');
                        var textElement = document.getElementById('reveal-length-text');
                        scoreElement.textContent = data.score;
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                            messageElement.style.marginBottom = "10px";
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                        textElement.textContent = data.length_card_text;
                    } else {
                        var messageElement = document.getElementById('hint-message');
                        if (totalHints === 1) {
                            messageElement.textContent = data.message;
                        } else {
                            messageElement.innerHTML += '<br>' + data.message;
                        }
                    }
                })
                .catch(function(error) {
                    // Handle network errors or other exceptions here
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var removeHigher = document.querySelector('.remove-higher');

    if (removeHigher) {
        removeHigher.addEventListener('click', function (event) {
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
                    var removeHigher = document.querySelector('.remove-higher');
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
                    }
                    removeHigher.disabled = true;
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

    var removeLower = document.querySelector('.remove-lower');

    if (removeLower) {
        removeLower.addEventListener('click', function (event) {
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
                    var removeLower = document.querySelector('.remove-lower');
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
                    }
                    removeLower.disabled = true;
                })
                .catch(function(error) {
                    console.error('Fetch error:', error);
                });
            }
        });
    }

});