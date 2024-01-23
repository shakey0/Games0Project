$(document).ready(function(){

    $('.liked-thumbsup, .like-thumbsup').on('click', handleLikeButtonClick);

    function handleLikeButtonClick() {

        const $button = $(this);
        const $form = $button.closest('form');
        const $likedInput = $form.find('input[name="liked"]');
        const formData = $form.serialize();

        $.ajax({
            url: '/like_high_score',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {

                    const scoreId = $button.siblings("input[name='score_id']").val();
                    const $scoreContainer = $(`.score-container[data-score-id='${scoreId}']`);
                    
                    if ($button.hasClass('liked-thumbsup')) {
                        $button.removeClass('liked-thumbsup').addClass('like-thumbsup');
                        $likedInput.val("no");
                    } else {
                        $button.removeClass('like-thumbsup').addClass('liked-thumbsup');
                        $likedInput.val("yes");
                    }
                    const newLikesCount = response.newLikesCount;
                    const $likesCount = $scoreContainer.find('.likes-count');
                    $likesCount.text(`${newLikesCount}`);

                } else {
                    alert(response.error || 'An error occurred while processing your request.');
                }
            },
            error: function() {
                alert('An unexpected error occurred. Please try again later.');
            }
        });
    }

    $('.amend-score-btn').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/amend_score',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    window.location.reload();
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

    $('.delete-score-btn').on('click', function(event) {
        event.preventDefault();
    
        const $button = $(this);
        $button.prop('disabled', true);
        const $form = $button.closest('form');
    
        const formData = $form.serialize();
    
        $.ajax({
            url: '/delete_score',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    window.location.reload();
                }
                $button.prop('disabled', false);
            },
            error: function() {
                $button.prop('disabled', false);
            }
        });
    });

});