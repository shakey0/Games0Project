$(document).ready(function(){

    $('.confirm-legal-btn').click(function(event){

        $.ajax({
            url: '/acknowledge_privacy_policy',
            type: 'GET',
            success: function(response) {
                console.log(response.message);
            },
            error: function(xhr, status, error) {
                console.error("Error acknowledging privacy policy", error);
            }
        });
    });

    $('.contact-send-message-btn').on('click', function(event) {
        event.preventDefault();

        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');

        const formData = $form.serialize();

        $.ajax({
            url: '/contact',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    $('.contact-error-message').addClass('hidden');
                    $('.contact-success-message').text(response.message);
                    $('.contact-success-message').removeClass('hidden');
                } else {
                    $('.contact-success-message').addClass('hidden');
                    $('.contact-error-message').text(response.error);
                    $('.contact-error-message').removeClass('hidden');
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $('.contact-error-message').text('An unexpected error occurred. Please try again later.');
                $button.prop('disabled', false);
            }
        });
    });

    $('.login-btn').on('click', function(event) {
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

    $('.reset-password-btn').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/send_reset_password_link',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    $('.forgotten-password-error-message').addClass('hidden');
                    $('.forgotten-password-success-message').text(response.message);
                    $('.forgotten-password-success-message').removeClass('hidden');
                } else {
                    $('.forgotten-password-success-message').addClass('hidden');
                    $('.forgotten-password-error-message').text(response.error);
                    $('.forgotten-password-error-message').removeClass('hidden');
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $('.reset-password-error-message').text('An unexpected error occurred. Please try again later.');
                $button.prop('disabled', false);
            }
        });
    });

    $('.sign-up-btn').on('click', function(event) {
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
                    $('.register-box-item .clear-error').html('');
                    const errorsArray = Object.entries(response.errors).map(([key, value]) => ({ field: key, message: value }));
                    errorsArray.sort((a, b) => a.field.localeCompare(b.field));
                    errorsArray.forEach(error => {
                        const errorField = `register-${error.field}-error-message`;
                        $(`.${errorField}`).text(error.message);
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

    // End of game form with victory message
    $('.go-to-scoreboard').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/game_finish',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    const scoreboardRoute = `/scoreboard?token=${encodeURIComponent(response.token)}`;
                    window.location.href = scoreboardRoute;
                } else {
                    $('.victory-message-error').text(response.error);
                    $('.victory-message-error').removeClass('hidden');
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $('.victory-message-error').text('An unexpected error occurred. Please try again.');
                $button.prop('disabled', false);
            }
        });
    });

});