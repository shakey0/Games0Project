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

                const scoreId = $button.siblings("input[name='score_id']").val();
                const $scoreContainer = $(`.score-container[data-score-id='${scoreId}']`);

                const newLikesCount = response.newLikesCount;
                const $likesCount = $scoreContainer.find('.likes-count');

                if (response.success) {
                    
                    if ($button.hasClass('liked-thumbsup')) {
                        $button.removeClass('liked-thumbsup').addClass('like-thumbsup');
                        $likedInput.val("no");
                    } else {
                        $button.removeClass('like-thumbsup').addClass('liked-thumbsup');
                        $likedInput.val("yes");
                    }
                    $likesCount.text(`${newLikesCount}`);

                } else {

                    const currentLikesCount = parseInt($likesCount.text(), 10) || 0;

                    if (response.error === 'previously not liked') {
                        const newLikesCount = currentLikesCount - 1;
                        $likesCount.text(newLikesCount);
                        if ($button.hasClass('liked-thumbsup')) {
                            $button.removeClass('liked-thumbsup').addClass('like-thumbsup');
                            $likedInput.val("no");
                        } 
                    } else if (response.error === 'already liked') {
                        const newLikesCount = currentLikesCount + 1;
                        $likesCount.text(newLikesCount);
                        if ($button.hasClass('like-thumbsup')) {
                            $button.removeClass('like-thumbsup').addClass('liked-thumbsup');
                            $likedInput.val("yes");
                        }
                    } else {
                        alert(response.error || 'An error occurred while processing your request.');
                        window.location.reload();
                    }
                }
            },
            error: function() {
                alert('An unexpected error occurred. Please try again later.');
                window.location.reload();
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